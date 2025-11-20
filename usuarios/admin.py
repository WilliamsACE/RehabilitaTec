from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UsuarioCreationForm
from .models import Usuario, Maquinas, EstadoMaquina, ComandoMaquina, SesionTerapia

class UsuarioAdmin(BaseUserAdmin):
    add_form = UsuarioCreationForm

    list_display = ('nombre', 'email', 'rol', 'is_staff', 'is_superuser')
    list_filter = ('rol', 'is_staff', 'is_superuser')

    # Edición de usuarios existentes
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {
            'fields': ('nombre', 'peso', 'altura' ,'tamano_de_la_pantorrilla', 'sesiones',
                       'activacion_muscular', 'descripcion_de_la_ultima_sesion', 'rol')
        }),
        ('Permisos', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    # Crear usuario nuevo
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'peso', 'altura' , 'tamano_de_la_pantorrilla',
                       'sesiones', 'activacion_muscular', 'username','descripcion_de_la_ultima_sesion',
                       'rol', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'nombre')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


admin.site.register(Usuario, UsuarioAdmin)

@admin.register(Maquinas)
class MaquinasAdmin(admin.ModelAdmin):
    list_display = ('id', 'numero', 'ip')
    search_fields = ('numero', 'ip')

@admin.register(EstadoMaquina)
class EstadoMaquinaAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'conectado', 'activo', 'grados_actuales', 'repeticiones', 'ultimo_timestamp')
    list_filter = ('conectado', 'activo', 'maquina')
    search_fields = ('maquina__numero',)

@admin.register(ComandoMaquina)
class ComandoMaquinaAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'accion', 'grados', 'repeticiones', 'ejecutado', 'usuario', 'timestamp_creacion')
    list_filter = ('ejecutado', 'accion', 'maquina')
    search_fields = ('maquina__numero', 'usuario__nombre')

@admin.register(SesionTerapia)
class SesionTerapiaAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'usuario', 'fecha_inicio', 'grados_objetivo', 'repeticiones_objetivo', 'repeticiones_completadas', 'completada')
    list_filter = ('completada', 'maquina', 'usuario')
    search_fields = ('maquina__numero', 'usuario__nombre')