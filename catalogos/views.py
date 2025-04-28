from django.shortcuts import render
from .models import Proyecto, Contacto, Cuentas, CuentaBancaria

def listado_proyectos(request):
    proyectos = Proyecto.objects.all()
    return render(request, 'catalogos/listado_proyectos.html', {'proyectos': proyectos})

def listado_contactos(request):
    contactos = Contacto.objects.all()
    return render(request, 'catalogos/listado_contactos.html', {'contactos': contactos})

def listado_cuentas(request):
    cuentas = Cuentas.objects.all()
    return render(request, 'catalogos/listado_cuentas.html', {'cuentas': cuentas})

def listado_cuentas_bancarias(request):
    cuentas_bancarias = CuentaBancaria.objects.all()
    return render(request, 'catalogos/listado_cuentas_bancarias.html', {'cuentas_bancarias': cuentas_bancarias})

