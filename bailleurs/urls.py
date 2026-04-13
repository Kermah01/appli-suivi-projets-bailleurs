from django.urls import path
from . import views

app_name = 'bailleurs'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('<int:pk>/', views.detail, name='detail'),
    path('nouveau/', views.creer, name='creer'),
    path('<int:pk>/modifier/', views.modifier, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer, name='supprimer'),
]
