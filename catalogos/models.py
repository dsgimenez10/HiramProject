from django.db import models
from simple_history.models import HistoricalRecords
# from smart_selects.db_fields import ChainedForeignKey  # Descomentar si usás Chained fields

class Contacto(models.Model):
    TIPO_CHOICES = [
        ('Cliente', 'Cliente'),
        ('Proveedor', 'Proveedor')
    ]

    nombre = models.CharField(max_length=255)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cuit = models.CharField(max_length=15)

    history = HistoricalRecords()  # 👈 Historial de cambios

    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    MONEDA = [
        ('Pesos', 'Pesos'),
        ('Dolares', 'Dolares')
    ]

    contacto = models.ForeignKey('Contacto', on_delete=models.SET_NULL, null=True, blank=True)  # Relación con Contacto
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(blank=True, null=True)
    estado = models.CharField(max_length=50, choices=[
        ('En Progreso', 'En Progreso'),
        ('Completado', 'Completado'),
        ('Pendiente', 'Pendiente')
    ])
    moneda = models.CharField(max_length=10, choices=MONEDA, null=True, blank=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)

    history = HistoricalRecords()  # 👈 Historial de cambios

    def __str__(self):
        return self.nombre

class Cuentas(models.Model):
    nombre = models.CharField(max_length=250)

    history = HistoricalRecords()  # 👈 Historial de cambios

    def __str__(self):
        return self.nombre

class CuentaBancaria(models.Model):
    numero_cuenta = models.CharField(max_length=20)
    banco = models.CharField(max_length=255)
    saldo_actual = models.DecimalField(max_digits=12, decimal_places=2)
    moneda = models.CharField(max_length=10)

    history = HistoricalRecords()  # 👈 Historial de cambios

    def __str__(self):
        return f"{self.banco} - {self.numero_cuenta} - {self.moneda}"