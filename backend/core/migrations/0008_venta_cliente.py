from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_cliente_datos_fiscales'),
    ]

    operations = [
        migrations.AddField(
            model_name='venta',
            name='cliente',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ventas',
                to='core.cliente',
            ),
        ),
    ]
