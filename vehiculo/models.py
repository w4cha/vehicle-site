
# Create your models here.
from django.db import models
from django.core.validators import MaxValueValidator
from pathlib import Path

class Vehículo(models.Model):

    PARTICULAR = "P"

    TRANSPORTE = "T"

    CARGA = "C"

    ACCEPTED_CATEGORIES = {
        PARTICULAR: "Particular",
        TRANSPORTE: "Transporte",
        CARGA: "Carga",
    }

    # si son int hay conflicto con el Charfield ya que espera str
    MARKS = {"1": "Chevrolet", 
             "2": "Fiat", 
             "3": "Ford", 
             "4": "Toyota",}
        
    

    marca = models.CharField(verbose_name="marca vehículo", max_length=20, null=False, choices=MARKS, default=MARKS["3"])

    modelo = models.CharField(verbose_name="modelo vehículo", max_length=100, null=False)

    carrocería = models.CharField(verbose_name="serial de carrocería", max_length=100, null=False, unique=True)

    motor = models.CharField(verbose_name="serial de motor", max_length=50, null=False, unique=True)

    categoría = models.CharField(verbose_name="categoría vehículo", max_length=20, null=False, choices=ACCEPTED_CATEGORIES, 
                                 default=ACCEPTED_CATEGORIES[PARTICULAR])
    
    precio = models.PositiveIntegerField(verbose_name="precio vehículo", null=False, 
                                             validators=[MaxValueValidator(500_000, message="valor debe ser menor o igual a %(limit_value)s")],
                                             help_text="precios entre 0 a 500000")
    
    creación = models.DateTimeField(verbose_name="fecha creación", auto_now_add=True, editable=False)

    modificación = models.DateTimeField(verbose_name="fecha modificación", auto_now=True)

    class Meta:
        # if verbose name is not specified the name of the model is use
        # if verbose_plural_name is not specified a s is put at the name of the name
        permissions = [
            (
                "visualizar_catalogo",
                "Puede ver la lista de vehículos disponibles",
            )
        ]

    # right way of overriding methods
    def save(self, *arg, **kwargs):
       new_directory = Path(fr"{Path(__file__).parent}\static\vehiculo\img\{self.marca}\{self.carrocería}")
       if not new_directory.is_dir():
           new_directory.mkdir()
       super().save(*arg, **kwargs)

    def __str__(self) -> str:
        return (f"Marca: {self.marca}, Modelo: {self.modelo}, Carrocería: {self.carrocería}, "
                f"Motor: {self.motor}, Categoría: {self.categoría}, Precio: {self.precio}, "
                f"Creación entrada: {self.creación}: Ultima modificación: {self.modificación}")
