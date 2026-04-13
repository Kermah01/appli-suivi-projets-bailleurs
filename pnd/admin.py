from django.contrib import admin
from .models import PlanNational, Pilier, SousObjectif


class PilierInline(admin.TabularInline):
    model = Pilier
    extra = 1


class SousObjectifInline(admin.TabularInline):
    model = SousObjectif
    extra = 1


@admin.register(PlanNational)
class PlanNationalAdmin(admin.ModelAdmin):
    list_display = ['nom', 'sigle', 'annee_debut', 'annee_fin', 'actif']
    list_filter = ['actif']
    inlines = [PilierInline]


@admin.register(Pilier)
class PilierAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom', 'plan', 'nombre_projets']
    list_filter = ['plan']
    inlines = [SousObjectifInline]


@admin.register(SousObjectif)
class SousObjectifAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom', 'pilier', 'nombre_projets']
    list_filter = ['pilier__plan', 'pilier']
