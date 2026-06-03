import json
from django import forms
from django.utils import timezone
from .models import Projet, Secteur, Programme, PieceJointe, ResponsableLocal
from bailleurs.models import Bailleur
from financements.models import Financement


class ProjetForm(forms.ModelForm):
    # JSON field pour multi-financements (rempli par Alpine.js)
    financements_json = forms.CharField(
        widget=forms.HiddenInput(attrs={'id': 'financements_json'}),
        required=False,
    )

    class Meta:
        model = Projet
        fields = [
            'code', 'titre', 'description', 'programme', 'secteur', 'bailleur_principal',
            'devise', 'montant_total', 'part_etat_pourcentage', 'part_etat',
            'date_signature', 'date_debut', 'date_fin_prevue', 'date_fin_effective',
            'date_1er_decaissement_prevu', 'date_1er_decaissement_effectif',
            'statut', 'taux_avancement', 'taux_avancement_financier', 'taux_decaissement_prevu_annee',
            'zone_geographique', 'niveau_intervention',
            'responsable', 'responsable_email', 'responsable_telephone', 'structure_responsable',
            'motif_retard_categorie', 'motif_retard', 'objectifs_pnd',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: PRJ-001'}),
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'programme': forms.Select(attrs={'class': 'form-input'}),
            'secteur': forms.Select(attrs={'class': 'form-input'}),
            'bailleur_principal': forms.Select(attrs={'class': 'form-input'}),
            'devise': forms.Select(attrs={'class': 'form-input'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'id': 'id_montant_total'}),
            'part_etat_pourcentage': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Ex: 20.00', 'id': 'id_part_etat_pourcentage'}),
            'part_etat': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'placeholder': '0.00 (calculé auto si % renseigné)', 'id': 'id_part_etat'}),
            'date_signature': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_fin_prevue': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_fin_effective': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_1er_decaissement_prevu': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_1er_decaissement_effectif': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-input'}),
            'taux_avancement': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
            'taux_avancement_financier': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
            'taux_decaissement_prevu_annee': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100', 'placeholder': 'Ex: 25.00'}),
            'zone_geographique': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Régions séparées par des virgules'}),
            'niveau_intervention': forms.Select(attrs={'class': 'form-input'}),
            'responsable': forms.TextInput(attrs={'class': 'form-input'}),
            'responsable_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'email@structure.ci'}),
            'responsable_telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+225 XX XX XX XX XX'}),
            'structure_responsable': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Ministère de la Santé'}),
            'motif_retard_categorie': forms.Select(attrs={'class': 'form-input'}),
            'motif_retard': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Explication détaillée du retard'}),
            'objectifs_pnd': forms.SelectMultiple(attrs={'class': 'form-input', 'size': '6'}),
        }

    def clean(self):
        cleaned = super().clean()
        statut = cleaned.get('statut')
        date_fin_prevue = cleaned.get('date_fin_prevue')
        motif_cat = cleaned.get('motif_retard_categorie')
        # Si projet en cours et date fin prévue dépassée → motif obligatoire
        if statut == 'en_cours' and date_fin_prevue and date_fin_prevue < timezone.now().date():
            if not motif_cat:
                self.add_error(
                    'motif_retard_categorie',
                    "Le projet est en retard : la catégorie du motif de retard est obligatoire."
                )
        return cleaned

    def get_bailleurs_json(self):
        """Returns JSON list of bailleurs for Alpine.js component."""
        return json.dumps([
            {'id': b.id, 'label': b.sigle or b.nom[:30]}
            for b in Bailleur.objects.all().order_by('nom')
        ])

    def get_type_choices_json(self):
        """Returns JSON list of financement type choices."""
        return json.dumps([
            {'value': code, 'label': label}
            for code, label in Financement.TYPE_CHOICES
        ])


class ProgrammeForm(forms.ModelForm):
    class Meta:
        model = Programme
        fields = ['code', 'nom', 'description', 'secteur', 'date_debut', 'date_fin', 'objectif_strategique']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: PRG-001'}),
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'secteur': forms.Select(attrs={'class': 'form-input'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'objectif_strategique': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class PieceJointeForm(forms.ModelForm):
    class Meta:
        model = PieceJointe
        fields = ['titre', 'type_document', 'fichier', 'description']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Accord de financement BAD'}),
            'type_document': forms.Select(attrs={'class': 'form-input'}),
            'fichier': forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': '.pdf,.doc,.docx,.xls,.xlsx,.png,.jpg,.jpeg'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }


class ResponsableLocalForm(forms.ModelForm):
    class Meta:
        model = ResponsableLocal
        fields = ['nom', 'fonction', 'structure', 'region', 'telephone', 'email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'fonction': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Coordonnateur régional'}),
            'structure': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Direction Régionale'}),
            'region': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Bouaké'}),
            'telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+225 XX XX XX XX XX'}),
            'email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
