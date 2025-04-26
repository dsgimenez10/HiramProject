from django.db import models
from django.contrib.auth.models import User
from datetime import date

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    imagen_usuario = models.ImageField(upload_to='imagenes_perfil/', default='imagenes_perfil/default_profile.png')
    nombres = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)

    pais = models.CharField(max_length=100, blank=True, null=True)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    estado = models.CharField(max_length=100, blank=True, null=True)
    codigo_postal = models.CharField(max_length=10, blank=True, null=True)
    direccion = models.CharField(max_length=255, blank=True, null=True)

    lenguaje = models.CharField(max_length=50, blank=True, null=True)
    rol = models.CharField(max_length=50, choices=[('user', 'User'), ('admin', 'Admin')], default='user')

    instagram = models.URLField(blank=True, null=True, default="")
    facebook = models.URLField(blank=True, null=True, default="")
    linkedin = models.URLField(blank=True, null=True, default="")
    x = models.URLField(blank=True, null=True, default="")
    youtube = models.URLField(blank=True, null=True, default="")

    bio = models.TextField(blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def edad(self):
        if self.fecha_nacimiento:
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

    def __str__(self):
        return f'{self.usuario.username} Profile'
    


