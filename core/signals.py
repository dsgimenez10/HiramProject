# core/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import PerfilUsuario

# Crear o actualizar el perfil cuando se crea o guarda un usuario
@receiver(post_save, sender=User)
def create_or_update_perfil(sender, instance, created, **kwargs):
    if created:
        # Crear un perfil y copiar datos desde el modelo User
        PerfilUsuario.objects.create(
            usuario=instance,
            nombres=instance.first_name,
            apellido=instance.last_name,
            email=instance.email
        )
    else:
        # Actualizar el perfil existente
        try:
            profile = instance.perfil  # Usar el related_name definido en el modelo
            profile.nombres = instance.first_name
            profile.apellido = instance.last_name
            profile.email = instance.email
            profile.save()
        except PerfilUsuario.DoesNotExist:
            # Si no existe un perfil, crearlo
            PerfilUsuario.objects.create(
                usuario=instance,
                nombres=instance.first_name,
                apellido=instance.last_name,
                email=instance.email
            )