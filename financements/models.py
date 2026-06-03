from decimal import Decimal
from django.db import models
from django.urls import reverse

TAUX_UC_FCFA = Decimal('769.083')


class Financement(models.Model):
    TYPE_CHOICES = [
        ('don', 'Don'),
        ('pret_concessionnel', 'Prêt concessionnel'),
        ('pret_non_concessionnel', 'Prêt non concessionnel'),
        ('assistance_technique', 'Assistance technique'),
        ('cofinancement', 'Cofinancement'),
        ('contrepartie', 'Contrepartie nationale'),
        ('autre', 'Autre'),
    ]

    DEVISE_CHOICES = [
        ('USD', 'Dollar US (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('XOF', 'Franc CFA (XOF)'),
        ('GBP', 'Livre Sterling (GBP)'),
        ('JPY', 'Yen Japonais (JPY)'),
        ('CHF', 'Franc Suisse (CHF)'),
    ]

    projet = models.ForeignKey(
        'projets.Projet', on_delete=models.CASCADE, related_name='financements',
        verbose_name="Projet"
    )
    bailleur = models.ForeignKey(
        'bailleurs.Bailleur', on_delete=models.CASCADE, related_name='financements',
        verbose_name="Bailleur"
    )
    type_financement = models.CharField(
        max_length=30, choices=TYPE_CHOICES, default='don',
        verbose_name="Type de financement"
    )
    montant_engage = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Montant du financement (accord)",
        help_text="Montant total inscrit dans l'accord de financement"
    )
    montant_circuit_validation = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Montant en circuit de validation",
        help_text="Montant engagé (validé ou en cours de validation) non encore décaissé"
    )
    devise = models.CharField(
        max_length=3, choices=DEVISE_CHOICES, default='USD',
        verbose_name="Devise"
    )
    date_accord = models.DateField(null=True, blank=True, verbose_name="Date d'accord")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence accord")
    observations = models.TextField(blank=True, verbose_name="Observations")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Financement"
        verbose_name_plural = "Financements"
        ordering = ['-date_creation']

    def save(self, *args, **kwargs):
        if self.devise == 'UC':
            if self.montant_engage:
                self.montant_engage = (Decimal(str(self.montant_engage)) * TAUX_UC_FCFA).quantize(Decimal('0.01'))
            if self.montant_circuit_validation:
                self.montant_circuit_validation = (Decimal(str(self.montant_circuit_validation)) * TAUX_UC_FCFA).quantize(Decimal('0.01'))
            self.devise = 'XOF'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bailleur.sigle or self.bailleur.nom} → {self.projet.code} ({self.montant_engage} {self.devise} | circuit: {self.montant_circuit_validation})"

    @property
    def total_decaisse(self):
        result = self.decaissements.aggregate(total=models.Sum('montant'))
        return result['total'] or 0

    @property
    def taux_decaissement(self):
        if self.montant_engage and self.montant_engage > 0:
            return round((float(self.total_decaisse) / float(self.montant_engage)) * 100, 2)
        return 0

    @property
    def reste_a_decaisser(self):
        return float(self.montant_engage) - float(self.total_decaisse)

    @property
    def montant_engage_total(self):
        """Montant total engagé = décaissé + circuit de validation."""
        return float(self.total_decaisse) + float(self.montant_circuit_validation)


class Decaissement(models.Model):
    financement = models.ForeignKey(
        Financement, on_delete=models.CASCADE, related_name='decaissements',
        verbose_name="Financement"
    )
    montant = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Montant décaissé"
    )
    date_prevue = models.DateField(
        null=True, blank=True, verbose_name="Date prévisionnelle",
        help_text="Date planifiée du décaissement (suivi du pipeline)"
    )
    date_decaissement = models.DateField(verbose_name="Date de mise à jour")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Décaissement"
        verbose_name_plural = "Décaissements"
        ordering = ['-date_decaissement']

    def __str__(self):
        return f"Décaissement de {self.montant} le {self.date_decaissement}"
