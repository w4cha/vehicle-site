# Generated by Django 5.1.1 on 2024-10-03 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vehiculo', '0017_alter_vehículogalería_imágenes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vehículogalería',
            name='descripción',
            field=models.CharField(error_messages='solo hasta 30 caracteres', max_length=50, verbose_name='descripción imagen'),
        ),
    ]
