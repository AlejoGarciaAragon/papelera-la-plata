# Configuración de ARCA

Copiá `.env.example` como `.env` y completá el CUIT del emisor, las rutas locales al
certificado `.crt` y a la clave privada `.key`, el punto de venta electrónico y el
régimen fiscal (`responsable_inscripto` o `monotributista`). No agregues `.env` ni
los certificados al repositorio.

`AFIP_PRODUCTION=False` usa homologación. `AFIP_PRODUCTION` selecciona los endpoints
WSAA y WSFE; para producción configurá también las rutas a los certificados emitidos
para ese entorno mediante `AFIP_CERT_PATH` y `AFIP_KEY_PATH`. El certificado y la
clave se leen y firman localmente en el backend.

El POST de `/api/ventas/` crea la preventa pendiente y descuenta el stock. El dueño
confirma el medio de pago, el cliente y el comprobante en
`POST /api/ventas/{id}/cobrar_y_facturar/`. Si ARCA rechaza o no responde, la
transacción de cobro se revierte y la venta queda pendiente para reintentar.
