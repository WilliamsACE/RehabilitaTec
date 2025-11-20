# models.py - Agregar estos modelos a los que ya tienes
from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    ROLES = [
        ('paciente', 'Paciente'),
        ('doctor', 'Doctor'),
    ]

    nombre = models.CharField(max_length=50)
    peso = models.FloatField(blank=True, null=True)
    altura = models.FloatField(blank=True, null=True)
    sesiones = models.CharField(max_length=50, blank=True)
    activacion_muscular = models.CharField(max_length=50, blank=True)
    descripcion_de_la_ultima_sesion = models.CharField(max_length=50, blank=True)
    tamano_de_la_pantorrilla = models.FloatField(blank=True, null=True)
    rol = models.CharField(max_length=10, choices=ROLES)

    def __str__(self):
        return f"{self.nombre} ({self.rol})"

class Maquinas(models.Model):
    
    numero = models.CharField(max_length=50)
    ip = models.GenericIPAddressField()

    class Meta:
        db_table = 'maquinas'

# NUEVOS MODELOS PARA EL SISTEMA ESP32
class EstadoMaquina(models.Model):
    maquina = models.OneToOneField(Maquinas, on_delete=models.CASCADE)
    activo = models.BooleanField(default=False)
    grados_actuales = models.IntegerField(default=0)
    repeticiones = models.IntegerField(default=0)
    stop_grados = models.IntegerField(default=0)  # <-- agrega esto
    modo = models.CharField(max_length=50, default="normal")
    conectado = models.BooleanField(default=True)
    ultimo_timestamp = models.FloatField(null=True, blank=True)

class ComandoMaquina(models.Model):
    TIPO_ACCIONES = [
        ('iniciar', 'Iniciar'),
        ('detener', 'Detener'),
        ('pausar', 'Pausar'),
        ('continuar', 'Continuar'),
    ]
    
    maquina = models.ForeignKey(Maquinas, on_delete=models.CASCADE, related_name='comandos')
    accion = models.CharField(max_length=20, choices=TIPO_ACCIONES)
    grados = models.IntegerField(null=True, blank=True)
    repeticiones = models.IntegerField(null=True, blank=True)
    ejecutado = models.BooleanField(default=False)
    timestamp_creacion = models.FloatField(default=0)
    timestamp_ejecucion = models.FloatField(null=True, blank=True)
    usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'comandos_maquinas'
        ordering = ['timestamp_creacion']
    
    def __str__(self):
        return f"{self.maquina.numero} - {self.accion}"

class SesionTerapia(models.Model):
    maquina = models.ForeignKey(Maquinas, on_delete=models.CASCADE, related_name='sesiones')
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='sesiones_terapia')
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    grados_objetivo = models.IntegerField()
    repeticiones_objetivo = models.IntegerField()
    repeticiones_completadas = models.IntegerField(default=0)
    completada = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'sesiones_terapia'
    
    def __str__(self):
        return f"Sesión {self.maquina.numero} - {self.usuario.nombre}"