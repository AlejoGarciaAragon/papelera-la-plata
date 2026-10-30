from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import SimpleTestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import Cliente, Inventario, Venta
from core.services.afip_service import (
	ARCAServiceError,
	_validate_invoice_type,
	_voucher_data,
	tipo_comprobante_sugerido,
)


class DetailRows(list):
	def select_related(self, *args, **kwargs):
		return self

	def all(self):
		return self


class ARCAServiceTests(SimpleTestCase):
	@override_settings(AFIP_CONDICION_FISCAL='responsable_inscripto')
	def test_factura_a_splits_gross_amount_into_net_and_iva(self):
		cliente = SimpleNamespace(
			condicion_iva='responsable_inscripto',
			tipo_documento='cuit',
			numero_documento='20123456789',
		)
		venta = SimpleNamespace(
			tipo_comprobante='Factura A',
			cliente=cliente,
			total=Decimal('121.00'),
			detalles=DetailRows([SimpleNamespace(subtotal=Decimal('121.00'), iva_porcentaje=21)]),
		)

		voucher = _voucher_data(venta, 1)

		self.assertEqual(voucher['ImpNeto'], Decimal('100.00'))
		self.assertEqual(voucher['ImpIVA'], Decimal('21.00'))
		self.assertEqual(voucher['Iva']['AlicIva'], [
			{'Id': 5, 'BaseImp': Decimal('100.00'), 'Importe': Decimal('21.00')},
		])

	@override_settings(AFIP_CONDICION_FISCAL='monotributista')
	def test_monotributista_issuer_suggests_factura_c(self):
		self.assertEqual(tipo_comprobante_sugerido(), 'Factura C')

	@override_settings(AFIP_CONDICION_FISCAL='responsable_inscripto')
	def test_factura_a_requires_a_customer_cuit(self):
		cliente = SimpleNamespace(
			condicion_iva='responsable_inscripto',
			tipo_documento='dni',
			numero_documento='12345678',
		)
		venta = SimpleNamespace(tipo_comprobante='Factura A', cliente=cliente)

		with self.assertRaisesRegex(ARCAServiceError, 'CUIT'):
			_validate_invoice_type(venta)


