"""
URL configuration for rehabilitaweb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from usuarios.views import home
from usuarios import views
from usuarios.views import lista_maquinas_json




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('login/', views.login_views, name='login'),
    path('paciente/dashboard/', views.dashboard_paciente, name='dashboard_paciente'),
    path('doctor/dashboard/', views.dashboard_doctor, name='dashboard_doctor'),
    path('doctor/gestion_pacientes/', views.gestion_pacientes, name='gestion_pacientes'),
    path('api/pacientes/', views.lista_pacientes, name='lista_pacientes'),
    path('estado_arduino/', views.estado_arduino, name='estado_arduino'),
    path('lista_maquinas/', views.lista_maquinas, name='lista_maquinas'),
    path('agregar_paciente/', views.agregar_paciente, name='agregar_paciente'),
    path("estado_arduino/", views.estado_arduino, name="estado_arduino"),
    path("controlar_sesion/", views.controlar_sesion, name="controlar_sesion"),
    path('recibir_datos/', views.recibir_datos, name='recibir_datos'),
    path('lista_maquinas_json/', lista_maquinas_json, name='lista_maquinas_json'),
    path("recibir_datos_esp/", views.recibir_datos_esp, name="recibir_datos_esp"),
    path('comando_esp/', views.comando_esp, name='comando_esp'),

]
