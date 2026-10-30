import base64
import logging
import threading
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs7
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone as django_timezone
from zeep import Client
from zeep.exceptions import Error as ZeepError
from zeep.helpers import serialize_object
from zeep.transports import Transport


logger = logging.getLogger(__name__)
_TOKEN_LOCK = threading.Lock()
_CENT = Decimal('0.01')
_VAT_IDS = {0: 3, 10: 4, 21: 5, 27: 6, 5: 8, 2: 9}
_INVOICE_CODES = {'Factura A': 1, 'Factura B': 6, 'Factura C': 11}
_RECEIVER_TAX_CODES = {
    'responsable_inscripto': 1,
    'exento': 4,
    'consumidor_final': 5,
    'monotributo': 6,
}
_DOCUMENT_CODES = {'cuit': 80, 'cuil': 86, 'dni': 96, 'pasaporte': 94, 'otro': 99}
_HOMOLOGATION_WSAA = 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms'
_PRODUCTION_WSAA = 'https://wsaa.afip.gov.ar/ws/services/LoginCms'
_HOMOLOGATION_WSFE = 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx'
_PRODUCTION_WSFE = 'https://servicios1.afip.gov.ar/wsfev1/service.asmx'


class ARCAServiceError(Exception):
    pass


def tipo_comprobante_sugerido(cliente=None):
    regimen = settings.AFIP_CONDICION_FISCAL
    if regimen == 'monotributista':
        return 'Factura C'
    if regimen == 'responsable_inscripto':
        if cliente and cliente.condicion_iva == 'responsable_inscripto':
            return 'Factura A'
        return 'Factura B'
    raise ARCAServiceError(
        'Configurá AFIP_CONDICION_FISCAL como responsable_inscripto o monotributista.'
    )


def _validate_invoice_type(venta):
    expected_type = tipo_comprobante_sugerido(venta.cliente)
    if venta.tipo_comprobante != expected_type:
        raise ARCAServiceError(
            f'El comprobante correspondiente a este cliente y al régimen del comercio es {expected_type}.'
        )
    if expected_type == 'Factura A':
        if not venta.cliente or venta.cliente.tipo_documento != 'cuit':
            raise ARCAServiceError('Para emitir Factura A, el cliente debe tener un CUIT configurado.')
        cuit = ''.join(filter(str.isdigit, venta.cliente.numero_documento))
        if len(cuit) != 11:
            raise ARCAServiceError('Para emitir Factura A, el cliente debe tener un CUIT de 11 dígitos.')


def _afip_configuration():
    cuit = ''.join(filter(str.isdigit, settings.AFIP_CUIT))
    if len(cuit) != 11:
        raise ARCAServiceError('Configurá AFIP_CUIT con un CUIT válido de 11 dígitos.')
    if not settings.AFIP_CERT_PATH or not settings.AFIP_KEY_PATH:
        raise ARCAServiceError('Configurá AFIP_CERT_PATH y AFIP_KEY_PATH en el archivo .env.')
    try:
        point_of_sale = int(settings.AFIP_PUNTO_VENTA)
    except (TypeError, ValueError) as error:
        raise ARCAServiceError('Configurá AFIP_PUNTO_VENTA con un número habilitado en ARCA.') from error
    if point_of_sale < 1:
        raise ARCAServiceError('AFIP_PUNTO_VENTA debe ser mayor que cero.')
    if settings.AFIP_CONDICION_FISCAL not in {'responsable_inscripto', 'monotributista'}:
        raise ARCAServiceError(
            'Configurá AFIP_CONDICION_FISCAL como responsable_inscripto o monotributista.'
        )
    return int(cuit), point_of_sale


def _load_certificate_and_key():
    cert_path = Path(settings.AFIP_CERT_PATH)
    key_path = Path(settings.AFIP_KEY_PATH)
    if not cert_path.is_absolute():
        cert_path = settings.BASE_DIR / cert_path
    if not key_path.is_absolute():
        key_path = settings.BASE_DIR / key_path
    try:
        certificate = x509.load_pem_x509_certificate(cert_path.read_bytes())
        private_key = serialization.load_pem_private_key(key_path.read_bytes(), password=None)
    except (OSError, ValueError, TypeError) as error:
        raise ARCAServiceError(
            'No se pudieron leer el certificado o la clave privada de ARCA. Verificá sus rutas y formato PEM.'
        ) from error
    return certificate, private_key


def _format_utc(value):
    return value.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')


