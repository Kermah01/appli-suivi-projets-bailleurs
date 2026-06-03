from django.urls import path
from . import views

app_name = 'assistant'

urlpatterns = [
    path('', views.assistant_index, name='index'),
    path('ask/', views.assistant_ask, name='ask'),
    path('configurer/', views.configure_api_key, name='configure'),
]
