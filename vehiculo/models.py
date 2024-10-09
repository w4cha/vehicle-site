
# Create your models here.
import string
from django.db import models
from django.core.validators import MaxValueValidator
from django.core.validators import FileExtensionValidator

class Vehículo(models.Model):

    PARTICULAR = "P"

    TRANSPORTE = "T"

    CARGA = "C"

    ACCEPTED_CATEGORIES = {
        PARTICULAR: "Particular",
        TRANSPORTE: "Transporte",
        CARGA: "Carga",
    }

    marca = models.CharField(verbose_name="marca vehículo", max_length=40, null=False)

    modelo = models.CharField(verbose_name="modelo vehículo", max_length=100, null=False, blank=False)

    carrocería = models.CharField(verbose_name="serial de carrocería", max_length=100, null=False, unique=True)

    motor = models.CharField(verbose_name="serial de motor", max_length=50, null=False, unique=True)

    categoría = models.CharField(verbose_name="categoría vehículo", max_length=20, null=False, choices=ACCEPTED_CATEGORIES, 
                                 default=ACCEPTED_CATEGORIES[PARTICULAR])
    
    precio = models.PositiveIntegerField(verbose_name="precio vehículo", null=False, 
                                             validators=[MaxValueValidator(500_000, message="valor debe ser menor o igual a %(limit_value)s")],
                                             help_text="precios entre 0 a 500.000")
    
    creación = models.DateTimeField(verbose_name="fecha creación", auto_now_add=True, editable=False)

    modificación = models.DateTimeField(verbose_name="fecha modificación", auto_now=True)

    class Meta:
        # if verbose name is not specified the name of the model is use
        # if verbose_plural_name is not specified a s is put at the name of the name
        permissions = [
            (
                "visualizar_catalogo",
                "Puede ver la lista de vehículos disponibles",
            ),
            (   "descargar_tabla",
                "Puede descargar la lista de vehículos"),
        ]
    
    def save(self, *args, **kwargs):
        self.marca = string.capwords(self.marca)
        self.modelo = string.capwords(self.modelo)
        self.carrocería = self.carrocería.upper()
        self.motor = self.motor.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (f"Marca: {self.marca}, Modelo: {self.modelo}, Carrocería: {self.carrocería}, "
                f"Motor: {self.motor}")


class VehículoGalería(models.Model):

    vehículo = models.ForeignKey(Vehículo, on_delete=models.CASCADE)

    descripción = models.CharField(verbose_name="descripción imagen", max_length=150, null=False, error_messages="solo hasta 150 caracteres")

    imágenes = models.ImageField(verbose_name="imágenes vehículo", upload_to="vehículo", 
                                help_text="archivo jpg, png o gif", null=False,
                                validators=[FileExtensionValidator(allowed_extensions=["png", "jpg", "jpeg", "gif",], 
                                                                   message="formatos soportados: png, jpg, jpeg o gif")])
    
    def __str__(self) -> str:
        return f"Vehículo relacionada: {self.vehículo}, Imagen: {self.imágenes.name}"

