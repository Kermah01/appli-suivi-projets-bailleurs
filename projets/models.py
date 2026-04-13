from decimal import Decimal
from django.db import models
from django.urls import reverse

# Taux de conversion vers FCFA (XOF) — taux indicatifs
TAUX_VERS_FCFA = {
    'XOF': Decimal('1'),
    'USD': Decimal('615.00'),
    'EUR': Decimal('655.957'),
    'GBP': Decimal('775.00'),
    'JPY': Decimal('4.10'),
    'CHF': Decimal('685.00'),
    'CNY': Decimal('85.00'),
}

DEVISE_CHOICES = [
    ('USD', 'Dollar US (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('XOF', 'Franc CFA (XOF)'),
    ('GBP', 'Livre Sterling (GBP)'),
    ('JPY', 'Yen Japonais (JPY)'),
    ('CHF', 'Franc Suisse (CHF)'),
    ('CNY', 'Yuan Chinois (CNY)'),
]


def convertir_en_fcfa(montant, devise):
    """Convertit un montant d'une devise donnée en FCFA."""
    taux = TAUX_VERS_FCFA.get(devise, Decimal('1'))
    return Decimal(str(montant)) * taux


class Secteur(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom du secteur")
    code = models.CharField(max_length=20, blank=True, verbose_name="Code")
    description = models.TextField(blank=True, verbose_name="Description")
    couleur = models.CharField(max_length=7, default="#3B82F6", verbose_name="Couleur (hex)")

    class Meta:
        verbose_name = "Secteur"
        verbose_name_plural = "Secteurs"
        ordering = ['nom']

    def __str__(self):
        return self.nom

    @property
    def nombre_projets(self):
        return self.projet_set.count()


class Projet(models.Model):
    STATUT_CHOICES = [
        ('identification', 'Identification'),
        ('preparation', 'Préparation'),
        ('negociation', 'Négociation'),
        ('en_cours', 'En cours d\'exécution'),
        ('suspendu', 'Suspendu'),
        ('cloture', 'Clôturé'),
        ('annule', 'Annulé'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Code du projet")
    titre = models.CharField(max_length=500, verbose_name="Titre du projet")
    description = models.TextField(blank=True, verbose_name="Description")
    secteur = models.ForeignKey(
        Secteur, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Secteur"
    )
    bailleur_principal = models.ForeignKey(
        'bailleurs.Bailleur', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Bailleur principal"
    )
    devise = models.CharField(
        max_length=3, choices=DEVISE_CHOICES, default='USD',
        verbose_name="Devise"
    )
    montant_total = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Montant total"
    )
    date_signature = models.DateField(null=True, blank=True, verbose_name="Date de signature")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_fin_prevue = models.DateField(null=True, blank=True, verbose_name="Date de fin prévue")
    date_fin_effective = models.DateField(null=True, blank=True, verbose_name="Date de fin effective")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='identification',
        verbose_name="Statut"
    )
    taux_avancement = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux d'avancement physique (%)"
    )
    zone_geographique = models.CharField(
        max_length=255, blank=True, verbose_name="Zone géographique"
    )
    responsable = models.CharField(
        max_length=255, blank=True, verbose_name="Responsable / Chef de projet"
    )
    objectifs_pnd = models.ManyToManyField(
        'pnd.SousObjectif', blank=True, related_name='projets',
        verbose_name="Objectifs PND"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ['-date_creation']

    def __str__(self):
        return f"[{self.code}] {self.titre}"

    def get_absolute_url(self):
        return reverse('projets:detail', kwargs={'pk': self.pk})

    @property
    def taux_decaissement(self):
        if self.montant_total and self.montant_total > 0:
            from financements.models import Decaissement
            total_decaisse = Decaissement.objects.filter(
                financement__projet=self
            ).aggregate(total=models.Sum('montant'))['total'] or 0
            return round((float(total_decaisse) / float(self.montant_total)) * 100, 2)
        return 0

    @property
    def total_decaisse(self):
        from financements.models import Decaissement
        result = Decaissement.objects.filter(
            financement__projet=self
        ).aggregate(total=models.Sum('montant'))
        return result['total'] or 0

    @property
    def total_engage(self):
        """Somme des montants engagés par tous les bailleurs (via Financement)."""
        from financements.models import Financement
        result = Financement.objects.filter(projet=self).aggregate(
            total=models.Sum('montant_engage')
        )
        return result['total'] or 0

    @property
    def nombre_bailleurs(self):
        """Nombre de bailleurs distincts finançant ce projet."""
        from financements.models import Financement
        return Financement.objects.filter(projet=self).values('bailleur').distinct().count()

    @property
    def est_cofinance(self):
        """True si le projet est financé par plus d'un bailleur."""
        return self.nombre_bailleurs > 1

    @property
    def bailleurs_list(self):
        """Liste des bailleurs distincts finançant ce projet (via Financement)."""
        from bailleurs.models import Bailleur
        from financements.models import Financement
        bailleur_ids = Financement.objects.filter(projet=self).values_list('bailleur_id', flat=True).distinct()
        return Bailleur.objects.filter(id__in=bailleur_ids)

    @property
    def repartition_financements(self):
        """Répartition des financements par bailleur avec montants et pourcentages."""
        from financements.models import Financement, Decaissement
        financements = Financement.objects.filter(projet=self).select_related('bailleur')
        total = float(self.total_engage) or 1
        repartition = []
        for f in financements:
            dec = float(Decaissement.objects.filter(financement=f).aggregate(t=models.Sum('montant'))['t'] or 0)
            repartition.append({
                'bailleur': f.bailleur,
                'sigle': f.bailleur.sigle or f.bailleur.nom[:20],
                'type_financement': f.get_type_financement_display(),
                'montant_engage': float(f.montant_engage),
                'montant_decaisse': dec,
                'devise': f.devise,
                'part_pct': round(float(f.montant_engage) / total * 100, 1),
                'taux_decaissement': round(dec / float(f.montant_engage) * 100, 1) if f.montant_engage else 0,
            })
        return repartition

    @property
    def montant_total_fcfa(self):
        """Montant total converti en FCFA."""
        return convertir_en_fcfa(self.montant_total, self.devise)

    @property
    def get_devise_display_short(self):
        return self.devise

    @property
    def est_en_retard(self):
        from django.utils import timezone
        if self.date_fin_prevue and self.statut == 'en_cours':
            return self.date_fin_prevue < timezone.now().date()
        return False

    @property
    def statut_badge_class(self):
        classes = {
            'identification': 'badge-gray',
            'preparation': 'badge-orange',
            'negociation': 'badge-blue',
            'en_cours': 'badge-green',
            'suspendu': 'badge-red',
            'cloture': 'badge-purple',
            'annule': 'badge-red',
        }
        return 'badge ' + classes.get(self.statut, 'badge-gray')
