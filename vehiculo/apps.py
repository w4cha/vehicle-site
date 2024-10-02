from django.apps import AppConfig


class VehiculoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vehiculo'
    # nombre app en sitio administrativo
    verbose_name = 'app de vehículos'
