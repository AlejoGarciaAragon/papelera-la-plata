from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import migrations, models


def convertir_precio_lista_a_porcentaje(apps, schema_editor):
    Producto = apps.get_model('core', 'Producto')
    for producto in Producto.objects.all():
        if producto.precio_actual and producto.precio_lista:
            producto.porcentaje_ganancia = (
                (producto.precio_lista / producto.precio_actual - Decimal('1')) * Decimal('100')
            ).quantize(Decimal('0.01'))
            producto.save(update_fields=['porcentaje_ganancia'])


class Migration(migrations.Migration):
    dependencies = [('core', '0004_cliente_direccion')]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='porcentaje_ganancia',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, validators=[MinValueValidator(0)]),
        ),
        migrations.RunPython(convertir_precio_lista_a_porcentaje, migrations.RunPython.noop),
    ]