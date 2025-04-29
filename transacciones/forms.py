from django import forms
from .models import Transaccion
from catalogos.models import Contacto, CuentaBancaria, Proyecto, Cuentas


class TransaccionForm(forms.ModelForm):
    class Meta:
        model = Transaccion
        fields = '__all__'  # Incluir todos los campos del modelo

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        self.fields['proyecto'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_transaccion'].widget.attrs.update({'class': 'form-control'})
        self.fields['contacto'].widget.attrs.update({'class': 'form-control'})
        self.fields['forma_pago'].widget.attrs.update({'class': 'form-control'})
        self.fields['moneda'].widget.attrs.update({'class': 'form-control'})
        self.fields['cuenta_bancaria'].widget.attrs.update({'class': 'form-control'})
        self.fields['cuentas'].widget.attrs.update({'class': 'form-control'})
        self.fields['monto'].widget.attrs.update({'class': 'form-control', 'step': '0.01'})
        self.fields['detalle'].widget.attrs.update({'class': 'form-control'})
        self.fields['fecha_pago'].widget = forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        self.fields['deuda'].widget.attrs.update({'class': 'form-control'})
        self.fields['conciliado'].widget.attrs.update({'class': 'form-check-input'})
        self.fields['archivo'].widget.attrs.update({'class': 'form-control'})  # Estilo para el campo archivo

    def clean(self):
        cleaned_data = super().clean()
        forma_pago = cleaned_data.get('forma_pago')
        cuenta_bancaria = cleaned_data.get('cuenta_bancaria')
        archivo = cleaned_data.get('archivo')

        if forma_pago == 'Efectivo' and cuenta_bancaria:
            self.add_error('cuenta_bancaria', 'No puede seleccionar una cuenta bancaria cuando la forma de pago es Efectivo.')

        # Validar que el archivo sea una imagen o PDF
        if archivo:
            valid_extensions = ['pdf', 'jpg', 'jpeg', 'png']
            if not archivo.name.split('.')[-1].lower() in valid_extensions:
                self.add_error('archivo', 'Solo se permiten archivos PDF, JPG, JPEG o PNG.')

        return cleaned_data