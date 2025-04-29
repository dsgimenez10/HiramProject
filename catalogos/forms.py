from django import forms
from .models import Proyecto, Contacto, Cuentas, CuentaBancaria

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['contacto'].widget.attrs.update({'class': 'form-control'})
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['descripcion'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_inicio'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        self.fields['fecha_fin'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        self.fields['estado'].widget.attrs.update({'class': 'form-control'})
        self.fields['moneda'].widget.attrs.update({'class': 'form-control'})
        self.fields['monto'].widget.attrs.update({'class': 'form-control'})


class ContactoForm(forms.ModelForm):
    class Meta:
        model = Contacto
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo'].widget.attrs.update({'class': 'form-control'})
        self.fields['cuit'].widget.attrs.update({'class': 'form-control'})
        

class CuentasForm(forms.ModelForm):
    class Meta:
        model = Cuentas
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['nombre'].widget.attrs.update({'class': 'form-control'})

class CuentaBancariaForm(forms.ModelForm):
    class Meta:
        model = CuentaBancaria
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['numero_cuenta'].widget.attrs.update({'class': 'form-control'})
        self.fields['banco'].widget.attrs.update({'class': 'form-control'})
        self.fields['saldo_actual'].widget.attrs.update({'class': 'form-control'})
        self.fields['moneda'].widget.attrs.update({'class': 'form-control'})
