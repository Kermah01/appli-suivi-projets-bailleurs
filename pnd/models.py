from django.db import models
from django.urls import reverse


class PlanNational(models.Model):
    nom = models.CharField(max_length=255, verbose_name="Nom du plan")
    sigle = models.CharField(max_length=50, blank=True, verbose_name="Sigle")
    annee_debut = models.PositiveIntegerField(verbose_name="Année de début")
    annee_fin = models.PositiveIntegerField(verbose_name="Année de fin")
    description = models.TextField(blank=True, verbose_name="Description")
    actif = models.BooleanField(default=True, verbose_name="Plan actif")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan National de Développement"
        verbose_name_plural = "Plans Nationaux de Développement"
        ordering = ['-annee_debut']

    def __str__(self):
        label = self.sigle if self.sigle else self.nom
        return f"{label} ({self.annee_debut}-{self.annee_fin})"

    @property
    def periode(self):
        return f"{self.annee_debut}-{self.annee_fin}"


class Pilier(models.Model):
    plan = models.ForeignKey(
        PlanNational, on_delete=models.CASCADE, related_name='piliers',
        verbose_name="Plan National"
    )
    numero = models.PositiveIntegerField(verbose_name="Numéro")
    nom = models.CharField(max_length=255, verbose_name="Intitulé du pilier")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Pilier"
        verbose_name_plural = "Piliers"
        ordering = ['plan', 'numero']
        unique_together = ['plan', 'numero']

    def __str__(self):
        return f"Pilier {self.numero} : {self.nom}"

    @property
    def nombre_projets(self):
        from projets.models import Projet
        return Projet.objects.filter(objectifs_pnd__pilier=self).distinct().count()

    @property
    def montant_total(self):
        from financements.models import Financement
        result = Financement.objects.filter(
            projet__objectifs_pnd__pilier=self
        ).distinct().aggregate(total=models.Sum('montant_engage'))
        return result['total'] or 0


class SousObjectif(models.Model):
    pilier = models.ForeignKey(
        Pilier, on_delete=models.CASCADE, related_name='sous_objectifs',
        verbose_name="Pilier"
    )
    numero = models.CharField(max_length=20, verbose_name="Numéro")
    nom = models.CharField(max_length=500, verbose_name="Intitulé")
    description = models.TextField(blank=True, verbose_name="Description")

    class Meta:
        verbose_name = "Sous-objectif"
        verbose_name_plural = "Sous-objectifs"
        ordering = ['pilier', 'numero']

    def __str__(self):
        return f"{self.numero} - {self.nom}"

    @property
    def nombre_projets(self):
        return self.projets.count()
