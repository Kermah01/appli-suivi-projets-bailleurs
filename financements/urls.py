from django.urls import path
from . import views

app_name = 'financements'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('<int:pk>/', views.detail, name='detail'),
    path('nouveau/', views.creer, name='creer'),
    path('<int:pk>/modifier/', views.modifier, name='modifier'),
    path('decaissement/nouveau/<int:financement_pk>/', views.creer_decaissement, name='creer_decaissement'),
]
