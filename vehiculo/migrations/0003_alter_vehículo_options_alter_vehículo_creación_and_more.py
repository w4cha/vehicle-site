# Generated by Django 5.1.1 on 2024-09-25 19:08

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0002_alter_vehículo_creación_alter_vehículo_modificación'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vehículo',
            options={'permissions': [('visualizar_catalogo', 'Puede ver la lista de vehículos disponibles')]},
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='creación',
            field=models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='fecha creación'),
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='precio',
            field=models.PositiveIntegerField(help_text='values between 0 and 500_000_000', validators=[django.core.validators.MaxValueValidator(500000000, message='value must be less than %(limit_value)s')], verbose_name='precio vehículo'),
        ),
    ]
