# Generated by Django 5.1.1 on 2024-09-26 13:33

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0005_alter_vehículo_precio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehículo',
            name='precio',
            field=models.PositiveIntegerField(help_text='values between 0 and 500_000', validators=[django.core.validators.MaxValueValidator(500000, message='value must be less than %(limit_value)s')], verbose_name='precio vehículo'),
        ),
    ]
