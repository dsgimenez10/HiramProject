from django.shortcuts import render
from .models import Transaccion
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from catalogos.models import Proyecto, Contacto, Cuentas, CuentaBancaria
# Listados ---------------------------------------------------------------------------------------------------------

def transaccion(request):
    transacciones = Transaccion.objects.all().order_by('fecha_pago')
    
    return render(request, 'transacciones/transaccion.html', {'transacciones': transacciones})

@csrf_exempt
def actualizar_conciliado(request):
    if request.method == "POST":
        transaccion_id = request.POST.get('transaccion_id')
        conciliado = request.POST.get('conciliado') == 'true'  # Verificamos si es true o false

        if not transaccion_id:
            return JsonResponse({'success': False, 'message': 'Falta transaccion_id'}, status=400)

        try:
            # Obtener la transacción
            transaccion = Transaccion.objects.get(id=transaccion_id)
            # Actualizar el estado de conciliado
            transaccion.conciliado = conciliado
            transaccion.save()

            # Responder con éxito
            return JsonResponse({'success': True})

        except Transaccion.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Transacción no encontrada'}, status=404)

    return JsonResponse({'success': False, 'message': 'Método no permitido o solicitud no válida'}, status=400)

# Reportes--------------------------------------------------------------------------------------------------

def libro_diario(request):
    # Obtener todas las transacciones ordenadas por fecha
    transacciones = Transaccion.objects.filter(conciliado=True).order_by('fecha_pago')

    # Inicializar el saldo total
    saldo_total = 0

    # Calcular los ingresos y egresos totales en pesos y dólares
    ingresos_totales_pesos = transacciones.filter(moneda='Pesos', tipo_transaccion='Ingreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    egresos_totales_pesos = transacciones.filter(moneda='Pesos', tipo_transaccion='Egreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    saldo_total_pesos = ingresos_totales_pesos - egresos_totales_pesos

    # Agregar el saldo acumulado a cada transacción
    for transaccion in transacciones:
        # Calcular el saldo total basado en el tipo de transacción
        if transaccion.tipo_transaccion == "Ingreso":
            saldo_total += transaccion.monto
        else:  # Egreso
            saldo_total -= transaccion.monto
        
        # Almacenar el saldo total en cada objeto de transacción
        transaccion.saldo_acumulado = saldo_total

    # Asegúrate de pasar las transacciones a la plantilla
    return render(request, 'transacciones/libro_diario.html', {
        'transacciones': transacciones,
        'ingresos_totales_pesos': ingresos_totales_pesos,
        'egresos_totales_pesos': egresos_totales_pesos,
        'saldo_total_pesos': saldo_total_pesos,
    })


def resumen_por_proyecto(request):
    # Calcular ingresos y egresos totales en Pesos
    ingresos_totales_pesos = Transaccion.objects.filter(tipo_transaccion='Ingreso', moneda='Pesos', conciliado=True).aggregate(total=Sum('monto'))['total'] or 0.00
    egresos_totales_pesos = Transaccion.objects.filter(tipo_transaccion='Egreso', moneda='Pesos', conciliado=True).aggregate(total=Sum('monto'))['total'] or 0.00
    saldo_total_pesos = ingresos_totales_pesos - egresos_totales_pesos

    # Calcular ingresos y egresos totales en Dólares
    ingresos_totales_dolares = Transaccion.objects.filter(tipo_transaccion='Ingreso', moneda='Dólares', conciliado=True).aggregate(total=Sum('monto'))['total'] or 0.00
    egresos_totales_dolares = Transaccion.objects.filter(tipo_transaccion='Egreso', moneda='Dólares', conciliado=True).aggregate(total=Sum('monto'))['total'] or 0.00
    saldo_total_dolares = ingresos_totales_dolares - egresos_totales_dolares

    # Obtener todos los proyectos y sus resúmenes en ambas monedas
    proyectos = Proyecto.objects.all()
    resumen_por_proyecto = []

    for proyecto in proyectos:
        # Calcular ingresos y egresos para el proyecto en Pesos
        ingresos_pesos = Transaccion.objects.filter(
            proyecto=proyecto, 
            tipo_transaccion='Ingreso', 
            moneda='Pesos',
            conciliado=True,
        ).aggregate(total=Sum('monto'))['total'] or 0.00

        egresos_pesos = Transaccion.objects.filter(
            proyecto=proyecto, 
            tipo_transaccion='Egreso', 
            moneda='Pesos',
            conciliado=True,
        ).aggregate(total=Sum('monto'))['total'] or 0.00

        saldo_pesos = ingresos_pesos - egresos_pesos

        # Calcular ingresos y egresos para el proyecto en Dólares
        ingresos_dolares = Transaccion.objects.filter(
            proyecto=proyecto, 
            tipo_transaccion='Ingreso', 
            moneda='Dólares',
            conciliado=True,
        ).aggregate(total=Sum('monto'))['total'] or 0.00

        egresos_dolares = Transaccion.objects.filter(
            proyecto=proyecto, 
            tipo_transaccion='Egreso', 
            moneda='Dólares',
            conciliado=True,
        ).aggregate(total=Sum('monto'))['total'] or 0.00

        saldo_dolares = ingresos_dolares - egresos_dolares

        # Agregar al resultado si hay algún movimiento en alguna de las monedas
        if ingresos_pesos > 0 or egresos_pesos > 0 or ingresos_dolares > 0 or egresos_dolares > 0:
            resumen_por_proyecto.append({
                'proyecto': proyecto,
                'ingresos_pesos': ingresos_pesos,
                'egresos_pesos': egresos_pesos,
                'saldo_pesos': saldo_pesos,
                'ingresos_dolares': ingresos_dolares,
                'egresos_dolares': egresos_dolares,
                'saldo_dolares': saldo_dolares,
            })
    
    # Renderizar la plantilla con los resultados en ambas monedas
    return render(request, 'transacciones/resumen_por_proyecto.html', {
        'ingresos_totales_pesos': ingresos_totales_pesos,
        'egresos_totales_pesos': egresos_totales_pesos,
        'saldo_total_pesos': saldo_total_pesos,
        'ingresos_totales_dolares': ingresos_totales_dolares,
        'egresos_totales_dolares': egresos_totales_dolares,
        'saldo_total_dolares': saldo_total_dolares,
        'resumen_por_proyecto': resumen_por_proyecto,
    })

def deudas_por_cobrar(request):
    # Filtrar las transacciones que son de 'Factura GlobalGes' y no tienen fecha_pago
    deudas = Transaccion.objects.filter(cuentas__nombre='Factura GlobalGes', fecha_pago__isnull=True)
    
    # Agrupar por moneda y contacto, y sumar el monto
    deudas_por_moneda_y_contacto = deudas.values('moneda', 'contacto__nombre').annotate(total_monto=Sum('monto')).order_by('moneda', 'contacto__nombre')
    
    # Calcular el total en Pesos y Dólares
    total_deuda_pesos = deudas.filter(moneda='Pesos').aggregate(total=Sum('monto'))['total'] or 0
    total_deuda_dolares = deudas.filter(moneda='Dolares').aggregate(total=Sum('monto'))['total'] or 0

    return render(request, 'transacciones/deudas_por_cobrar.html', {
        'deudas_por_moneda_y_contacto': deudas_por_moneda_y_contacto,
        'total_deuda_pesos': total_deuda_pesos,
        'total_deuda_dolares': total_deuda_dolares
    })

def deudas_a_pagar(request):
    # Filtrar las transacciones que no son de 'Factura GlobalGes' y no tienen fecha_pago
    # Filtrar las transacciones que no son de 'Factura GlobalGes' y, si tienen 'deuda' en 'Si', no importar la fecha_pago
    deudas = Transaccion.objects.exclude(cuentas__nombre='Factura GlobalGes').filter(
        deuda='Si'  # Incluir las transacciones con deuda en 'Si'
    ) | Transaccion.objects.exclude(cuentas__nombre='Factura GlobalGes').filter(fecha_pago__isnull=True)
    
    # Agrupar por moneda y contacto, y sumar el monto
    deudas_por_moneda_y_contacto = deudas.values('moneda', 'contacto__nombre').annotate(total_monto=Sum('monto')).order_by('moneda', 'contacto__nombre')
    
    # Calcular el total en Pesos y Dólares
    total_deuda_pesos = deudas.filter(moneda='Pesos').aggregate(total=Sum('monto'))['total'] or 0
    total_deuda_dolares = deudas.filter(moneda='Dolares').aggregate(total=Sum('monto'))['total'] or 0
    
    return render(request, 'transacciones/deudas_a_pagar.html', {
        'deudas_por_moneda_y_contacto': deudas_por_moneda_y_contacto,
        'total_deuda_pesos': total_deuda_pesos,
        'total_deuda_dolares': total_deuda_dolares
    })

def saldos_por_contacto(request):
    # Filtrar transacciones que están conciliadas
    transacciones_conciliadas = Transaccion.objects.filter(conciliado=True)

    # Calcular los ingresos y egresos totales en pesos y dólares
    ingresos_totales_pesos = transacciones_conciliadas.filter(moneda='Pesos', tipo_transaccion='Ingreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    egresos_totales_pesos = transacciones_conciliadas.filter(moneda='Pesos', tipo_transaccion='Egreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    saldo_total_pesos = ingresos_totales_pesos - egresos_totales_pesos

    ingresos_totales_dolares = transacciones_conciliadas.filter(moneda='Dólares', tipo_transaccion='Ingreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    egresos_totales_dolares = transacciones_conciliadas.filter(moneda='Dólares', tipo_transaccion='Egreso').aggregate(
        total=Sum('monto')
    )['total'] or 0

    saldo_total_dolares = ingresos_totales_dolares - egresos_totales_dolares

    # Agrupar por contacto y moneda, y calcular ingresos, egresos y saldo
    saldos_por_contacto = transacciones_conciliadas.values('contacto__nombre', 'moneda').annotate(
        ingresos_pesos=Sum(
            Case(
                When(moneda='Pesos', tipo_transaccion='Ingreso', then=F('monto')),
                default=0,
                output_field=DecimalField()
            )
        ),
        egresos_pesos=Sum(
            Case(
                When(moneda='Pesos', tipo_transaccion='Egreso', then=F('monto')),
                default=0,
                output_field=DecimalField()
            )
        ),
        saldo_pesos=Sum(
            Case(
                When(moneda='Pesos', tipo_transaccion='Ingreso', then=F('monto')),
                When(moneda='Pesos', tipo_transaccion='Egreso', then=-F('monto')),
                default=0,
                output_field=DecimalField()
            )
        ),
        ingresos_dolares=Sum(
            Case(
                When(moneda='Dólares', tipo_transaccion='Ingreso', then=F('monto')),
                default=0,
                output_field=DecimalField()
            )
        ),
        egresos_dolares=Sum(
            Case(
                When(moneda='Dólares', tipo_transaccion='Egreso', then=F('monto')),
                default=0,
                output_field=DecimalField()
            )
        ),
        saldo_dolares=Sum(
            Case(
                When(moneda='Dólares', tipo_transaccion='Ingreso', then=F('monto')),
                When(moneda='Dólares', tipo_transaccion='Egreso', then=-F('monto')),
                default=0,
                output_field=DecimalField()
            )
        )
    ).order_by('contacto__nombre', 'moneda')
    
    return render(request, 'transacciones/saldos_por_contacto.html', {
        'saldos_por_contacto': saldos_por_contacto,
        'ingresos_totales_pesos': ingresos_totales_pesos,
        'egresos_totales_pesos': egresos_totales_pesos,
        'saldo_total_pesos': saldo_total_pesos,
        'ingresos_totales_dolares': ingresos_totales_dolares,
        'egresos_totales_dolares': egresos_totales_dolares,
        'saldo_total_dolares': saldo_total_dolares,
    })

def certificados_de_ganancias(request):
    # Filtrar transacciones donde tipo_transaccion es "Ingreso" y cuenta es "Impuesto a las Ganancias"
    ingresos_impuesto_ganancias = Transaccion.objects.filter(
        tipo_transaccion='Ingreso',
        cuentas__nombre='Impuesto a las Ganancias'  # Ajusta 'cuenta__nombre' según tu modelo
    )

    # Calcular el total de los montos en pesos y en dólares
    total_monto = ingresos_impuesto_ganancias.aggregate(total_pesos=Sum('monto'))['total_pesos'] or 0

    return render(request, 'transacciones/certificados_de_ganancias.html', {
        'ingresos_impuesto_ganancias': ingresos_impuesto_ganancias,
        'total_monto': total_monto,
    })

def iva(request):
    # Filtrar transacciones donde la cuenta es "IVA Crédito"
    iva_credito = Transaccion.objects.filter(cuentas__nombre='IVA Credito').annotate(month=TruncMonth('fecha'))
    
    
    iva_credito_por_mes = iva_credito.values('month').annotate(total_credito=Sum('monto')).order_by('month')
    

    # Filtrar transacciones donde la cuenta es "IVA Débito"
    iva_debito = Transaccion.objects.filter(cuentas__nombre='IVA Debito').annotate(month=TruncMonth('fecha'))
    
    iva_debito_por_mes = iva_debito.values('month').annotate(total_debito=Sum('monto')).order_by('month')
    
    # Crear una lista para los resultados con los cálculos
    totales_por_mes = []

    # Combinar los resultados de "IVA Crédito" y "IVA Débito"
    for credito in iva_credito_por_mes:
        # Buscar el IVA Débito correspondiente al mismo mes
        debito = next((item for item in iva_debito_por_mes if item['month'] == credito['month']), None)

        # Si existe un débito para el mes, calculamos el 21% de ese total
        if debito:
            iva_21 = debito['total_debito']
            saldo = credito['total_credito'] - iva_21
        else:
            iva_21 = 0  # Si no hay débito, no hay cálculo de IVA 21%
            saldo = credito['total_credito']  # Solo el total de crédito

        totales_por_mes.append({
            'month': credito['month'],
            'total_credito': credito['total_credito'],
            'total_debito': debito['total_debito'] if debito else 0,
            'iva_21_debito': iva_21,
            'saldo': saldo,
        })
    
    
    # Calcular el total de IVA Crédito
    total_credito = sum([item['total_credito'] for item in totales_por_mes])

    # Calcular el total de IVA Débito
    total_debito = (sum([item['total_debito'] for item in totales_por_mes]))
    
    # Pasamos los resultados a la plantilla
    return render(request, 'transacciones/iva.html', {
        'totales_por_mes': totales_por_mes,
        'total_debito': total_debito,
        'total_credito': total_credito,
    })
