from django.contrib import admin
from .models import Vehículo, VehículoGalería

# Register your models here.

# para editar la tabla hija desde el padre
class ChoiceInline(admin.TabularInline):
    model = VehículoGalería
    extra = 0

# para cambiar como se visualizan los modelos en el sitio de administrador
class VehículoAdmin(admin.ModelAdmin):

    list_display = ["marca", "modelo", "carrocería",
                    "motor", "categoría", "precio",
                    "estado_precio", "creación", "modificación",]

    search_fields = ["marca", "modelo",]

    # barra lateral con filtros
    list_filter = ["categoría", "marca", "modelo",]

    readonly_fields = ["creación", "modificación",]

    ordering = ["marca",]

    inlines = [ChoiceInline,]


    # to create custom columns with classification you register a method
    # in list display that is going to return the labels base on the data
    # grouping to access model fields you use the obj arg
    def estado_precio(self, obj):
        return "Alto" if obj.precio >= 30_000 else ("Medio" if 10_000 <= obj.precio < 30_000 else "Bajo")


class ImágenesAdmin(admin.ModelAdmin):
    
    list_display = ["vehículo", "descripción", "imágenes",]

    readonly_fields = ["imágenes",]

    # asi se referencia a la tabla padre desde el hijo para filtros
    list_filter = ["vehículo__marca",]


admin.site.register(Vehículo, VehículoAdmin)
admin.site.register(VehículoGalería, ImágenesAdmin)
admin.site.site_title = 'Administración'
admin.site.site_header = 'Sistema de administración de vehículos'
admin.site.index_title = 'Acciones administrativas disponibles'

