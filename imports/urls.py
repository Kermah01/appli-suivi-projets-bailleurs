from django.urls import path
from . import views

app_name = 'imports'

urlpatterns = [
    path('', views.import_index, name='index'),
    path('template/', views.download_template, name='download_template'),
]
