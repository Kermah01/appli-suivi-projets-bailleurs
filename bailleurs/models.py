from django.db import models
from django.urls import reverse


class Bailleur(models.Model):
    TYPE_CHOICES = [
        ('multilateral', 'Multilatéral'),
        ('bilateral', 'Bilatéral'),
        ('regional', 'Régional'),
        ('prive', 'Privé'),
        ('ong', 'ONG Internationale'),
        ('autre', 'Autre'),
    ]

    CATEGORIE_CHOICES = [
        ('bretton_woods', 'Institutions de Bretton Woods'),
        ('systeme_nu', 'Système des Nations Unies'),
        ('banque_multilaterale', 'Banques multilatérales de développement'),
        ('cooperation_bilaterale', 'Coopération bilatérale'),
        ('institution_regionale', 'Institutions régionales africaines'),
        ('fonds_vertical', 'Fonds verticaux / thématiques'),
        ('secteur_prive', 'Secteur privé / Fondations'),
        ('ong_internationale', 'ONG internationales'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=255, verbose_name="Nom complet")
    sigle = models.CharField(max_length=50, verbose_name="Sigle / Acronyme", blank=True)
    type_bailleur = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='multilateral',
        verbose_name="Type de bailleur"
    )
    categorie_institutionnelle = models.CharField(
        max_length=30, choices=CATEGORIE_CHOICES, default='autre',
        verbose_name="Catégorie institutionnelle", blank=True,
    )
    pays_siege = models.CharField(max_length=100, blank=True, verbose_name="Pays du siège")
    description = models.TextField(blank=True, verbose_name="Description")
    site_web = models.URLField(blank=True, verbose_name="Site web")
    contact_email = models.EmailField(blank=True, verbose_name="Email de contact")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bailleur"
        verbose_name_plural = "Bailleurs"
        ordering = ['nom']

    def __str__(self):
        if self.sigle:
            return f"{self.sigle} - {self.nom}"
        return self.nom

    def get_absolute_url(self):
        return reverse('bailleurs:detail', kwargs={'pk': self.pk})

    @property
    def nombre_projets(self):
        """Nombre de projets où ce bailleur a un financement (pas seulement bailleur_principal)."""
        from financements.models import Financement
        return Financement.objects.filter(bailleur=self).values('projet').distinct().count()

    @property
    def nombre_projets_principal(self):
        """Nombre de projets où ce bailleur est le bailleur principal."""
        return self.projet_set.count()

    @property
    def projets_finances(self):
        """Tous les projets financés par ce bailleur (via Financement)."""
        from projets.models import Projet
        from financements.models import Financement
        projet_ids = Financement.objects.filter(bailleur=self).values_list('projet_id', flat=True).distinct()
        return Projet.objects.filter(id__in=projet_ids).select_related('secteur', 'bailleur_principal')

    @property
    def montant_total_engage(self):
        from financements.models import Financement
        result = Financement.objects.filter(bailleur=self).aggregate(
            total=models.Sum('montant_engage')
        )
        return result['total'] or 0

    @property
    def montant_total_decaisse(self):
        from financements.models import Decaissement
        result = Decaissement.objects.filter(financement__bailleur=self).aggregate(
            total=models.Sum('montant')
        )
        return result['total'] or 0
