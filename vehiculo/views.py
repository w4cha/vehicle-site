from pathlib import Path
import csv
from django.http.response import HttpResponse, HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import generic
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth import views as auth_views, authenticate, login
from .forms import VehicleForm, LoginForm, CreateUserForm, FileUploadForm
from .services import fetch_query
from django.contrib import messages
from .models import Vehículo, VehículoGalería
from django.forms.models import model_to_dict
from django.contrib.auth.models import Group
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
        return fetch_query(self.request.GET.get("resultados", None))
    
    # para pasar datos extras al template en este caso tomamos
    # los nombres de los campos o atributos del modelo para usarlos como encabezado de tabla
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # django creates an aditional field to the model related to this one
        context["header"] = [field.verbose_name for field in Vehículo._meta.get_fields() 
                             if field.name not in("id", "creación", "modificación", "vehículogalería")]
        context["header"].extend(["Condición de precio",])
        if (download_context := self.request.GET.get("resultados", False)):
            context["download"] = download_context
        else:
            context["download"] = "all"
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

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:index"), status = 302)
    


class LogUserOut(auth_views.LogoutView):

    # donde se redirige después de salir de la cuenta
    next_page = "vehiculo:index"

    # message on log out
    def get_success_url(self):
        messages.success(self.request, "sesión cerrada", "éxito")
        return super().get_success_url()


class NewUser(SuccessMessageMixin, CreateView):

    form_class = CreateUserForm

    template_name = 'registration/signup.html'

    success_message = "usuario creado exitosamente"

    # this is how get method is overwritten in class view
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return super().get(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:index"), status = 302)

    # necessary to log user in after creation
    def form_valid(self, form):
        valid = super().form_valid(form)
        # group do not have a codename unlike permissions
        try:
            permission_group = Group.objects.get(name="usuario general")
        except Group.DoesNotExist:
            pass
        else:
            self.object.groups.add(permission_group)
        # you can actually do this
        # for adding one permission do this self.object.user_permissions.add(permission_user)
        # to add to a group do this:
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
    # HTTP_HX_REQUEST this tells that it is htmx
    if request.META.get("HTTP_HX_REQUEST", False):
        if request.method == "GET":
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
                # this for redirect with htmx
                new_response = HttpResponse()
                new_response["HX-Redirect"] = reverse("vehiculo:list")
                return new_response
            else:
                context = {"form": form}
                return render(request, "vehiculo/edit.html", context, status=200)
    raise PermissionDenied
    
@login_required(login_url=reverse_lazy("vehiculo:login"))
def delete_vehiculo(request, pk):
    if request.META.get("HTTP_HX_REQUEST", False):
        if request.method == "DELETE":
            delete_vehiculo = get_object_or_404(Vehículo, pk=pk)
            old_entry = model_to_dict(instance=delete_vehiculo, exclude=["id", "creación", "modificación",])
            old_entry["categoría"] = delete_vehiculo.get_categoría_display()
            old_entry = ", ".join([f"{key}: {value}" for key, value in old_entry.items()])
            related_gallery = VehículoGalería.objects.all().filter(vehículo=pk)
            for entry in related_gallery:
                Path(entry.imágenes.path).unlink()
            delete_vehiculo.delete()
            messages.success(request, f"Entrada borrada exitosamente<br> {old_entry}", "éxito")
            new_response = HttpResponse()
            new_response["HX-Redirect"] = reverse("vehiculo:list")
            return new_response
        elif request.method == "GET":
            context = {"entry": pk}
            return render(request, "vehiculo/delete.html", context)
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
    current = model_to_dict(instance=current_element, exclude=["id", "creación", "modificación", "categoría",])
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
            total_img_gallery = 8
            if total_entries_images < total_img_gallery:
                messages.success(request, "imagen subida exitosamente", "éxito")
                vehicle_img = form.save(commit=False)
                vehicle_img.vehículo = get_object_or_404(Vehículo, pk=pk)
                vehicle_img.save()
                return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:gallery", kwargs={"pk": pk}), status = 302)

            else:
                messages.error(request, f"se supero el número máximo de imágenes por entrada de {total_img_gallery}", "error")
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
        return HttpResponseRedirect(redirect_to=reverse(f"vehiculo:gallery", kwargs={"pk": delete_img.vehículo.pk}), status = 302)
   else:
       raise PermissionDenied

@login_required(login_url=reverse_lazy("vehiculo:login"))
def download_csv(request, query):
    if request.method == "GET" and request.user.has_perm("vehiculo.dascargar_tabla"):
        csv_data = fetch_query(None if query == "all" else query)
        if csv_data:
            response = HttpResponse(
            content_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="vehículos.csv"'},
            )
            # HttpResponse is already a pseudo file so i can write directly to it
            writer = csv.writer(response, delimiter="|")
            file_header = [field.verbose_name for field in Vehículo._meta.get_fields() 
                               if field.name not in("id", "creación", "modificación", "vehículogalería")]
            file_header += ["Condición de precio",]
            writer.writerow(file_header)
            for item in csv_data:
                writer.writerow([item.marca, item.modelo, item.carrocería, item.motor, 
                                 item.precio, item.categoría, item.condición])
            return response
        else:
           return HttpResponseRedirect(redirect_to=reverse("vehiculo:list"), status = 302)
    else:
        raise PermissionDenied