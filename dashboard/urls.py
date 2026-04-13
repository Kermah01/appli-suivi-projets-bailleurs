from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('api/regions-geojson/', views.regions_geojson, name='regions_geojson'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
]
