from django.urls import path
from .forms import TransaccionForm
from .models import Transaccion
from .views import libro_diario, actualizar_conciliado, resumen_por_proyecto, deudas_por_cobrar, deudas_a_pagar, saldos_por_contacto, certificados_de_ganancias, iva, transaccion
from core.views import agregar_editar_form, confirm_delete

app_name = 'transacciones'

template_name = 'core/CRUD_Generico/agregar_editar_form.html'
template_name_eliminar = 'core/CRUD_Generico/confirm_delete.html'
redirect_url_detalle = 'detalle'

urlpatterns = [

    path('libro_diario/', libro_diario, name='libro_diario'),
    path('actualizar_conciliado/', actualizar_conciliado, name='actualizar_conciliado'),
    path('resumen_por_proyecto/', resumen_por_proyecto, name='resumen_por_proyecto'),
    path('deudas_por_cobrar/', deudas_por_cobrar, name='deudas_por_cobrar'),
    path('deudas_a_pagar/', deudas_a_pagar, name='deudas_a_pagar'),
    path('saldos_por_contacto/', saldos_por_contacto, name='saldos_por_contacto'),
    path('certificados_de_ganancias/', certificados_de_ganancias, name='certificados_de_ganancias'),
    path('iva/', iva, name='iva'),

    # Transaccion

    path('transaccion/', transaccion, name='transaccion'),

    path('transaccion/agregar/', 
        agregar_editar_form, 
        name='agregar_transaccion',
        kwargs={'FormClass': TransaccionForm, 'template_name': template_name, 'redirect_url': 'transacciones:transaccion'}
    ),

    path('transaccion/editar/<int:instance_id>/', 
        agregar_editar_form, 
        name='editar_transaccion',
        kwargs={'FormClass': TransaccionForm, 'template_name': template_name, 'redirect_url': 'transacciones:transaccion', 'model': Transaccion}
    ),

    path('transaccion/eliminar/<int:instance_id>/', 
        confirm_delete, 
        name='eliminar_transaccion',
        kwargs={'model': Transaccion, 'redirect_url': 'transacciones:transaccion', 'template_name': template_name_eliminar}
    ),
]