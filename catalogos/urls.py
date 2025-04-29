from django.urls import path
from .forms import ProyectoForm, ContactoForm, CuentasForm, CuentaBancariaForm
from .models import Proyecto, Contacto, Cuentas, CuentaBancaria
from .views import listado_proyectos, listado_contactos, listado_cuentas, listado_cuentas_bancarias
from core.views import agregar_editar_form, confirm_delete



app_name = 'catalogos'

template_name = 'core/CRUD_Generico/agregar_editar_form.html'
template_name_eliminar = 'core/CRUD_Generico/confirm_delete.html'
redirect_url_detalle = 'detalle'

urlpatterns = [

    path('proyectos/', listado_proyectos, name='listado_proyectos'),
    path('contactos/', listado_contactos, name='listado_contactos'),
    path('cuentas/', listado_cuentas, name='listado_cuentas'),
    path('cuentas_bancarias/', listado_cuentas_bancarias, name='listado_cuentas_bancarias'),

    # PROYECTOS
    path('proyectos/agregar/', 
         agregar_editar_form,
         name='agregar_proyecto',
         kwargs={'FormClass': ProyectoForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_proyectos'}
    ),
    path('proyectos/editar/<int:instance_id>/', 
         agregar_editar_form,
         name='editar_proyecto',
         kwargs={'FormClass': ProyectoForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_proyectos', 'model': Proyecto}
    ),
    path('proyectos/eliminar/<int:instance_id>/', 
         confirm_delete,
         name='eliminar_proyecto',
         kwargs={'model': Proyecto, 'redirect_url': 'catalogos:listado_proyectos', 'template_name': template_name_eliminar}
    ),

    # CONTACTOS
    path('contactos/agregar/', 
         agregar_editar_form,
         name='agregar_contacto',
         kwargs={'FormClass': ContactoForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_contactos'}
    ),
    path('contactos/editar/<int:instance_id>/', 
         agregar_editar_form,
         name='editar_contacto',
         kwargs={'FormClass': ContactoForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_contactos', 'model': Contacto}
    ),
    path('contactos/eliminar/<int:instance_id>/', 
         confirm_delete,
         name='eliminar_contacto',
         kwargs={'model': Contacto, 'redirect_url': 'catalogos:listado_contactos', 'template_name': template_name_eliminar}
    ),

    # CUENTAS
    path('cuentas/agregar/', 
         agregar_editar_form,
         name='agregar_cuenta',
         kwargs={'FormClass': CuentasForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_cuentas'}
    ),
    path('cuentas/editar/<int:instance_id>/', 
         agregar_editar_form,
         name='editar_cuenta',
         kwargs={'FormClass': CuentasForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_cuentas', 'model': Cuentas}
    ),
    path('cuentas/eliminar/<int:instance_id>/', 
         confirm_delete,
         name='eliminar_cuenta',
         kwargs={'model': Cuentas, 'redirect_url': 'catalogos:listado_cuentas', 'template_name': template_name_eliminar}
    ),

    # CUENTAS BANCARIAS
    path('cuentas_bancarias/agregar/', 
         agregar_editar_form,
         name='agregar_cuenta_bancaria',
         kwargs={'FormClass': CuentaBancariaForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_cuentas_bancarias'}
    ),
    path('cuentas_bancarias/editar/<int:instance_id>/', 
         agregar_editar_form,
         name='editar_cuenta_bancaria',
         kwargs={'FormClass': CuentaBancariaForm, 'template_name': template_name, 'redirect_url': 'catalogos:listado_cuentas_bancarias', 'model': CuentaBancaria}
    ),
    path('cuentas_bancarias/eliminar/<int:instance_id>/', 
         confirm_delete,
         name='eliminar_cuenta_bancaria',
         kwargs={'model': CuentaBancaria, 'redirect_url': 'catalogos:listado_cuentas_bancarias', 'template_name': template_name_eliminar}
    ),
]

