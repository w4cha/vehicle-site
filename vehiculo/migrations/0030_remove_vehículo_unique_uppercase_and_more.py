# Generated by Django 5.1.1 on 2024-10-09 19:32

import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0029_remove_vehículo_unique_uppercase_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='vehículo',
            name='unique uppercase',
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='carrocería',
            field=models.CharField(max_length=100, unique=True, verbose_name='serial de carrocería'),
        ),
        migrations.AlterField(
            model_name='vehículo',
            name='motor',
            field=models.CharField(max_length=50, unique=True, verbose_name='serial de motor'),
        ),
        migrations.AddConstraint(
            model_name='vehículo',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Upper('carrocería'), name='unique uppercase'),
        ),
    ]
