from django import forms
from .models import CritereRetard


class CritereRetardForm(forms.ModelForm):
    class Meta:
        model = CritereRetard
        fields = [
            'nom', 'type_critere', 'description',
            'seuil_ecart_pct', 'seuil_duree_ecoulee_pct', 'seuil_taux_decaissement_pct',
            'actif', 'ordre',
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input'}),
            'type_critere': forms.Select(attrs={'class': 'form-input', 'id': 'id_type_critere'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'seuil_ecart_pct': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0', 'max': '100'}),
            'seuil_duree_ecoulee_pct': forms.NumberInput(attrs={'class': 'form-input', 'step': '5', 'min': '0', 'max': '100'}),
            'seuil_taux_decaissement_pct': forms.NumberInput(attrs={'class': 'form-input', 'step': '5', 'min': '0', 'max': '100'}),
            'actif': forms.CheckboxInput(attrs={'class': 'rounded text-ci-orange-500'}),
            'ordre': forms.NumberInput(attrs={'class': 'form-input', 'min': '0'}),
        }
