from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0006_venta_detalleventa'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cliente',
            old_name='cuit_dni',
            new_name='numero_documento',
        ),
        migrations.RenameField(
            model_name='cliente',
            old_name='razon_social',
            new_name='nombre_o_razon_social',
        ),
        migrations.AddField(
            model_name='cliente',
            name='activo',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='telefono',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='cliente',
            name='tipo_documento',
            field=models.CharField(
                choices=[
                    ('dni', 'DNI'),
                    ('cuit', 'CUIT'),
                    ('cuil', 'CUIL'),
                    ('pasaporte', 'Pasaporte'),
                    ('otro', 'Otro'),
                ],
                default='dni',
                max_length=15,
            ),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='condicion_iva',
            field=models.CharField(
                choices=[
                    ('consumidor_final', 'Consumidor Final'),
                    ('responsable_inscripto', 'Responsable Inscripto'),
                    ('monotributo', 'Monotributo'),
                    ('exento', 'Exento'),
                ],
                default='consumidor_final',
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='nombre_o_razon_social',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='cliente',
            name='numero_documento',
            field=models.CharField(db_index=True, max_length=50, unique=True),
        ),
    ]
