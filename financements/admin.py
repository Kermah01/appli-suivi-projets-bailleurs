from django.contrib import admin
from .models import Financement, Decaissement


class DecaissementInline(admin.TabularInline):
    model = Decaissement
    extra = 1


@admin.register(Financement)
class FinancementAdmin(admin.ModelAdmin):
    list_display = ['projet', 'bailleur', 'type_financement', 'montant_engage', 'devise', 'taux_decaissement']
    list_filter = ['type_financement', 'devise', 'bailleur']
    search_fields = ['projet__titre', 'bailleur__nom']
    inlines = [DecaissementInline]


@admin.register(Decaissement)
class DecaissementAdmin(admin.ModelAdmin):
    list_display = ['financement', 'montant', 'date_decaissement', 'reference']
    list_filter = ['date_decaissement']
    date_hierarchy = 'date_decaissement'
