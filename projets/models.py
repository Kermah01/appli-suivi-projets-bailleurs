from decimal import Decimal
from django.conf import settings
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
    'UC':  Decimal('769.083'),  # Unité de Compte BAD — bulletin mai 2026
}

DEVISE_CHOICES = [
    ('USD', 'Dollar US (USD)'),
    ('EUR', 'Euro (EUR)'),
    ('XOF', 'Franc CFA (XOF)'),
    ('UC',  'Unité de Compte BAD (UC)'),
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


class Programme(models.Model):
    """Ensemble cohérent d'interventions stratégiques regroupant plusieurs projets."""
    STATUT_CHOICES = [
        ('identification', 'Identification'),
        ('preparation', 'Préparation'),
        ('negociation', 'Négociation'),
        ('en_cours', "En cours d'exécution"),
        ('suspendu', 'Suspendu'),
        ('cloture', 'Clôturé'),
        ('annule', 'Annulé'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Code du programme")
    nom = models.CharField(max_length=500, verbose_name="Nom du programme")
    description = models.TextField(blank=True, verbose_name="Description")
    secteur = models.ForeignKey(
        Secteur, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Secteur principal"
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
        verbose_name="Montant total du programme"
    )
    date_signature = models.DateField(null=True, blank=True, verbose_name="Date de signature")
    date_debut = models.DateField(null=True, blank=True, verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin prévue")
    date_fin_effective = models.DateField(null=True, blank=True, verbose_name="Date de fin effective")
    statut = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='identification', blank=True,
        verbose_name="Statut"
    )
    taux_avancement = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux d'ex\u00e9cution physique (%)"
    )
    taux_avancement_financier = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux d'avancement financier (%)"
    )
    taux_decaissement_prevu_annee = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux de décaissement prévu annuel (%)"
    )
    zone_geographique = models.CharField(
        max_length=255, blank=True, verbose_name="Zone géographique"
    )
    responsable = models.CharField(
        max_length=255, blank=True, verbose_name="Responsable / Chef de programme"
    )
    structure_responsable = models.CharField(
        max_length=255, blank=True, verbose_name="Structure responsable"
    )
    objectif_strategique = models.TextField(blank=True, verbose_name="Objectif stratégique")
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Programme"
        verbose_name_plural = "Programmes"
        ordering = ['nom']

    def __str__(self):
        return f"[{self.code}] {self.nom}"

    def get_absolute_url(self):
        return reverse('projets:programme_detail', kwargs={'pk': self.pk})

    @property
    def nombre_projets(self):
        return self.projets.count()

    @property
    def montant_total_engage(self):
        from financements.models import Financement
        result = Financement.objects.filter(projet__programme=self).aggregate(
            total=models.Sum('montant_engage')
        )
        return result['total'] or 0

    @property
    def montant_total_decaisse(self):
        from financements.models import Decaissement
        result = Decaissement.objects.filter(financement__projet__programme=self).aggregate(
            total=models.Sum('montant')
        )
        return result['total'] or 0

    @property
    def taux_decaissement(self):
        engage = float(self.montant_total_engage or 0)
        if engage > 0:
            return round(float(self.montant_total_decaisse) / engage * 100, 2)
        return 0


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
        verbose_name="Montant total du projet (accord de financement)",
        help_text="Montant total prévu d'après l'accord de financement (budget total du projet)"
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
        verbose_name="Taux d'ex\u00e9cution physique (%)"
    )
    zone_geographique = models.CharField(
        max_length=255, blank=True, verbose_name="Zone géographique"
    )
    responsable = models.CharField(
        max_length=255, blank=True, verbose_name="Responsable / Chef de projet"
    )
    responsable_email = models.EmailField(
        blank=True, verbose_name="Email du responsable"
    )
    responsable_telephone = models.CharField(
        max_length=30, blank=True, verbose_name="Téléphone du responsable"
    )
    structure_responsable = models.CharField(
        max_length=255, blank=True, verbose_name="Structure responsable"
    )
    # Motif retard désagrégé par catégorie (CDC §5.2.1, demande CCSPPP-BAD)
    MOTIF_RETARD_CATEGORIES = [
        ('', 'Non concerné'),
        ('administratif', 'Administratif'),
        ('financier', 'Financier'),
        ('technique', 'Technique'),
        ('contextuel', 'Contextuel (sécurité, climat...)'),
        ('autre', 'Autre'),
    ]
    motif_retard_categorie = models.CharField(
        max_length=20, choices=MOTIF_RETARD_CATEGORIES, blank=True, default='',
        verbose_name="Catégorie du motif de retard",
        help_text="Obligatoire si le projet est en retard"
    )
    motif_retard = models.TextField(
        blank=True, verbose_name="Détail du motif de retard",
        help_text="Explication détaillée du retard"
    )
    # Programme stratégique de rattachement (CDC §5.2.1, demande PHAS/ANStat)
    programme = models.ForeignKey(
        Programme, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='projets', verbose_name="Programme de rattachement"
    )
    # Dates du 1er décaissement
    date_1er_decaissement_prevu = models.DateField(
        null=True, blank=True,
        verbose_name="Date prévue du 1er décaissement"
    )
    date_1er_decaissement_effectif = models.DateField(
        null=True, blank=True,
        verbose_name="Date effective du 1er décaissement"
    )
    # Part de l'État / contrepartie nationale (CDC §5.2.1, demande DSID)
    part_etat = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        verbose_name="Part de l'État — montant (contrepartie)",
        help_text="Montant de la contrepartie nationale dans la devise du projet (calculé auto si % renseigné)"
    )
    part_etat_pourcentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Part de l'État (%)",
        help_text="Pourcentage de la contrepartie nationale sur le montant total du projet"
    )
    # Taux d'avancement financier (distinct du physique, demande CCSPPP-BAD)
    taux_avancement_financier = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux d'avancement financier (%)",
        help_text="Pourcentage d'exécution financière (peut différer du taux de décaissement)"
    )
    # Niveau d'intervention géographique (CDC §5.2.1)
    NIVEAU_CHOICES = [
        ('national', 'National'),
        ('regional', 'Régional'),
        ('local', 'Local'),
    ]
    niveau_intervention = models.CharField(
        max_length=20, choices=NIVEAU_CHOICES, blank=True, default='',
        verbose_name="Niveau d'intervention"
    )
    objectifs_pnd = models.ManyToManyField(
        'pnd.SousObjectif', blank=True, related_name='projets',
        verbose_name="Objectifs PND"
    )
    taux_decaissement_prevu_annee = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        verbose_name="Taux de décaissement prévu pour l'année (%)",
        help_text="Objectif de décaissement pour l'année en cours, en % du montant total du projet"
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

    def save(self, *args, **kwargs):
        if self.devise == 'UC':
            taux_uc = TAUX_VERS_FCFA['UC']
            if self.montant_total:
                self.montant_total = (Decimal(str(self.montant_total)) * taux_uc).quantize(Decimal('0.01'))
            if self.part_etat:
                self.part_etat = (Decimal(str(self.part_etat)) * taux_uc).quantize(Decimal('0.01'))
            self.devise = 'XOF'
        if self.part_etat_pourcentage and self.part_etat_pourcentage > 0 and self.montant_total:
            self.part_etat = (Decimal(str(self.part_etat_pourcentage)) / Decimal('100')) * self.montant_total
        elif self.part_etat and self.montant_total and self.montant_total > 0 and not self.part_etat_pourcentage:
            self.part_etat_pourcentage = (self.part_etat / self.montant_total * 100).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

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
        """Répartition des financements par bailleur + part État avec montants et pourcentages."""
        from financements.models import Financement, Decaissement
        financements = Financement.objects.filter(projet=self).select_related('bailleur')
        # Base de calcul : montant total du projet (accord de financement)
        base = float(self.montant_total) if self.montant_total else (float(self.total_engage) or 1)
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
                'part_pct': round(float(f.montant_engage) / base * 100, 1),
                'taux_decaissement': round(dec / float(f.montant_engage) * 100, 1) if f.montant_engage else 0,
                'is_etat': False,
            })
        # Ajouter la part de l'État si renseignée
        if self.part_etat and self.part_etat > 0:
            repartition.append({
                'bailleur': None,
                'sigle': 'État CI',
                'type_financement': 'Contrepartie nationale',
                'montant_engage': float(self.part_etat),
                'montant_decaisse': 0,
                'devise': self.devise,
                'part_pct': round(float(self.part_etat) / base * 100, 1) if base else 0,
                'taux_decaissement': 0,
                'is_etat': True,
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
        if self.statut != 'en_cours':
            return False
        try:
            from alertes.models import CritereRetard
            criteres = list(CritereRetard.objects.filter(actif=True))
            if criteres:
                return any(c.evaluer(self) for c in criteres)
        except Exception:
            pass
        from django.utils import timezone
        return bool(self.date_fin_prevue and self.date_fin_prevue < timezone.now().date())

    @property
    def criteres_retard_actifs(self):
        """Labels des critères de retard déclenchés pour ce projet."""
        if self.statut != 'en_cours':
            return []
        try:
            from alertes.models import CritereRetard
            criteres = list(CritereRetard.objects.filter(actif=True))
            if criteres:
                return [c.get_label_declenchement(self) for c in criteres if c.evaluer(self)]
        except Exception:
            pass
        from django.utils import timezone
        if self.date_fin_prevue and self.date_fin_prevue < timezone.now().date():
            return ['Date de fin dépassée']
        return []

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

    @property
    def montant_pipeline(self):
        """Montant en circuit de validation (saisi manuellement sur chaque financement)."""
        from financements.models import Financement
        result = Financement.objects.filter(projet=self).aggregate(
            total=models.Sum('montant_circuit_validation')
        )
        return float(result['total'] or 0)

    @property
    def reste_a_decaisser(self):
        """Différence entre montant total engagé et montant décaissé (en XOF)."""
        return max(0, float(self.total_engage) - float(self.total_decaisse))

    @property
    def montant_prevu_annee(self):
        """Montant prévu à décaisser sur l'année en cours (en devise du projet)."""
        if self.montant_total and self.taux_decaissement_prevu_annee:
            return float(self.montant_total) * float(self.taux_decaissement_prevu_annee) / 100
        return 0

    @property
    def ecart_taux_annuel(self):
        """Différence en points entre taux de décaissement réel et objectif annuel."""
        return round(float(self.taux_decaissement) - float(self.taux_decaissement_prevu_annee), 2)

    @property
    def jours_depuis_modification(self):
        """Nombre de jours depuis la dernière modification (pour suivi ponctualité)."""
        from django.utils import timezone
        if self.date_modification:
            return (timezone.now() - self.date_modification).days
        return None


def piece_jointe_upload_to(instance, filename):
    return f'projets/{instance.projet_id}/pieces_jointes/{filename}'


class PieceJointe(models.Model):
    """Document joint à un projet (CDC §5.2.1, demande DSID)."""
    TYPE_CHOICES = [
        ('accord', 'Accord de financement'),
        ('rapport', "Rapport d'avancement"),
        ('pv', 'Procès-verbal de réunion'),
        ('audit', "Rapport d'audit"),
        ('autre', 'Autre document'),
    ]
    projet = models.ForeignKey(
        Projet, on_delete=models.CASCADE, related_name='pieces_jointes',
        verbose_name="Projet"
    )
    titre = models.CharField(max_length=255, verbose_name="Titre du document")
    type_document = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='autre',
        verbose_name="Type de document"
    )
    fichier = models.FileField(
        upload_to=piece_jointe_upload_to, verbose_name="Fichier"
    )
    description = models.TextField(blank=True, verbose_name="Description")
    uploaded_by = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Déposé par"
    )
    date_upload = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Pièce jointe"
        verbose_name_plural = "Pièces jointes"
        ordering = ['-date_upload']

    def __str__(self):
        return f"{self.titre} ({self.projet.code})"

    @property
    def taille_kb(self):
        try:
            return round(self.fichier.size / 1024, 1)
        except Exception:
            return 0

    @property
    def extension(self):
        import os
        return os.path.splitext(self.fichier.name)[1].lower().lstrip('.')


