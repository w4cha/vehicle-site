# Generated by Django 5.1.1 on 2024-10-10 13:58

import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0035_remove_vehículo_unique_carrocería_upper_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='vehículo',
            name='unique carrocería upper',
        ),
        migrations.RemoveConstraint(
            model_name='vehículo',
            name='unique motor upper',
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='carrocería',
            field=models.CharField(max_length=100, verbose_name='serial de carrocería'),
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='motor',
            field=models.CharField(max_length=50, verbose_name='serial de motor'),
        ),
        migrations.AddConstraint(
            model_name='vehículo',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper('carrocería'), name='unique carrocería upper', violation_error_message='La serial de carrocería que intenta ingresar ya existe'),
        ),
        migrations.AddConstraint(
            model_name='vehículo',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper('motor'), name='unique motor upper', violation_error_message='La serial de motor que intenta ingresar ya existe'),
        ),
    ]
