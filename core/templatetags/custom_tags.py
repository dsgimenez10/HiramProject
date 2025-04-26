from django import template

register = template.Library()

@register.filter
def has_admin_access(user):
    return user.is_authenticated and user.is_staff and user.has_perm('admin.view_logentry')

@register.filter(name='addclass')
def addclass(value, arg):
    return value.as_widget(attrs={'class': arg})