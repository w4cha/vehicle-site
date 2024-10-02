from django.contrib import admin
from .models import Vehículo

# Register your models here.

# para cambiar como se visualizan los modelos en el sitio de administrador
class VehículoAdmin(admin.ModelAdmin):

    list_display = ["marca", "modelo", "carrocería",
                    "motor", "categoría", "precio",
                    "estado_precio", "creación", "modificación",]

    search_fields = ["marca", "modelo",]

    # barra lateral con filtros
    list_filter = ["categoría",]

    readonly_fields = ["creación", "modificación",]

    ordering = ["marca",]

    # to create custom columns with classification you register a method
    # in list display that is going to return the labels base on the data
    # grouping to access model fields you use the obj arg
    def estado_precio(self, obj):
        return "Alto" if obj.precio >= 30_000 else ("Medio" if 10_000 <= obj.precio < 30_000 else "Bajo")



    
admin.site.register(Vehículo, VehículoAdmin)
admin.site.site_title = 'Administración'
admin.site.site_header = 'Sistema de administración de vehículos'
admin.site.index_title = 'Acciones administrativas disponibles'

