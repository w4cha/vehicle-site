from django import forms
from .models import Vehículo
from django.utils.translation import gettext_lazy as alt
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# para que aparezcan errores si el usuario o contraseña es incorrecto
class LoginForm(AuthenticationForm):
    error_messages = {
        "invalid_login": "Nombre de usuario <br> o contraseña inválidos",
        "inactive": "Acceso denegado",
    }

class VehicleForm(forms.ModelForm):

    # para sobre escribir el comportamiento de ModelForm
    # y que el valor default en html <select> sea el que queramos
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["marca"].initial = "3"
        self.fields["categoría"].initial = "P"
    
    class Meta:

        model = Vehículo

        # que campos del modelo no se deben mostrar
        exclude = ["creación", "modificación",]

        # mensaje de error si el dato es incorrecto
        error_messages = {
            "precio": {
                "max_value": alt("el valor tiene que ser menor que 500.000"),
            },
        }

class CreateUserForm(UserCreationForm):
    
  
  email = forms.EmailField(required=True)

  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for item in self.fields:
            self.fields[item].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].help_text = """
    Consideraciones:<br>
    1. Su contraseña no puede ser muy similar a su otra información personal<br>
    2. Su contraseña debe contener al menos 8 caracteres<br>
    3. Su contraseña no puede ser una contraseña de uso común<br>
    4. Su contraseña no puede ser completamente numérica

"""

  class Meta:
      model = User
      fields = ['username', 'email', 'password1', 'password2',]
    