def _build_login_ticket(certificate, private_key):
    now = datetime.now(timezone.utc)
    root = ET.Element('loginTicketRequest', version='1.0')
    header = ET.SubElement(root, 'header')
    ET.SubElement(header, 'uniqueId').text = str(int(now.timestamp()))
    ET.SubElement(header, 'generationTime').text = _format_utc(now - timedelta(minutes=10))
    ET.SubElement(header, 'expirationTime').text = _format_utc(now + timedelta(minutes=10))
    ET.SubElement(root, 'service').text = 'wsfe'

    cms = (
        pkcs7.PKCS7SignatureBuilder()
        .set_data(ET.tostring(root, encoding='utf-8'))
        .add_signer(certificate, private_key, hashes.SHA256())
        .sign(serialization.Encoding.DER, [pkcs7.PKCS7Options.Binary])
    )
    return base64.b64encode(cms).decode('ascii')


def _soap_client(wsdl_url):
    session = requests.Session()
    return Client(
        f'{wsdl_url}?WSDL',
        transport=Transport(session=session, timeout=30, operation_timeout=30),
    )


def _get_authentication(cuit):
    environment = 'prod' if settings.AFIP_PRODUCTION else 'homo'
    cache_key = f'arca_wsfe_auth_{environment}_{cuit}'
    cached_auth = cache.get(cache_key)
    if cached_auth:
        return cached_auth

    with _TOKEN_LOCK:
        cached_auth = cache.get(cache_key)
        if cached_auth:
            return cached_auth

        certificate, private_key = _load_certificate_and_key()
        login_wsdl = _PRODUCTION_WSAA if settings.AFIP_PRODUCTION else _HOMOLOGATION_WSAA
        cms = _build_login_ticket(certificate, private_key)
        login_response = _soap_client(login_wsdl).service.loginCms(in0=cms)
        root = ET.fromstring(login_response)
        token = root.findtext('.//token')
        sign = root.findtext('.//sign')
        expiration_text = root.findtext('.//expirationTime')
        if not token or not sign or not expiration_text:
            raise ARCAServiceError('ARCA no devolvió un token de autorización válido para WSFE.')

        expiration = datetime.fromisoformat(expiration_text.replace('Z', '+00:00'))
        if expiration.tzinfo is None:
            expiration = expiration.replace(tzinfo=timezone.utc)
        expires_in = max(30, int((expiration - datetime.now(timezone.utc)).total_seconds()) - 60)
        auth = {'Token': token, 'Sign': sign, 'Cuit': cuit}
        cache.set(cache_key, auth, timeout=expires_in)
        return auth


def _receiver_document(cliente):
    if cliente is None:
        return 99, 0
    document_type = _DOCUMENT_CODES.get(cliente.tipo_documento)
    if document_type is None:
        raise ARCAServiceError('El tipo de documento del cliente no es válido para ARCA.')
    document_number = ''.join(filter(str.isdigit, cliente.numero_documento))
    if cliente.tipo_documento == 'otro' and not document_number:
        return document_type, 0
    if not document_number:
        raise ARCAServiceError('El cliente seleccionado no tiene un documento fiscal configurado.')
    return document_type, int(document_number)


def _vat_breakdown(venta):
    breakdown = defaultdict(lambda: {'base': Decimal('0.00'), 'vat': Decimal('0.00')})
    for detail in venta.detalles.select_related('producto').all():
        rate = detail.iva_porcentaje
        if rate not in _VAT_IDS:
            raise ARCAServiceError(f'La alícuota de IVA {rate}% no está soportada para facturación ARCA.')
        gross = Decimal(detail.subtotal).quantize(_CENT, rounding=ROUND_HALF_UP)
        base = (gross / (Decimal('1') + Decimal(rate) / Decimal('100'))).quantize(
            _CENT, rounding=ROUND_HALF_UP
        )
        breakdown[rate]['base'] += base
        breakdown[rate]['vat'] += gross - base
    return breakdown


def _voucher_data(venta, voucher_number):
    invoice_type = venta.tipo_comprobante
    document_type, document_number = _receiver_document(venta.cliente)
    receiver_tax_code = _RECEIVER_TAX_CODES.get(
        venta.cliente.condicion_iva if venta.cliente else 'consumidor_final'
    )
    if receiver_tax_code is None:
        raise ARCAServiceError('La condición frente al IVA del cliente no es válida para ARCA.')

    total = Decimal(venta.total).quantize(_CENT, rounding=ROUND_HALF_UP)
    vat = _vat_breakdown(venta)
    if invoice_type == 'Factura C':
        net_amount = total
        vat_amount = Decimal('0.00')
        vat_items = []
    else:
        net_amount = sum((values['base'] for values in vat.values()), Decimal('0.00'))
        vat_amount = sum((values['vat'] for values in vat.values()), Decimal('0.00'))
        vat_items = [
            {
                'Id': _VAT_IDS[rate],
                'BaseImp': values['base'],
                'Importe': values['vat'],
            }
            for rate, values in sorted(vat.items())
        ]

    voucher = {
        'Concepto': 1,
        'DocTipo': document_type,
        'DocNro': document_number,
        'CbteDesde': voucher_number,
        'CbteHasta': voucher_number,
        'CbteFch': django_timezone.localdate().strftime('%Y%m%d'),
        'ImpTotal': total,
        'ImpTotConc': Decimal('0.00'),
        'ImpNeto': net_amount,
        'ImpOpEx': Decimal('0.00'),
        'ImpIVA': vat_amount,
        'ImpTrib': Decimal('0.00'),
        'MonId': 'PES',
        'MonCotiz': Decimal('1.00'),
        'CondicionIVAReceptorId': receiver_tax_code,
    }
    if vat_items:
        voucher['Iva'] = {'AlicIva': vat_items}
    return voucher


