from django.contrib import admin
from .models import PerfilUsuario
from django.contrib import admin


@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    # Campos a mostrar en la lista
    list_display = ('usuario', 'email', 'nombres', 'apellido', 'rol', 'fecha_registro')
    search_fields = ('usuario__username', 'email', 'nombres', 'apellido', 'rol')
    list_filter = ('rol', 'pais', 'lenguaje', 'fecha_registro')
    ordering = ('-fecha_registro',)
    readonly_fields = ('fecha_registro',)  # Marcar fecha_registro como solo lectura

    # Configuración de campos agrupados por secciones
    fieldsets = (
        ('Información básica', {
            'fields': ('usuario', 'imagen_usuario', 'nombres', 'apellido', 'email', 'telefono', 'fecha_nacimiento')
        }),
        ('Ubicación', {
            'fields': ('pais', 'ciudad', 'estado', 'codigo_postal', 'direccion')
        }),
        ('Preferencias e idioma', {
            'fields': ('lenguaje', 'rol')
        }),
        ('Redes sociales', {
            'fields': ('instagram', 'facebook', 'linkedin', 'x', 'youtube')
        }),
        ('Información adicional', {
            'fields': ('bio', 'sitio_web', 'fecha_registro')  # fecha_registro se mostrará, pero no será editable
        }),
    )
