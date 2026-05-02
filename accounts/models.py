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
        ('dircab_adjoint', 'Directeur de Cabinet Adjoint'),
        ('chef_cabinet', 'Chef de Cabinet'),
        ('conseiller', 'Conseiller Technique'),
        ('dg', 'Directeur Général'),
        ('charge_etudes', "Chargé d'Etudes"),
        ('point_focal', 'Point Focal Bailleur'),
        ('autre', 'Autre'),
    ]

    UNIQUE_FONCTIONS = ['ministre', 'dircab', 'dircab_adjoint', 'chef_cabinet']
    FONCTIONS_SANS_BAILLEUR = ['ministre', 'dircab', 'dircab_adjoint', 'chef_cabinet']

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

    def get_visible_bailleur_ids(self):
        """Retourne la liste des IDs de bailleurs visibles, ou None pour tout voir."""
        if self.user.is_superuser or self.is_directeur:
            return None
        if self.is_approved:
            return list(self.bailleurs.values_list('id', flat=True))
        return []


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Création'),
        ('update', 'Modification'),
        ('delete', 'Suppression'),
        ('approve', 'Approbation'),
        ('login', 'Connexion'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=50, verbose_name="Objet")
    object_repr = models.CharField(max_length=200, verbose_name="Description")
    object_id = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True, verbose_name="Détails")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Date")

    class Meta:
        verbose_name = "Journal d'activité"
        verbose_name_plural = "Journal d'activité"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} — {self.get_action_display()} {self.model_name} ({self.timestamp:%d/%m/%Y %H:%M})"

    @classmethod
    def log(cls, user, action, model_name, object_repr, object_id=None, details=''):
        cls.objects.create(
            user=user, action=action, model_name=model_name,
            object_repr=str(object_repr)[:200], object_id=object_id, details=details
        )
