from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoriaViewSet, ClienteViewSet, ProductoViewSet, VentaViewSet

router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'clientes', ClienteViewSet, basename='cliente')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'ventas', VentaViewSet, basename='venta')

urlpatterns = [
    path('', include(router.urls)),
]