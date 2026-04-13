from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'fonction', 'is_approved', 'date_demande', 'approved_by')
    list_filter = ('role', 'is_approved', 'fonction')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    filter_horizontal = ('bailleurs',)
    readonly_fields = ('date_demande', 'date_approbation')
    list_editable = ('is_approved', 'role')
