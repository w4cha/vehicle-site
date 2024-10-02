# Generated by Django 5.1.1 on 2024-09-26 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0006_alter_vehículo_precio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehículo',
            name='marca',
            field=models.CharField(choices=[(0, 'Chevrolet'), (1, 'Fiat'), (2, 'Ford'), (3, 'Toyota')], default='Toyota', max_length=20, verbose_name='marca vehículo'),
        ),
    ]
