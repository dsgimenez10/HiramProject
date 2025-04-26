from core.models import PerfilUsuario

def perfil(request):
    # Verifica si el usuario está autenticado
    if request.user.is_authenticated:
        # Intenta obtener el perfil del usuario. Si no existe, lo crea.
        perfil, created = PerfilUsuario.objects.get_or_create(usuario=request.user)
        return {
            'perfil': perfil  # Añade el perfil del usuario al contexto
        }
    return {}