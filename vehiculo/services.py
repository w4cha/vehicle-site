from django.db.models import Case, When, Value, Q
from .models import Vehículo

def fetch_query(url_args = None):
    if url_args is not None and isinstance(url_args, str):
        total_args = url_args.split(";", 1)
        if len(total_args) == 2:
            v_marca, v_modelo = total_args
            partial = Q(marca__icontains=v_marca) & Q(modelo__icontains=v_modelo) 

        else:
            v_marca = v_modelo = url_args
            partial = Q(marca__icontains=v_marca) | Q(modelo__icontains=v_modelo) 
        query = Vehículo.objects.filter(partial).order_by('precio').annotate(condición=Case(
                When(precio__gte=0, precio__lt=10_000, then=Value("Bajo")),
                When(precio__gte=10_000, precio__lt=30_000, then=Value("Medio")),
                default=Value("Alto")),)
        return query
    else:
        query = Vehículo.objects.all().order_by('precio').annotate(condición=Case(
                When(precio__gte=0, precio__lt=10_000, then=Value("Bajo")),
                When(precio__gte=10_000, precio__lt=30_000, then=Value("Medio")),
                default=Value("Alto")),)
        return query
           