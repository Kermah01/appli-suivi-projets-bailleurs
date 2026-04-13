from django.urls import path
from . import views

app_name = 'pnd'

urlpatterns = [
    path('', views.index, name='index'),
    path('pilier/<int:pk>/', views.pilier_detail, name='pilier_detail'),
]
