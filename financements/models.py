from django.db import models
from django.urls import reverse


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
        verbose_name="Montant engagé"
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

    def __str__(self):
        return f"{self.bailleur.sigle or self.bailleur.nom} → {self.projet.code} ({self.montant_engage} {self.devise})"

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


class Decaissement(models.Model):
    financement = models.ForeignKey(
        Financement, on_delete=models.CASCADE, related_name='decaissements',
        verbose_name="Financement"
    )
    montant = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Montant décaissé"
    )
    date_decaissement = models.DateField(verbose_name="Date de décaissement")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Référence")
    description = models.TextField(blank=True, verbose_name="Description")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Décaissement"
        verbose_name_plural = "Décaissements"
        ordering = ['-date_decaissement']

    def __str__(self):
        return f"Décaissement de {self.montant} le {self.date_decaissement}"
