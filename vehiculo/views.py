from pathlib import Path
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_views, authenticate, login
from django.db.models import Case, When, Value, Q
from .forms import VehicleForm, LoginForm, CreateUserForm, FileUploadForm
from django.contrib import messages
from .models import Vehículo, VehículoGalería
from django.forms.models import model_to_dict
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required

# Create your views here.

# PermissionRequiredMixin es para evitar en este caso que
# se trate de acceder a la ruta escribiendo la url manual
class VehicleList(PermissionRequiredMixin, generic.ListView):

    # template de la ruta
    template_name = 'vehiculo/list.html'

    # nombre para referirse a valores pasados al template
    context_object_name = 'list_of_vehicles'

    # permisos que PermissionRequiredMixin va revisar
    # que tenga el usuario
    permission_required = 'vehiculo.visualizar_catalogo'

    # donde redirige si un usuario no registrado y autorizado quiere entrar
    # si un usuario registrado pero no autorizado intenta entrar se le da un error
    # 403 y no se le redirige al login
    login_url = "vehiculo:login"

    redirect_field_name = "redirect_to"

    # sql de consulta al modelo que se retorna al template
    # Case es igual que a los condicionales de postsgresql
    # en Case cada condición se escribe usando When
    # cosas como precio__gte significa del modelo Vehículo
    # en el atributo precio usa el método __gte__ (greater or equal than)
    # then es el valor que se va a pasar cuando se cumpla la condicional
    # condición= es el nombre del Case para referirse a el en el template
    def get_queryset(self):
        if (search := self.request.GET.get("resultados", False)):
            options = {val.lower(): key for key, val in Vehículo.MARKS.items()}
            both = search.split(";", 1)
            if len(both) == 2:
                v_marca, v_modelo = both
                partial = Q(marca=options.get(v_marca.lower(), "-")) & Q(modelo__icontains=v_modelo) 

            else:
                v_marca = v_modelo = search
                partial = Q(marca=options.get(v_marca.lower(), "-")) | Q(modelo__icontains=v_modelo) 
            query = Vehículo.objects.filter(partial).order_by('precio').annotate(condición=Case(
                    When(precio__gte=0, precio__lt=10_000, then=Value("Bajo")),
                    When(precio__gte=10_000, precio__lt=30_000, then=Value("Medio")),
                    default=Value("Alto")),)
        else:
            query = Vehículo.objects.all().order_by('precio').annotate(condición=Case(
                    When(precio__gte=0, precio__lt=10_000, then=Value("Bajo")),
                    When(precio__gte=10_000, precio__lt=30_000, then=Value("Medio")),
                    default=Value("Alto")),)
        return query
    
    # para pasar datos extras al template en este caso tomamos
    # los nombres de los campos o atributos del modelo para usarlos como encabezado de tabla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # django creates an aditional field to the model related to this one
        context["header"] = [field.verbose_name for field in Vehículo._meta.get_fields() 
                             if field.name not in("id", "creación", "modificación", "vehículogalería")]
        context["header"].extend(["Condición de precio",])
        return context


class IndexView(generic.TemplateView):

    template_name = 'vehiculo/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_authorized"] = self.request.user.has_perm("vehiculo.add_vehículo") 
        return context


class VehicleCreateView(PermissionRequiredMixin, CreateView):

    # defino la clase de forma a usar desde forms.py

    model = Vehículo

    form_class = VehicleForm

    template_name = "vehiculo/add.html"

    permission_required = 'vehiculo.add_vehículo'

    login_url = "vehiculo:login"

    redirect_field_name = "redirect_to"

    # mensaje de entrada creada con éxito, de forma
    # habitual si un usuario con ambos poderes add_vehículo 
    # y visualizar_catalogo crea una entrada se redirige a la
    # lista de todas las entradas lo que en si es su mensaje 
    # de éxito pero si no tiene el permiso visualizar_catalogo
    # se le tiene que enviar de vuelta al formulario y para
    # que tenga una idea de que el formulario fue exitoso
    # se requiere este mensaje y la clase SuccessMessageMixin

    # ruta a la que se redirige si el formulario es valido
    # en mi caso después de crear cada entrada redirijo a la
    # lista de entradas
    def get_success_url(self) -> str:
        new_entry = model_to_dict(instance=get_object_or_404(Vehículo, pk=self.object.id), exclude=["id", "creación", "modificación",])
        new_entry = ", ".join([f"{key}: {value}" for key, value in new_entry.items()])
        messages.success(self.request, f"Entrada creada exitosamente<br> {new_entry}", "éxito")
        return reverse("vehiculo:add-vehicle")

    

class LogUserIn(auth_views.LoginView):

    template_name = "registration/login.html"

    next_page = "vehiculo:index"

    # defino la clase de forma a usar desde forms.py
    authentication_form = LoginForm


class LogUserOut(auth_views.LogoutView):

    # donde se redirige después de salir de la cuenta
    next_page = "vehiculo:index"


