from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "vehiculo"

urlpatterns = [
    # name is useful for url references in template
    path("", views.IndexView.as_view(), name="index"),
    path("list/", views.VehicleList.as_view(), name="list"),
    path("add/", views.VehicleCreateView.as_view(), name="add-vehicle"),
    path("login/", views.LogUserIn.as_view(), name="login"),
    path("logout/", views.LogUserOut.as_view(), name="logout"),
    path("registro/", views.NewUser.as_view(), name="sign-up"),
    path("update/<int:pk>", views.update_vehiculo, name="update"),
    path("delete/<int:pk>", views.delete_vehiculo, name="delete"),
    path("gallery/<int:pk>", views.gallery_view, name="gallery"),
    path("del-img/<int:pk>", views.delete_img, name="rm-img"),
    path("download/<str:query>", views.download_csv, name="vehicle_csv"),
]