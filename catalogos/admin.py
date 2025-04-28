from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Contacto, Proyecto, Cuentas, CuentaBancaria

admin.site.register(Contacto, SimpleHistoryAdmin)
admin.site.register(Proyecto, SimpleHistoryAdmin)
admin.site.register(Cuentas, SimpleHistoryAdmin)
admin.site.register(CuentaBancaria, SimpleHistoryAdmin)
