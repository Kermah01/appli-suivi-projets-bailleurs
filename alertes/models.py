from django.conf import settings
from django.db import models


class Alerte(models.Model):
    TYPE_CHOICES = [
        ("retard_avere", "Retard avéré"),
        ("faible_decaissement", "Faible taux de décaissement"),
        ("discordance", "Discordance physique/financier"),
        ("inactivite", "Données non mises à jour"),
        ("signalement_manuel", "Signalement manuel"),
    ]
    NIVEAU_CHOICES = [
        ("critique", "Critique"),
        ("attention", "Attention"),
        ("information", "Information"),
    ]
    STATUT_CHOICES = [
        ("active", "Active"),
        ("traitee", "Traitée"),
        ("ignoree", "Ignorée"),
    ]

    projet = models.ForeignKey(
        "projets.Projet",
        on_delete=models.CASCADE,
        related_name="alertes",
        verbose_name="Projet concerné",
    )
    type_alerte = models.CharField(
        max_length=30, choices=TYPE_CHOICES, verbose_name="Type"
    )
    niveau = models.CharField(
        max_length=20, choices=NIVEAU_CHOICES, default="attention", verbose_name="Niveau"
    )
    message = models.TextField(verbose_name="Message")
    details = models.TextField(blank=True, verbose_name="Détails")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default="active", verbose_name="Statut"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(blank=True, null=True)
    note_traitement = models.TextField(blank=True, verbose_name="Note de traitement")
    signale_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertes_signalees",
        verbose_name="Signalé par",
    )
    traite_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="alertes_traitees",
        verbose_name="Traité par",
    )

    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ["-date_creation"]

    def __str__(self):
        return f"[{self.niveau}] {self.type_alerte} — {self.projet}"


class ParametreSysteme(models.Model):
    CLE_CHOICES = [
        ("seuil_faible_decaissement", "Seuil taux de décaissement faible (%)"),
        ("seuil_discordance", "Seuil discordance physique/financier (points)"),
        ("seuil_inactivite_jours", "Délai d'inactivité avant alerte (jours)"),
    ]

    cle = models.CharField(
        max_length=50, choices=CLE_CHOICES, unique=True, verbose_name="Paramètre"
    )
    valeur = models.CharField(max_length=50, verbose_name="Valeur")
    description = models.TextField(blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    modifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Paramètre système"
        verbose_name_plural = "Paramètres système"

    def __str__(self):
        return f"{self.cle} = {self.valeur}"


class CritereRetard(models.Model):
    TYPE_CHOICES = [
        ('date_depassee', 'Date de fin prévue dépassée'),
        ('decaissement_vs_prevu', 'Taux de décaissement < Objectif annuel'),
        ('ecart_physique_financier', 'Écart avancement physique / décaissement ≥ seuil'),
        ('duree_ecoulee_taux_faible', 'Taux décaissement faible en fin de projet'),
    ]

    nom = models.CharField(max_length=200, verbose_name="Nom du critère")
    type_critere = models.CharField(
        max_length=40, choices=TYPE_CHOICES, verbose_name="Type de critère"
    )
    description = models.TextField(blank=True, verbose_name="Description")

    seuil_ecart_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=25,
        verbose_name="Écart physique/décaissement minimum (%)",
        help_text="Utilisé pour le type « Écart avancement physique / décaissement »"
    )
    seuil_duree_ecoulee_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=75,
        verbose_name="Durée écoulée minimum (%)",
        help_text="Utilisé pour le type « Durée critique » : % de la durée totale à partir duquel le critère s'active"
    )
    seuil_taux_decaissement_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=50,
        verbose_name="Taux de décaissement maximum (%)",
        help_text="Utilisé pour le type « Durée critique » : si décaissement < ce seuil → retard"
    )

    actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre = models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Critère de retard"
        verbose_name_plural = "Critères de retard"
        ordering = ['ordre', 'nom']

    def __str__(self):
        statut = "actif" if self.actif else "inactif"
        return f"{self.nom} ({statut})"

    def evaluer(self, projet):
        """Retourne True si ce critère est déclenché pour le projet donné."""
        from django.utils import timezone
        today = timezone.now().date()

        if self.type_critere == 'date_depassee':
            return bool(projet.date_fin_prevue and projet.date_fin_prevue < today)

        elif self.type_critere == 'decaissement_vs_prevu':
            return (
                float(projet.taux_decaissement_prevu_annee) > 0 and
                projet.taux_decaissement < float(projet.taux_decaissement_prevu_annee)
            )

        elif self.type_critere == 'ecart_physique_financier':
            ecart = float(projet.taux_avancement) - projet.taux_decaissement
            return ecart >= float(self.seuil_ecart_pct)

        elif self.type_critere == 'duree_ecoulee_taux_faible':
            if not projet.date_debut or not projet.date_fin_prevue:
                return False
            duree_totale = (projet.date_fin_prevue - projet.date_debut).days
            if duree_totale <= 0:
                return False
            duree_ecoulee = (today - projet.date_debut).days
            pct_ecoule = duree_ecoulee / duree_totale * 100
            return (
                pct_ecoule >= float(self.seuil_duree_ecoulee_pct) and
                projet.taux_decaissement < float(self.seuil_taux_decaissement_pct)
            )

        return False

    def get_label_declenchement(self, projet):
        """Label court expliquant pourquoi ce critère est déclenché."""
        if not self.evaluer(projet):
            return None
        if self.type_critere == 'date_depassee':
            return "Date de fin dépassée"
        elif self.type_critere == 'decaissement_vs_prevu':
            return f"Déc. {projet.taux_decaissement:.1f}% < Obj. {float(projet.taux_decaissement_prevu_annee):.1f}%"
        elif self.type_critere == 'ecart_physique_financier':
            ecart = float(projet.taux_avancement) - projet.taux_decaissement
            return f"Écart phys./fin. : {ecart:.1f}pts"
        elif self.type_critere == 'duree_ecoulee_taux_faible':
            return f"Déc. faible ({projet.taux_decaissement:.1f}%) en fin de projet"
        return self.nom
