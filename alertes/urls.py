from django.urls import path
from . import views

app_name = 'alertes'

urlpatterns = [
    path('criteres/', views.criteres_liste, name='criteres'),
    path('criteres/creer/', views.critere_creer, name='critere_creer'),
    path('criteres/<int:pk>/modifier/', views.critere_modifier, name='critere_modifier'),
    path('criteres/<int:pk>/supprimer/', views.critere_supprimer, name='critere_supprimer'),
    path('criteres/<int:pk>/toggle/', views.critere_toggle, name='critere_toggle'),
]