def _response_dict(response):
    result = serialize_object(response, target_cls=dict)
    return result if isinstance(result, dict) else {}


def _as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _arca_error_messages(result):
    errors = result.get('Errors') or {}
    error_entries = _as_list(errors.get('Err') if isinstance(errors, dict) else None)
    messages = [
        f"{entry.get('Code', '')}: {entry.get('Msg', 'Error informado por ARCA')}".strip(': ')
        for entry in error_entries
        if isinstance(entry, dict)
    ]
    return '; '.join(messages)


def generar_factura(venta):
    _validate_invoice_type(venta)
    cuit, point_of_sale = _afip_configuration()
    voucher_type = _INVOICE_CODES[venta.tipo_comprobante]

    try:
        auth = _get_authentication(cuit)
        wsfe_wsdl = _PRODUCTION_WSFE if settings.AFIP_PRODUCTION else _HOMOLOGATION_WSFE
        wsfe = _soap_client(wsfe_wsdl)
        last_number = wsfe.service.FECompUltimoAutorizado(
            Auth=auth,
            PtoVta=point_of_sale,
            CbteTipo=voucher_type,
        )
        last_number_data = _response_dict(last_number)
        if last_number_data.get('CbteNro') is None:
            message = _arca_error_messages(last_number_data)
            raise ARCAServiceError(message or 'ARCA no devolvió el último número autorizado.')
        voucher_number = int(last_number_data['CbteNro']) + 1
        voucher = _voucher_data(venta, voucher_number)
        response = wsfe.service.FECAESolicitar(
            Auth=auth,
            FeCAEReq={
                'FeCabReq': {
                    'CantReg': 1,
                    'PtoVta': point_of_sale,
                    'CbteTipo': voucher_type,
                },
                'FeDetReq': {'FECAEDetRequest': [voucher]},
            },
        )
    except ARCAServiceError:
        raise
    except (
        ZeepError, requests.RequestException, OSError, ValueError, TypeError, KeyError, ET.ParseError
    ) as error:
        logger.error('Falló la comunicación con ARCA durante la emisión (%s).', type(error).__name__)
        raise ARCAServiceError(
            'No se pudo confirmar la respuesta de ARCA. La venta sigue pendiente y sin cobrar; '
            'verificá el comprobante en ARCA antes de reintentar.'
        ) from error

    result = _response_dict(response)
    if 'FeCAESolicitarResult' in result:
        result = _response_dict(result['FeCAESolicitarResult'])
    error_message = _arca_error_messages(result)
    if error_message:
        raise ARCAServiceError(f'ARCA rechazó el comprobante: {error_message}')

    details = result.get('FeDetResp') or {}
    detail_entries = _as_list(details.get('FECAEDetResponse') if isinstance(details, dict) else None)
    if not detail_entries:
        raise ARCAServiceError('ARCA no devolvió el resultado del comprobante.')
    authorized = _response_dict(detail_entries[0])
    cae = authorized.get('CAE')
    cae_expiration = authorized.get('CAEFchVto')
    authorized_number = authorized.get('CbteDesde')
    if authorized.get('Resultado') != 'A' or not cae or not cae_expiration or not authorized_number:
        observations = authorized.get('Observaciones') or {}
        observation_entries = _as_list(
            observations.get('Obs') if isinstance(observations, dict) else None
        )
        messages = [
            str(entry.get('Msg', '')) for entry in observation_entries if isinstance(entry, dict)
        ]
        suffix = f" {'; '.join(messages)}" if messages else ''
        raise ARCAServiceError(f'ARCA no autorizó el comprobante.{suffix}')

    return {
        'cae': str(cae),
        'vencimiento_cae': datetime.strptime(str(cae_expiration), '%Y%m%d').date(),
        'nro_comprobante': f'{point_of_sale:04d}-{int(authorized_number):08d}',
    }
