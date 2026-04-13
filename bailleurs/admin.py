from django.contrib import admin
from .models import Bailleur


@admin.register(Bailleur)
class BailleurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'sigle', 'type_bailleur', 'pays_siege', 'nombre_projets']
    list_filter = ['type_bailleur']
    search_fields = ['nom', 'sigle']
