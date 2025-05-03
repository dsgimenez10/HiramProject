
from django.shortcuts import (
    render, 
    get_object_or_404, 
    redirect
)
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import (
    login_required, 
    permission_required, 
    user_passes_test
)
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import (
    User, 
    Group, 
    Permission
)

# Formularios propios
from .forms import ( 
    UserAdminEditForm, 
    UserCreateForm
)

from django.urls import NoReverseMatch
from transacciones.models import Transaccion
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth, TruncYear
from catalogos.models import Cuentas, Proyecto
from decimal import Decimal
from collections import defaultdict
from django.db.models import F, Case, When, Value, DecimalField

def login_view(request):
    """
    Vista para iniciar sesión (login).
    Si se recibe un POST, se intenta autenticar al usuario;
    de lo contrario, se muestra la plantilla de login.
    """
    if request.method == 'POST':
        # Se obtienen los datos del formulario
        username = request.POST['username']
        password = request.POST['password']
        
        # Se autentica el usuario
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Si existe el usuario, se hace login y se redirige
            login(request, user)
            return redirect('dashboard_view')
        else:
            # Si la autenticación falla, se devuelve la plantilla con error
            return render(request, 'core/login.html', {
                'error': 'Invalid username or password'
            })
    # Si es GET, solo se muestra la plantilla
    return render(request, 'core/login.html')