class ApiIntegrationTests(APITestCase):
	def setUp(self):
		user_model = get_user_model()
		self.user = user_model.objects.create_user(username='owner-test', password='Secure-test-123')
		self.user.groups.add(Group.objects.create(name='Dueno'))
		self.client.force_authenticate(self.user)

	def test_vite_origin_is_allowed_by_cors(self):
		response = self.client.options('/api/categorias/', HTTP_ORIGIN='http://localhost:5173')
		self.assertEqual(response.headers.get('Access-Control-Allow-Origin'), 'http://localhost:5173')

	def test_catalog_contract_maps_ui_fields(self):
		category_response = self.client.post('/api/categorias/', {
			'nombre': 'Papelería', 'descripcion': 'Artículos', 'color': '#7fdcdc',
		}, format='json')
		self.assertEqual(category_response.status_code, 201)
		category_id = category_response.data['id']

		product_response = self.client.post('/api/productos/', {
			'codigo': 'TEST-001', 'nombre': 'Cuaderno', 'categoriaId': category_id,
			'precioCosto': '1000.00', 'ganancia': '40', 'iva': 21,
			'stock': 8, 'stockMinimo': 3,
		}, format='json')
		self.assertEqual(product_response.status_code, 201)
		self.assertEqual(product_response.data['codigo'], 'TEST-001')
		self.assertEqual(product_response.data['stock'], 8)
		self.assertEqual(product_response.data['stockMinimo'], 3)
		self.assertEqual(product_response.data['categoriaId'], category_id)
		delete_category = self.client.delete(f'/api/categorias/{category_id}/')
		self.assertEqual(delete_category.status_code, 400)

		client_response = self.client.post('/api/clientes/', {
			'razonSocial': 'Cliente de prueba', 'documento': '20123456789',
			'tipoDocumento': 'cuit',
			'condicionIVA': 'Responsable Inscripto', 'direccion': '', 'telefono': '', 'email': '',
		}, format='json')
		self.assertEqual(client_response.status_code, 201)
		self.assertEqual(client_response.data['razonSocial'], 'Cliente de prueba')
		self.assertEqual(client_response.data['condicionIVA'], 'Responsable Inscripto')
		self.assertEqual(client_response.data['tipoDocumento'], 'cuit')

	@override_settings(AFIP_CONDICION_FISCAL='responsable_inscripto')
	def test_invoice_type_suggestion_uses_customer_tax_condition(self):
		cliente = Cliente.objects.create(
			nombre_o_razon_social='Responsable Inscripto',
			tipo_documento='cuit',
			numero_documento='20123456789',
			condicion_iva='responsable_inscripto',
		)
		response = self.client.get('/api/ventas/tipo-comprobante-sugerido/')
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['tipo'], 'Factura B')

		customer_response = self.client.get(
			'/api/ventas/tipo-comprobante-sugerido/',
			{'clienteId': cliente.id},
		)
		self.assertEqual(customer_response.status_code, 200)
		self.assertEqual(customer_response.data['tipo'], 'Factura A')

	def test_login_and_sale_persist_and_decrement_inventory(self):
		self.client.force_authenticate(user=None)
		login_response = self.client.post('/api/token/', {
			'username': 'owner-test', 'password': 'Secure-test-123',
		}, format='json')
		self.assertEqual(login_response.status_code, 200)
		self.assertEqual(login_response.data['role'], 'Dueno')
		self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

		category = self.client.post('/api/categorias/', {'nombre': 'Oficina', 'color': '#7fdcdc'}, format='json').data
		product = self.client.post('/api/productos/', {
			'codigo': 'TEST-002', 'nombre': 'Resma', 'categoriaId': category['id'],
			'precioCosto': '1000.00', 'ganancia': '40', 'iva': 21,
			'stock': 5, 'stockMinimo': 2,
		}, format='json').data
		caja_response = self.client.post('/api/cajas/abrir/', {'montoInicial': 10000}, format='json')
		self.assertEqual(caja_response.status_code, 201)
		self.assertEqual(caja_response.data['fechaOperativa'], timezone.localdate().isoformat())

		sale_response = self.client.post('/api/ventas/', {
			'clienteId': None, 'tipo': 'Factura X', 'medioPago': 'Efectivo',
			'items': [{'productoId': product['id'], 'cantidad': 2}],
		}, format='json')
		self.assertEqual(sale_response.status_code, 201)
		self.assertEqual(sale_response.data['tipo'], 'Factura X')
		self.assertEqual(sale_response.data['estado'], 'pendiente_cobro')
		self.assertEqual(sale_response.data['medioPago'], 'Pendiente de cobro')
		self.assertEqual(sale_response.data['vendedorNombre'], 'owner-test')
		self.assertEqual(sale_response.data['estadoARCA'], 'Pendiente')
		self.assertEqual(sale_response.data['cae'], '')
		self.assertTrue(sale_response.data['numero'].startswith('PENDIENTE-'))
		self.assertEqual(sale_response.data['cajaId'], caja_response.data['id'])
		self.assertEqual(sale_response.data['total'], '3400.00')
		self.assertEqual(Inventario.objects.get(producto_id=product['id']).stock_fisico, 3)

		with patch('core.api.views.generar_factura', return_value={
			'cae': '12345678901234',
			'vencimiento_cae': date(2026, 11, 10),
			'nro_comprobante': '0001-00000001',
		}) as emitir:
			billing_response = self.client.post(
				f"/api/ventas/{sale_response.data['id']}/cobrar_y_facturar/",
				{
					'tipo': 'Factura B',
					'medioPago': 'Efectivo',
					'pagaCon': '3500.00',
				},
				format='json',
			)
		self.assertEqual(billing_response.status_code, 200)
		self.assertEqual(billing_response.data['estado'], 'completada')
		self.assertEqual(billing_response.data['nroComprobante'], '0001-00000001')
		self.assertEqual(billing_response.data['numero'], '0001-00000001')
		self.assertEqual(billing_response.data['cae'], '12345678901234')
		self.assertEqual(billing_response.data['caeVto'], '2026-11-10')
		emitir.assert_called_once()

		movement_response = self.client.post(f"/api/cajas/{caja_response.data['id']}/movimientos/", {
			'tipo': 'Ingreso', 'concepto': 'Cambio', 'monto': '500.00',
		}, format='json')
		self.assertEqual(movement_response.status_code, 201)
		close_response = self.client.post(f"/api/cajas/{caja_response.data['id']}/cerrar/", {
			'montoCierre': 10400,
		}, format='json')
		self.assertEqual(close_response.status_code, 200)
		self.assertIsNotNone(close_response.data['cerradaEn'])
		second_open_response = self.client.post('/api/cajas/abrir/', {'montoInicial': 10000}, format='json')
		self.assertEqual(second_open_response.status_code, 400)

	def test_sale_requires_open_cash_register(self):
		category = self.client.post('/api/categorias/', {'nombre': 'Ventas', 'color': '#7fdcdc'}, format='json').data
		product = self.client.post('/api/productos/', {
			'codigo': 'TEST-003', 'nombre': 'Lapicera', 'categoriaId': category['id'],
			'precioCosto': '100.00', 'ganancia': '20', 'iva': 21, 'stock': 2,
		}, format='json').data
		response = self.client.post('/api/ventas/', {
			'tipo': 'Factura B', 'medioPago': 'Efectivo',
			'items': [{'productoId': product['id'], 'cantidad': 1}],
		}, format='json')
		self.assertEqual(response.status_code, 400)
		self.assertEqual(Inventario.objects.get(producto_id=product['id']).stock_fisico, 2)

	def test_arca_rejection_keeps_sale_pending_and_does_not_record_payment(self):
		category = self.client.post('/api/categorias/', {'nombre': 'ARCA', 'color': '#7fdcdc'}, format='json').data
		product = self.client.post('/api/productos/', {
			'codigo': 'ARCA-001', 'nombre': 'Papel', 'categoriaId': category['id'],
			'precioCosto': '100.00', 'ganancia': '20', 'iva': 21, 'stock': 3,
		}, format='json').data
		self.client.post('/api/cajas/abrir/', {'montoInicial': 0}, format='json')
		sale = self.client.post('/api/ventas/', {
			'items': [{'productoId': product['id'], 'cantidad': 1}],
		}, format='json')
		self.assertEqual(sale.status_code, 201)

		with patch(
			'core.api.views.generar_factura',
			side_effect=ARCAServiceError('ARCA rechazó el comprobante.'),
		):
			response = self.client.post(
				f"/api/ventas/{sale.data['id']}/cobrar_y_facturar/",
				{'tipo': 'Factura B', 'medioPago': 'Efectivo', 'pagaCon': sale.data['total']},
				format='json',
			)

		self.assertEqual(response.status_code, 400)
		venta = Venta.objects.get(pk=sale.data['id'])
		self.assertEqual(venta.estado, Venta.ESTADO_PENDIENTE_COBRO)
		self.assertEqual(venta.metodo_pago, Venta.METODO_PAGO_PENDIENTE)
		self.assertEqual(venta.cae, '')
		self.assertEqual(Inventario.objects.get(producto_id=product['id']).stock_fisico, 2)

	def test_employee_can_submit_pending_sale_but_only_owner_can_collect_or_close(self):
		category = self.client.post('/api/categorias/', {'nombre': 'Empleado', 'color': '#7fdcdc'}, format='json').data
		product = self.client.post('/api/productos/', {
			'codigo': 'EMP-001', 'nombre': 'Carpeta', 'categoriaId': category['id'],
			'precioCosto': '100.00', 'ganancia': '20', 'iva': 21, 'stock': 4,
		}, format='json').data
		employee_group = Group.objects.create(name='Empleado')
		employee = get_user_model().objects.create_user(username='employee-test', password='Secure-test-123')
		employee.groups.add(employee_group)
		self.client.force_authenticate(employee)

		productos_response = self.client.get('/api/productos/')
		self.assertEqual(productos_response.status_code, 200)
		self.assertNotIn('precioCosto', productos_response.data[0])
		self.assertNotIn('ganancia', productos_response.data[0])
		self.assertEqual(productos_response.data[0]['stockMinimo'], 5)
		self.assertEqual(self.client.patch(f"/api/productos/{product['id']}/", {'oculto': True}, format='json').status_code, 403)
		self.assertEqual(self.client.post('/api/productos/', {}, format='json').status_code, 403)
		categorias_response = self.client.get('/api/categorias/')
		self.assertEqual(categorias_response.status_code, 200)
		self.assertEqual(categorias_response.data[0]['color'], '#7fdcdc')
		self.assertEqual(self.client.post('/api/categorias/', {}, format='json').status_code, 403)
		self.assertEqual(self.client.get('/api/clientes/').status_code, 403)
		self.assertEqual(self.client.get('/api/ventas/').status_code, 403)

		caja = self.client.post('/api/cajas/abrir/', {'montoInicial': 0}, format='json')
		self.assertEqual(caja.status_code, 201)
		self.assertEqual(self.client.post(f"/api/cajas/{caja.data['id']}/cerrar/", {'montoCierre': 0}, format='json').status_code, 403)
		self.assertEqual(self.client.post(f"/api/cajas/{caja.data['id']}/movimientos/", {
			'tipo': 'Ingreso', 'concepto': 'Cambio', 'monto': 10,
		}, format='json').status_code, 403)

		venta = self.client.post('/api/ventas/', {
			'tipo': 'Factura B', 'items': [{'productoId': product['id'], 'cantidad': 1}],
		}, format='json')
		self.assertEqual(venta.status_code, 201)
		self.assertEqual(venta.data['estado'], 'pendiente_cobro')
		self.assertEqual(venta.data['medioPago'], 'Pendiente de cobro')
		self.assertEqual(Inventario.objects.get(producto_id=product['id']).stock_fisico, 3)
		self.assertEqual(self.client.post(f"/api/ventas/{venta.data['id']}/cobrar/", {
			'medioPago': 'Efectivo', 'pagaCon': venta.data['total'],
		}, format='json').status_code, 403)
		self.assertEqual(self.client.post(f"/api/ventas/{venta.data['id']}/cobrar_y_facturar/", {
			'tipo': 'Factura B', 'medioPago': 'Efectivo',
		}, format='json').status_code, 403)

		self.client.force_authenticate(self.user)
		cliente = Cliente.objects.create(
			nombre_o_razon_social='Cliente elegido al cobrar',
			tipo_documento='dni',
			numero_documento='40123456',
			condicion_iva='consumidor_final',
		)
		self.assertEqual(self.client.post(f"/api/cajas/{caja.data['id']}/cerrar/", {'montoCierre': 0}, format='json').status_code, 400)
		url_cobro = f"/api/ventas/{venta.data['id']}/cobrar/"
		self.assertEqual(self.client.post(url_cobro, {'medioPago': 'Efectivo'}, format='json').status_code, 400)
		with patch('core.api.views.generar_factura', return_value={
			'cae': '12345678901234',
			'vencimiento_cae': date(2026, 11, 10),
			'nro_comprobante': '0001-00000002',
		}):
			cobrada = self.client.post(url_cobro, {
				'tipo': 'Factura B', 'medioPago': 'Efectivo',
				'pagaCon': venta.data['total'], 'clienteId': cliente.id,
			}, format='json')
		self.assertEqual(cobrada.status_code, 200)
		self.assertEqual(cobrada.data['estado'], 'completada')
		self.assertEqual(cobrada.data['medioPago'], 'Efectivo')
		self.assertEqual(cobrada.data['clienteId'], cliente.id)
		self.assertEqual(cobrada.data['clienteNombre'], 'Cliente elegido al cobrar')
		self.assertEqual(self.client.post(f"/api/cajas/{caja.data['id']}/cerrar/", {'montoCierre': 0}, format='json').status_code, 200)
