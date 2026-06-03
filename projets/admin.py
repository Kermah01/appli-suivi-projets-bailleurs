from django.contrib import admin
from .models import Secteur, Projet, CommentaireProjet


@admin.register(Secteur)
class SecteurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'code', 'nombre_projets']
    search_fields = ['nom', 'code']


class CommentaireProjetInline(admin.TabularInline):
    model = CommentaireProjet
    extra = 1
    fields = ['type_commentaire', 'niveau', 'contenu', 'date_commentaire', 'source']


@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ['code', 'titre', 'secteur', 'bailleur_principal', 'statut', 'montant_total', 'taux_avancement']
    list_filter = ['statut', 'secteur', 'bailleur_principal']
    search_fields = ['code', 'titre']
    filter_horizontal = ['objectifs_pnd']
    date_hierarchy = 'date_debut'
    inlines = [CommentaireProjetInline]


@admin.register(CommentaireProjet)
class CommentaireProjetAdmin(admin.ModelAdmin):
    list_display = ['projet', 'type_commentaire', 'niveau', 'date_commentaire', 'source', 'contenu_court']
    list_filter = ['type_commentaire', 'niveau', 'source']
    search_fields = ['projet__code', 'projet__titre', 'contenu']
    date_hierarchy = 'date_commentaire'

    def contenu_court(self, obj):
        return str(obj.contenu)[:80] + '…' if len(obj.contenu) > 80 else obj.contenu
    contenu_court.short_description = "Contenu"
