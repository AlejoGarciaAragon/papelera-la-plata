from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from rest_framework.test import APITestCase

from core.models import Inventario, Producto


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
			'condicionIVA': 'Responsable Inscripto', 'direccion': '', 'telefono': '', 'email': '',
		}, format='json')
		self.assertEqual(client_response.status_code, 201)
		self.assertEqual(client_response.data['razonSocial'], 'Cliente de prueba')
		self.assertEqual(client_response.data['condicionIVA'], 'Responsable Inscripto')

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
		self.assertEqual(sale_response.data['estadoARCA'], 'No aplica')
		self.assertEqual(sale_response.data['cae'], '')
		self.assertEqual(sale_response.data['cajaId'], caja_response.data['id'])
		self.assertEqual(sale_response.data['total'], '3400.00')
		self.assertEqual(Inventario.objects.get(producto_id=product['id']).stock_fisico, 3)

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
