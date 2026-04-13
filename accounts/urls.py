from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('connexion/', views.login_view, name='login'),
    path('inscription/', views.register_view, name='register'),
    path('deconnexion/', views.logout_view, name='logout'),
    path('en-attente/', views.pending_view, name='pending'),
    path('utilisateurs/', views.user_management_view, name='user_management'),
    path('utilisateurs/<int:pk>/approuver/', views.approve_user, name='approve_user'),
    path('utilisateurs/<int:pk>/rejeter/', views.reject_user, name='reject_user'),
    path('utilisateurs/<int:pk>/role/', views.change_role, name='change_role'),
    path('utilisateurs/<int:pk>/toggle/', views.toggle_active, name='toggle_active'),
]
