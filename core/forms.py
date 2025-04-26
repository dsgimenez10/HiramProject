from django import forms
from django.contrib.auth.models import User, Group

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'id': 'loginEmail',
            'class': 'form-control',
            'maxlength': '254',
            'autocomplete': 'username',
        }),
        label='Email'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'id': 'loginPassword',
            'class': 'form-control',
            'autocomplete': 'current-password',
        }),
        label='Password'
    )

# =============================================================================
# 2. Formulario para Crear Usuario (UserCreateForm)
#    - Pensado para que un admin/staff cree un usuario con username, email, is_staff
#    - Incluye password y confirm_password para validación.
# =============================================================================

class UserCreateForm(forms.ModelForm):
    """
    Formulario simplificado para crear usuarios desde un panel de administración.
    Incluye:
      - username
      - email
      - is_staff
      - password
      - confirm_password
    """
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff']

    def clean(self):
        """
        Validación:
        - Verifica que password y confirm_password coincidan.
        """
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data

    def save(self, commit=True):
        """
        Al guardar:
        - Se crea el usuario con set_password para hashear la contraseña.
        - Se guarda el user si commit=True.
        """
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


# =============================================================================
# 3. Formulario para Editar Usuario (UserAdminEditForm)
#    - Emula el comportamiento del Django Admin:
#      * Permite cambiar contraseñas sin obligar a reingresar la anterior.
#      * Permite asignar grupos y permisos directamente.
# =============================================================================

class UserAdminEditForm(forms.ModelForm):
    """Formulario para editar usuario, sin grupos/permisos en este caso."""
    new_password = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label="Confirmar contraseña",
        required=False,
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'is_active', 'is_staff', 'is_superuser',
        ]
        help_texts = {
            'username': (
                "Requerido. 150 caracteres como máximo. "
                "Únicamente letras, dígitos y @/./+/-/_"
            ),
            'is_staff': "Indica si el usuario puede entrar en este sitio de administración.",
            'is_active': "Designa si este usuario debe ser tratado como activo. "
                         "Desmarca esta opción en lugar de borrar la cuenta.",
            'is_superuser': "Concede todos los permisos disponibles.",
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password')
        p2 = cleaned_data.get('confirm_password')
        if p1 or p2:
            if p1 != p2:
                self.add_error('confirm_password', "Las contraseñas no coinciden.")
        return cleaned_data



# =============================================================================
# 4. Formulario para Crear Grupo (GroupCreateForm)
#    - Podrías extenderlo si deseas incluir permisos en el mismo formulario.
#    - De momento, está vacío o no implementado.
# =============================================================================

class GroupCreateForm(forms.ModelForm):
    """
    Placeholder para un formulario más complejo de creación de grupos,
    si en un futuro se maneja la asignación de permisos desde aquí.
    """
    class Meta:
        model = Group
        fields = ['name']
    # Podrías agregar campos para permisos (similar a la lógica de JavaScript
    # que manejas en la vista). 
    pass

    # Quitamos el widget por defecto de "permissions" para no usar su <select multiple>
    # (Si quisieras un "select" normal, podrías mantenerlo)
    class Meta:
        model = Group
        fields = ["name", "permissions"]
        # Normalmente, el admin hace un "filter_horizontal" o "filter_vertical",
        # pero aquí lo gestionaremos a mano en la plantilla.
        widgets = {
            "permissions": forms.SelectMultiple(attrs={"class": "d-none"}),  
            # 'd-none' para ocultar el <select> original, si quieres
        }