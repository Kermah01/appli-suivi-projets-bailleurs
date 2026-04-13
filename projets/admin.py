from django.contrib import admin
from .models import Secteur, Projet


@admin.register(Secteur)
class SecteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'nombre_projets']
    search_fields = ['nom', 'code']


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ['code', 'titre', 'secteur', 'bailleur_principal', 'statut', 'montant_total', 'taux_avancement']
    list_filter = ['statut', 'secteur', 'bailleur_principal']
    search_fields = ['code', 'titre']
    filter_horizontal = ['objectifs_pnd']
    date_hierarchy = 'date_debut'
