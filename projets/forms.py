import json
from django import forms
from .models import Projet, Secteur
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
            'code', 'titre', 'description', 'secteur', 'bailleur_principal',
            'devise', 'montant_total', 'date_signature', 'date_debut', 'date_fin_prevue',
            'date_fin_effective', 'statut', 'taux_avancement', 'zone_geographique',
            'responsable', 'objectifs_pnd',
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: PRJ-001'}),
            'titre': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'secteur': forms.Select(attrs={'class': 'form-input'}),
            'bailleur_principal': forms.Select(attrs={'class': 'form-input'}),
            'devise': forms.Select(attrs={'class': 'form-input'}),
            'montant_total': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'date_signature': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_fin_prevue': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'date_fin_effective': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'statut': forms.Select(attrs={'class': 'form-input'}),
            'taux_avancement': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0', 'max': '100'}),
            'zone_geographique': forms.TextInput(attrs={'class': 'form-input'}),
            'responsable': forms.TextInput(attrs={'class': 'form-input'}),
            'objectifs_pnd': forms.SelectMultiple(attrs={'class': 'form-input', 'size': '6'}),
        }

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
