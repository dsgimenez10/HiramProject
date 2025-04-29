from django.contrib import admin
from .models import Transaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('cuenta_bancaria', 'contacto', 'monto', 'fecha', 'conciliado')
    list_filter = ('fecha', 'conciliado', 'tipo_transaccion', 'forma_pago', 'moneda', 'deuda')
    search_fields = ('contacto__nombre', 'cuenta_bancaria__numero_cuenta')
