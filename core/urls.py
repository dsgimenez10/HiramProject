from django.urls import path
from .views import login_view, dashboard_view, perfil, password_change_view, list_users, create_user, admin_user_edit_view, delete_user, list_groups, create_group_view, edit_group_view, delete_group, dashboard_data



urlpatterns = [
    path('', login_view, name='login'),
   path('dashboard/', dashboard_view, name='dashboard_view'),
    path('dashboard/data/', dashboard_data, name='dashboard_data'),  # 👈 Correcto
    path('perfil/', perfil, name='perfil'),
    path('password-change/', password_change_view, name='password_change'),
    path('miadmin/users/', list_users, name='list_users'),
    path('miadmin/users/create/', create_user, name='create_user'),
    path('miadmin/users/<int:user_id>/edit/', admin_user_edit_view, name='admin_user_edit_full'),
    path('miadmin/users/<int:user_id>/delete/', delete_user, name='delete_user'),
    path('miadmin/groups/', list_groups, name='list_groups'),
    path('miadmin/groups/create/', create_group_view, name='create_group'),
    path('miadmin/groups/<int:group_id>/edit/', edit_group_view, name='edit_group'),
    path('miadmin/groups/<int:group_id>/delete/', delete_group, name='delete_group'),
]