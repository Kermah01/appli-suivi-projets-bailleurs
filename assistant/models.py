from django.db import models
from django.contrib.auth.models import User


class GeminiConfig(models.Model):
    """Configuration de la clé API Gemini."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='gemini_config',
        verbose_name='Utilisateur'
    )
    api_key = models.CharField(
        max_length=255,
        verbose_name='Clé API Gemini',
        help_text='Votre clé API Gemini (obtenue sur https://ai.google.dev/)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Actif'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Configuration Gemini'
        verbose_name_plural = 'Configurations Gemini'

    def __str__(self):
        return f"Config Gemini - {self.user.username}"