@login_required
def dashboard_view(request):
    ingresos_pesos = Transaccion.objects.filter(conciliado=True, moneda='Pesos', tipo_transaccion='Ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
    egresos_pesos = Transaccion.objects.filter(conciliado=True, moneda='Pesos', tipo_transaccion='Egreso').aggregate(Sum('monto'))['monto__sum'] or 0
    otros_ingresos = Transaccion.objects.filter(cuentas=7, tipo_transaccion='Ingreso').aggregate(Sum('monto'))['monto__sum'] or 0

    saldo_cta_pesos = ingresos_pesos - egresos_pesos

    ingresos_dolares = Transaccion.objects.filter(conciliado=True, moneda='Dolares', tipo_transaccion='Ingreso').aggregate(Sum('monto'))['monto__sum'] or 0
    egresos_dolares = Transaccion.objects.filter(conciliado=True, moneda='Dolares', tipo_transaccion='Egreso').aggregate(Sum('monto'))['monto__sum'] or 0
    saldo_cta_dolares = ingresos_dolares - egresos_dolares

    deudas_por_cobrar = Transaccion.objects.filter(cuentas__nombre='Factura GlobalGes', fecha_pago__isnull=True)
    total_deuda_por_cobrar_pesos = deudas_por_cobrar.filter(moneda='Pesos').aggregate(total=Sum('monto'))['total'] or 0
    total_deuda_por_cobrar_dolares = deudas_por_cobrar.filter(moneda='Dolares').aggregate(total=Sum('monto'))['total'] or 0

    deudas_a_pagar = Transaccion.objects.exclude(cuentas__nombre='Factura GlobalGes').filter(deuda='Si') | Transaccion.objects.exclude(cuentas__nombre='Factura GlobalGes').filter(fecha_pago__isnull=True)

    deudas_a_pagar = deudas_a_pagar.annotate(
        monto_ajustado=Case(
            When(cuentas__nombre='IVA Credito', then=F('monto')),
            When(cuentas__nombre='IVA Debito', then=F('monto') * -1),
            default=F('monto'),
            output_field=DecimalField()
        )
    )

    total_deudas_a_pagar_pesos = deudas_a_pagar.filter(moneda='Pesos').aggregate(
        total=Sum('monto_ajustado')
    )['total'] or 0

    total_deudas_a_pagar_dolares = deudas_a_pagar.filter(moneda='Dolares').aggregate(
        total=Sum('monto_ajustado')
    )['total'] or 0

    saldo_real_pesos = saldo_cta_pesos + otros_ingresos + total_deuda_por_cobrar_pesos - total_deudas_a_pagar_pesos
    saldo_real_dolares = saldo_cta_dolares + total_deuda_por_cobrar_dolares - total_deudas_a_pagar_dolares

    context = {
        'saldo_cta_pesos': saldo_cta_pesos,
        'otros_ingresos': otros_ingresos,
        'total_deuda_por_cobrar_pesos': total_deuda_por_cobrar_pesos,
        'total_deudas_a_pagar_pesos': total_deudas_a_pagar_pesos,
        'saldo_real_pesos': saldo_real_pesos,
        'saldo_cta_dolares': saldo_cta_dolares,
        'total_deuda_por_cobrar_dolares': total_deuda_por_cobrar_dolares,
        'total_deudas_a_pagar_dolares': total_deudas_a_pagar_dolares,
        'saldo_real_dolares': saldo_real_dolares,
    }
    return render(request, 'core/dashboard_view.html', context)



@login_required
def dashboard_data(request):
    if not request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Unauthorized'}, status=400)

    transacciones = Transaccion.objects.filter(
        conciliado=True,
        fecha_pago__year__in=[2024, 2025]
    )

    saldos = transacciones.annotate(
        anio=TruncYear('fecha_pago'),
        mes=TruncMonth('fecha_pago')
    ).values('anio', 'mes').annotate(
        total_ingresos=Sum('monto', filter=Q(tipo_transaccion='Ingreso')),
        total_egresos=Sum('monto', filter=Q(tipo_transaccion='Egreso')),
    ).order_by('mes')

    data = []
    saldo_acumulado = 0

    for item in saldos:
        ingresos = float(item['total_ingresos'] or 0)
        egresos = float(item['total_egresos'] or 0)
        saldo_anterior = saldo_acumulado
        saldo_acumulado += ingresos - egresos

        data.append({
            'mes': f"{item['mes'].strftime('%Y-%m')}",
            'ingresos': ingresos,
            'egresos': egresos,
            'saldo_acumulado': saldo_acumulado,
            'saldo_anterior': saldo_anterior
        })

    return JsonResponse(data, safe=False)

def datos_cuentas_logicas(request):
    cuentas = Cuentas.objects.all()
    cuentas_data = []

    for cuenta in cuentas:
        ingresos_pesos = Transaccion.objects.filter(
            cuentas=cuenta, tipo_transaccion='Ingreso', moneda='Pesos', conciliado=True
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        egresos_pesos = Transaccion.objects.filter(
            cuentas=cuenta, tipo_transaccion='Egreso', moneda='Pesos', conciliado=True
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        saldo_pesos = ingresos_pesos - egresos_pesos

        ingresos_dolares = Transaccion.objects.filter(
            cuentas=cuenta, tipo_transaccion='Ingreso', moneda='Dolares', conciliado=True
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        egresos_dolares = Transaccion.objects.filter(
            cuentas=cuenta, tipo_transaccion='Egreso', moneda='Dolares', conciliado=True
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        saldo_dolares = ingresos_dolares - egresos_dolares

        cuentas_data.append({
            'cuenta': cuenta.nombre,
            'pesos': float(saldo_pesos),
            'dolares': float(saldo_dolares),
            'total': abs(saldo_pesos) + abs(saldo_dolares)
        })

    cuentas_data.sort(key=lambda x: x['total'], reverse=True)
    data = cuentas_data[:10]

    return JsonResponse(data, safe=False)


@login_required
def dashboard_data_proyectos_completo(request):
    proyectos = Proyecto.objects.all()
    labels = []
    ingresos_list = []
    egresos_list = []
    saldos_list = []

    for proyecto in proyectos:
        ingresos = Transaccion.objects.filter(
            proyecto=proyecto, tipo_transaccion='Ingreso', conciliado=True, moneda='Pesos'
        ).aggregate(total=Sum('monto'))['total'] or 0

        egresos = Transaccion.objects.filter(
            proyecto=proyecto, tipo_transaccion='Egreso', conciliado=True, moneda='Pesos'
        ).aggregate(total=Sum('monto'))['total'] or 0

        saldo = ingresos - egresos

        labels.append(proyecto.nombre)
        ingresos_list.append(float(ingresos))
        egresos_list.append(float(egresos))
        saldos_list.append(float(saldo))

    return JsonResponse({
        'labels': labels,
        'ingresos': ingresos_list,
        'egresos': egresos_list,
        'saldos': saldos_list
    })



@login_required
def perfil(request):
    """
    Vista para mostrar y actualizar el perfil del usuario.
    Se asume que el modelo PerfilUsuario se accede con request.user.perfil.
    """
    # Obtenemos el perfil del usuario actual
    perfil = request.user.perfil  # Asegúrate de que user tenga un campo 'perfil'

    if request.method == "POST":
        # Se actualizan campos con los datos recibidos en el formulario
        perfil.nombres = request.POST.get('nombres', perfil.nombres)
        perfil.apellido = request.POST.get('apellido', perfil.apellido)
        perfil.telefono = request.POST.get('telefono', perfil.telefono)
        perfil.email = request.POST.get('email', perfil.email)
        perfil.fecha_nacimiento = request.POST.get('fecha_nacimiento', perfil.fecha_nacimiento)
        perfil.pais = request.POST.get('pais', perfil.pais)
        perfil.ciudad = request.POST.get('ciudad', perfil.ciudad)
        perfil.estado = request.POST.get('estado', perfil.estado)
        perfil.codigo_postal = request.POST.get('codigo_postal', perfil.codigo_postal)
        perfil.direccion = request.POST.get('direccion', perfil.direccion)
        perfil.lenguaje = request.POST.get('lenguaje', perfil.lenguaje)
        perfil.rol = request.POST.get('rol', perfil.rol)
        perfil.instagram = request.POST.get('instagram', perfil.instagram)
        perfil.facebook = request.POST.get('facebook', perfil.facebook)
        perfil.linkedin = request.POST.get('linkedin', perfil.linkedin)
        perfil.x = request.POST.get('x', perfil.x)  # Twitter/X
        perfil.youtube = request.POST.get('youtube', perfil.youtube)
        perfil.bio = request.POST.get('bio', perfil.bio)
        perfil.sitio_web = request.POST.get('sitio_web', perfil.sitio_web)

        # Si se subió una nueva imagen de perfil
        if 'imagen_usuario' in request.FILES:
            perfil.imagen_usuario = request.FILES['imagen_usuario']

        # Guardar cambios
        perfil.save()
        return redirect('perfil')  # Redirigir a la misma vista o a otra

    # GET: Renderizar el perfil con sus datos
    return render(request, 'core/perfil.html', {'perfil': perfil})


# =============================================================================
# 4. Vistas para Cambiar Contraseña
# =============================================================================

@login_required
def password_change_view(request):
    """
    Vista para cambiar la contraseña del usuario actual.
    Utiliza el formulario PasswordChangeForm de Django.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Mantiene la sesión activa tras el cambio de contraseña
            update_session_auth_hash(request, form.user)
            return redirect('dashboard_view')
        else:
            messages.error(request, 'Corrige los errores del formulario.')
    else:
        form = PasswordChangeForm(user=request.user)
    
    # Obtener datos extra (último login, fecha de alta)
    last_login = (
        request.user.last_login.strftime('%d %b, %Y %H:%M')
        if request.user.last_login else 'Nunca'
    )
    date_joined = (
        request.user.date_joined.strftime('%d %b, %Y')
        if request.user.date_joined else 'Desconocida'
    )
    
    return render(request, 'core/admin/password_change.html', {
        'form': form,
        'last_login': last_login,
        'date_joined': date_joined
    })


# =============================================================================
# 5. Administración de Usuarios (vistas estilo Admin)
# =============================================================================

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def list_users(request):
    """
    Lista todos los usuarios del sistema.
    Solo accesible a staff o superusuarios.
    """
    users = User.objects.all()
    return render(request, 'core/admin/admin_users_list.html', {'users': users})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def create_user(request):
    """
    Crea un nuevo usuario utilizando el formulario UserCreateForm.
    Solo accesible a staff o superusuarios.
    """
    if request.method == 'POST':
        form = UserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_users')
    else:
        form = UserCreateForm()
    
    return render(request, 'core/admin/admin_user_create.html', {'form': form})


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def admin_user_edit_view(request, user_id):
    """
    Edita un usuario existente, simulando el panel de Django Admin,
    con doble lista de grupos y permisos.
    """
    user = get_object_or_404(User, pk=user_id)

    # 1. Separamos Grupos asignados vs. disponibles
    all_groups = Group.objects.all().order_by('name')
    assigned_groups = user.groups.all()  
    available_groups = all_groups.exclude(id__in=assigned_groups)

    # 2. Separamos Permisos asignados vs. disponibles
    all_perms = Permission.objects.all().order_by('name')
    assigned_perms = user.user_permissions.all()
    available_perms = all_perms.exclude(id__in=assigned_perms)

    if request.method == 'POST':
        form = UserAdminEditForm(request.POST, instance=user)
        if form.is_valid():
            # Guardar campos "básicos" (username, email, is_staff, etc.)
            updated_user = form.save(commit=False)

            # Manejo de contraseña
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                updated_user.set_password(new_password)

            updated_user.save()

            # 3. Procesar grupos y permisos desde el POST
            #    - Suponiendo que en la plantilla usas <select name="assigned_groups" multiple>
            new_group_ids = request.POST.getlist('assigned_groups')  
            new_perm_ids = request.POST.getlist('assigned_perms')

            updated_user.groups.set(new_group_ids)  
            updated_user.user_permissions.set(new_perm_ids)

            messages.success(request, "Usuario modificado con éxito.")
            return redirect('list_users')
        else:
            messages.error(request, "Por favor, corrige los errores del formulario.")

        # Si form no es válido, recalculamos las listas con la data actual
        assigned_groups = user.groups.all()
        available_groups = all_groups.exclude(id__in=assigned_groups)
        assigned_perms = user.user_permissions.all()
        available_perms = all_perms.exclude(id__in=assigned_perms)
    else:
        form = UserAdminEditForm(instance=user)

    context = {
        'form': form,
        'user_obj': user,
        # Listas para la doble-lateral:
        'available_groups': available_groups,
        'assigned_groups': assigned_groups,
        'available_perms': available_perms,
        'assigned_perms': assigned_perms,
    }
    return render(request, 'core/admin/admin_user_edit_full.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_user(request, user_id):
    """
    Elimina un usuario, previa confirmación.
    Solo accesible a staff o superusuarios.
    """
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        user.delete()
        return redirect('list_users')
    return render(request, 'core/admin/admin_user_delete.html', {'user_obj': user})


# =============================================================================
# 6. Administración de Grupos (vistas estilo Admin)
# =============================================================================

@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def list_groups(request):
    """
    Lista todos los grupos existentes (Group).
    Solo accesible a staff o superusuarios.
    """
    groups = Group.objects.all()
    return render(request, 'core/admin/admin_groups_list.html', {'groups': groups})


@login_required
@permission_required('auth.add_group', raise_exception=True)
def create_group_view(request):
    """
    Crea un nuevo grupo con los permisos seleccionados.
    Utiliza un input hidden 'permissions' que contiene IDs separados por comas.
    """
    if request.method == 'POST':
        group_name = request.POST.get('name', '').strip()
        
        # Se crea el grupo
        new_group = Group.objects.create(name=group_name)
        
        # Se añaden los permisos
        permissions_str = request.POST.get('permissions', '')  # "1,2,3"
        if permissions_str:
            perm_ids = permissions_str.split(',')
            for pid in perm_ids:
                if pid:
                    try:
                        perm = Permission.objects.get(id=pid)
                        new_group.permissions.add(perm)
                    except Permission.DoesNotExist:
                        pass
        
        return redirect('list_groups')
    else:
        # En GET se muestra la lista de todos los permisos disponibles
        all_permissions = Permission.objects.all().order_by('name')
        return render(request, 'core/admin/admin_group_create.html', {
            'all_permissions': all_permissions,
        })


@login_required
@permission_required('auth.change_group', raise_exception=True)
def edit_group_view(request, group_id):
    """
    Edita un grupo existente y sus permisos.
    - Limpia los permisos actuales
    - Agrega los permisos recibidos en el campo hidden
    """
    group_obj = get_object_or_404(Group, pk=group_id)
    all_permissions = Permission.objects.all().order_by('name')
    
    if request.method == 'POST':
        # Actualizar nombre
        group_name = request.POST.get('name', '').strip()
        group_obj.name = group_name
        group_obj.save()

        # Limpiar permisos actuales
        group_obj.permissions.clear()

        # Asignar nuevos permisos
        permissions_str = request.POST.get('permissions', '')
        if permissions_str:
            perm_ids = permissions_str.split(',')
            for pid in perm_ids:
                if pid:
                    try:
                        perm = Permission.objects.get(id=pid)
                        group_obj.permissions.add(perm)
                    except Permission.DoesNotExist:
                        pass
        
        return redirect('list_groups')
    else:
        # GET: mostrar formulario de edición
        context = {
            'group_obj': group_obj,
            'all_permissions': all_permissions,
        }
        return render(request, 'core/admin/admin_group_edit.html', context)


@user_passes_test(lambda u: u.is_staff or u.is_superuser)
def delete_group(request, group_id):
    """
    Elimina un grupo tras confirmación.
    Solo accesible a staff o superusuarios.
    """
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        group.delete()
        return redirect('list_groups')
    return render(request, 'core/admin/admin_group_delete.html', {'group_obj': group})


# Agregar - Editar form Simples --------------------------------------------------------------------------------------------------

def agregar_editar_form(request, FormClass, template_name, redirect_url, instance=None, instance_id=None, model=None):
    if instance_id and model:
        instance = get_object_or_404(model, pk=instance_id)
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
             # Verifica si `redirect_url` necesita `instance_id`
            try:
                return redirect(redirect_url, instance_id)
            except NoReverseMatch:
                return redirect(redirect_url)
    else:
        form = FormClass(instance=instance)
 
    return render(request, template_name, {'form': form, 'instance': instance})

# Eliminar form Simples ---------------------------------------------------------------------------------------------------------

def confirm_delete(request, model, redirect_url, id_contrato=None, instance_id=None, template_name='confirm_delete.html'):
    instance = get_object_or_404(model, pk=instance_id)

    if request.method == 'POST':
        instance.delete()
        messages.success(request, 'El registro ha sido eliminado correctamente.')
        
        # Intentar redirigir a una URL que puede necesitar instance_id
        try:
            if id_contrato:
                return redirect(redirect_url, id_contrato)
            else:
                return redirect(redirect_url, instance_id)
        except NoReverseMatch:
            return redirect(redirect_url)
    
    # Captura la URL anterior o usa el valor por defecto
    previous_url = request.META.get('HTTP_REFERER', redirect_url)
    
    return render(request, template_name, {'instance': instance, 'previous_url': previous_url})