class NewUser(SuccessMessageMixin, CreateView):

    form_class = CreateUserForm

    template_name = 'registration/signup.html'

    success_message = "usuario creado exitosamente"

    # necessary to log user in after creation
    def form_valid(self, form):
        valid = super().form_valid(form)
        permission_user = Permission.objects.get(codename="visualizar_catalogo")
        # you can actually do this
        self.object.user_permissions.add(permission_user)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        if new_user is not None:
            login(self.request, new_user)
        return valid

    def get_success_url(self):
        return reverse("vehiculo:index")

@login_required(login_url=reverse_lazy("vehiculo:login"))   
def update_vehiculo(request, pk):
    
    # so you can write the url to update manually
    if request.method == "GET" and request.headers.get("X-Csrftoken", False):
        edit_vehiculo = get_object_or_404(Vehículo, pk=pk)
        form = VehicleForm(instance=edit_vehiculo)
        context = {"form": form,}
        return render(request, "vehiculo/edit.html", context)
    elif request.method == "POST":
        edit_vehiculo = get_object_or_404(Vehículo, pk=pk)
        # this way you can update using a functional way
        # print(request.POST) is the data obtained from the form
        # the instance is the one to update
        form = VehicleForm(request.POST, instance=edit_vehiculo)
        if form.is_valid():
            form.save()
            messages.success(request, "entrada actualizada exitosamente", "éxito")
            # how to manage redirect ajax pass response with url and redirect in js
            return HttpResponse(content=reverse("vehiculo:list"), status = 302)
        else:
            context = {"form": form}
            return render(request, "vehiculo/edit.html", context, status=200)
    else:
        raise PermissionDenied
    
@login_required(login_url=reverse_lazy("vehiculo:login"))
def delete_vehiculo(request, pk):
    if request.method == "POST":
        delete_vehiculo = get_object_or_404(Vehículo, pk=pk)
        old_entry = model_to_dict(instance=delete_vehiculo, exclude=["id", "creación", "modificación",])
        old_entry["marca"] = delete_vehiculo.get_marca_display()
        old_entry["categoría"] = delete_vehiculo.get_categoría_display()
        old_entry = ", ".join([f"{key}: {value}" for key, value in old_entry.items()])
        related_gallery = VehículoGalería.objects.all().filter(vehículo=pk)
        for entry in related_gallery:
            Path(entry.imágenes.path).unlink()
        delete_vehiculo.delete()
        messages.success(request, f"Entrada borrada exitosamente<br> {old_entry}", "éxito")
        return HttpResponse(content=reverse("vehiculo:list"), status = 302)
    elif request.method == "GET" and request.headers.get("X-Csrftoken", False):
        context = {"entry": pk}
        return render(request, "vehiculo/delete.html", context)
    else:
        raise PermissionDenied
    
@login_required(login_url=reverse_lazy("vehiculo:login"))
def gallery_view(request, pk):
    if "vehiculo.view_vehículogalería" not in request.user.get_all_permissions():
        raise PermissionDenied
    # global context
    try:
        current_element = Vehículo.objects.get(pk=pk)
    except Vehículo.DoesNotExist:
        return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:list"), status = 302)
    vehicle_gallery = VehículoGalería.objects.all().filter(vehículo=pk)
    verbose_mark = current_element.get_marca_display()
    current = model_to_dict(instance=current_element, exclude=["id", "creación", "modificación", "categoría",])
    current["marca"] = verbose_mark
    if request.method == "GET":
        # if the user tries to manually enter a gallery without elements
        form = FileUploadForm()
        context = {"gallery": vehicle_gallery, "form": form, "entry": current}
        return render(request, "vehiculo/gallery.html", context, status=200)
    elif request.method == "POST":
        if "vehiculo.add_vehículogalería" not in request.user.get_all_permissions():
            raise PermissionDenied
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            total_entries_images = VehículoGalería.objects.all().filter(vehículo=pk).count()
            if total_entries_images < 5:
                messages.success(request, "imagen subida exitosamente", "éxito")
                vehicle_img = form.save(commit=False)
                vehicle_img.vehículo = get_object_or_404(Vehículo, pk=pk)
                vehicle_img.save()
                return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:gallery", kwargs={"pk": pk}), status = 302)

            else:
                messages.error(request, f"se supero el número máximo de imágenes por entrada de {total_entries_images}", "error")
                return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:gallery", kwargs={"pk": pk}), status = 302)

            # how to manage redirect ajax pass response with url and redirect in js
        context = {"gallery": vehicle_gallery, "form": form, "entry": current}
        return render(request, "vehiculo/gallery.html", context, status=200)
    else:
        raise PermissionDenied
    
@login_required(login_url=reverse_lazy("vehiculo:login"))
def delete_img(request, pk):
   if request.method == "POST":
        if "vehiculo.delete_vehículogalería" not in request.user.get_all_permissions():
            raise PermissionDenied
        # se puede acceder a los campos directamente del objeto relacionado
        delete_img = get_object_or_404(VehículoGalería, pk=pk)
        
        Path(delete_img.imágenes.path).unlink()
        delete_img.delete()
        return HttpResponse(content=reverse(f"vehiculo:gallery", kwargs={"pk": delete_img.vehículo.pk}), status = 302)
   else:
       raise PermissionDenied

    