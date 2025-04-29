from django.db import models
from simple_history.models import HistoricalRecords


class Transaccion(models.Model):
    TIPO_CHOICES = [
        ('Ingreso', 'Ingreso'),
        ('Egreso', 'Egreso')
    ]
    FORMA_PAGO = [
        ('Efectivo', 'Efectivo'),
        ('Banco', 'Banco')
    ]
    MONEDA = [
        ('Pesos', 'Pesos'),
        ('Dolares', 'Dolares')
    ]
    SINO = [
        ('Si', 'Si'),
        ('No', 'No')
    ]

    fecha = models.DateField()
    proyecto = models.ForeignKey('catalogos.Proyecto', on_delete=models.SET_NULL, null=True, blank=True)
    tipo_transaccion = models.CharField(max_length=10, choices=TIPO_CHOICES)
    contacto = models.ForeignKey('catalogos.Contacto', on_delete=models.SET_NULL, null=True, blank=True, related_name='transaccion_principal')
    forma_pago = models.CharField(max_length=10, choices=FORMA_PAGO, null=True, blank=True)
    moneda = models.CharField(max_length=10, choices=MONEDA, null=True, blank=True)
    cuenta_bancaria = models.ForeignKey('catalogos.CuentaBancaria', on_delete=models.CASCADE, null=True, blank=True) 
    cuentas = models.ForeignKey('catalogos.Cuentas', on_delete=models.CASCADE, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    detalle = models.TextField()
    fecha_pago = models.DateField(null=True, blank=True)
    deuda = models.CharField(max_length=10, choices=SINO, null=True, blank=True)
    conciliado = models.BooleanField(default=False)
    archivo = models.FileField(upload_to='transacciones/', null=True, blank=True)  # Nuevo campo

    history = HistoricalRecords()  # 👈 Agregado el historial de cambios

    def __str__(self):
        return f"{self.tipo_transaccion} - {self.monto} - {self.contacto}"