class ResponsableLocal(models.Model):
    """Responsable au niveau local intervenant sur un projet (CDC §5.2.1, demande DGP/DGATDRL)."""
    projet = models.ForeignKey(
        Projet, on_delete=models.CASCADE, related_name='responsables_locaux',
        verbose_name="Projet"
    )
    nom = models.CharField(max_length=255, verbose_name="Nom et prénom")
    fonction = models.CharField(max_length=255, blank=True, verbose_name="Fonction")
    structure = models.CharField(max_length=255, blank=True, verbose_name="Structure / Localité")
    region = models.CharField(max_length=100, blank=True, verbose_name="Région d'intervention")
    telephone = models.CharField(max_length=30, blank=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, verbose_name="Email")

    class Meta:
        verbose_name = "Responsable local"
        verbose_name_plural = "Responsables locaux"
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.projet.code})"


class CommentaireProjet(models.Model):
    """
    Commentaire/justification structuré sur un projet :
    retards, points d'attention, points de blocage et observations générales.
    Alimenté manuellement ou via import Excel (colonne Description/Observations).
    """
    TYPE_CHOICES = [
        ('retard',     'Justification de retard'),
        ('attention',  "Point d'attention"),
        ('blocage',    'Point de blocage'),
        ('observation','Observation générale'),
    ]
    NIVEAU_CHOICES = [
        ('critique',    'Critique'),
        ('important',   'Important'),
        ('information', 'Information'),
    ]

    projet = models.ForeignKey(
        'Projet', on_delete=models.CASCADE,
        related_name='commentaires', verbose_name="Projet"
    )
    type_commentaire = models.CharField(
        max_length=20, choices=TYPE_CHOICES, default='observation',
        verbose_name="Type"
    )
    niveau = models.CharField(
        max_length=20, choices=NIVEAU_CHOICES, default='information',
        verbose_name="Niveau"
    )
    contenu = models.TextField(verbose_name="Contenu")
    date_commentaire = models.DateField(
        null=True, blank=True, verbose_name="Date"
    )
    source = models.CharField(
        max_length=100, blank=True, default='manuel',
        verbose_name="Source", help_text="'manuel', 'import_excel', etc."
    )
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name="Auteur"
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Commentaire projet"
        verbose_name_plural = "Commentaires projets"
        ordering = ['-date_commentaire', '-date_creation']

    def __str__(self):
        return f"[{self.get_type_commentaire_display()}] {self.projet.code} — {str(self.contenu)[:60]}"
