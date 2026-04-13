from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('superadmin', 'Super Administrateur'),
        ('directeur', 'Directeur / Haute fonction'),
        ('point_focal', 'Point Focal Bailleur'),
        ('lecteur', 'Lecteur (consultation seule)'),
    ]

    FONCTION_CHOICES = [
        ('ministre', 'Ministre'),
        ('dircab', 'Directeur de Cabinet'),
        ('dca', 'Directeur de la Coopération et de l\'Aide'),
        ('conseiller', 'Conseiller Technique'),
        ('chef_service', 'Chef de Service'),
        ('charge_suivi', 'Chargé de Suivi'),
        ('point_focal', 'Point Focal Bailleur'),
        ('autre', 'Autre'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='point_focal', verbose_name="Rôle")
    fonction = models.CharField(max_length=30, choices=FONCTION_CHOICES, default='point_focal', verbose_name="Fonction")
    titre_poste = models.CharField(max_length=150, blank=True, verbose_name="Titre du poste")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    bailleurs = models.ManyToManyField(
        'bailleurs.Bailleur', blank=True,
        related_name='points_focaux',
        verbose_name="Bailleurs (Point focal)"
    )
    is_approved = models.BooleanField(default=False, verbose_name="Compte approuvé")
    date_demande = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='approved_users', verbose_name="Approuvé par"
    )
    date_approbation = models.DateTimeField(null=True, blank=True, verbose_name="Date d'approbation")
    notes_admin = models.TextField(blank=True, verbose_name="Notes administrateur")

    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"
        ordering = ['-date_demande']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} — {self.get_role_display()}"

    @property
    def is_superadmin(self):
        return self.role == 'superadmin' or self.user.is_superuser

    @property
    def is_directeur(self):
        return self.role in ('superadmin', 'directeur') or self.user.is_superuser

    @property
    def can_edit_all(self):
        """Superadmin et directeurs peuvent tout modifier."""
        return self.is_directeur

    def can_edit_bailleur(self, bailleur):
        """Point focal peut modifier uniquement ses bailleurs assignés."""
        if self.can_edit_all:
            return True
        if self.role == 'point_focal' and self.is_approved:
            return self.bailleurs.filter(pk=bailleur.pk).exists()
        return False

    def can_edit_projet(self, projet):
        """Vérifie si l'utilisateur peut modifier un projet."""
        if self.can_edit_all:
            return True
        if self.role == 'point_focal' and self.is_approved and projet.bailleur_principal:
            return self.bailleurs.filter(pk=projet.bailleur_principal.pk).exists()
        return False

    def can_edit_financement(self, financement):
        """Vérifie si l'utilisateur peut modifier un financement."""
        if self.can_edit_all:
            return True
        if self.role == 'point_focal' and self.is_approved:
            return self.bailleurs.filter(pk=financement.bailleur.pk).exists()
        return False
