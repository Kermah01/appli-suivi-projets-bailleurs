from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('ministre/', views.ministre_dashboard, name='ministre'),
    path('ponctualite/', views.ponctualite, name='ponctualite'),
    path('exporter-kpi/', views.exporter_kpi, name='exporter_kpi'),
    path('exporter-kpi-pdf/', views.exporter_kpi_pdf, name='exporter_kpi_pdf'),
    path('exporter-rapport-retards-pdf/', views.exporter_rapport_retards_pdf, name='exporter_rapport_retards_pdf'),
    path('api/regions-geojson/', views.regions_geojson, name='regions_geojson'),
    path('api/search/', views.api_search, name='api_search'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
]
