from django import forms
from .models import Financement, Decaissement


class FinancementForm(forms.ModelForm):
    class Meta:
        model = Financement
        fields = ['projet', 'bailleur', 'type_financement', 'montant_engage', 'devise', 'date_accord', 'reference', 'observations']
        widgets = {
            'projet': forms.Select(attrs={'class': 'form-input'}),
            'bailleur': forms.Select(attrs={'class': 'form-input'}),
            'type_financement': forms.Select(attrs={'class': 'form-input'}),
            'montant_engage': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'devise': forms.Select(attrs={'class': 'form-input'}),
            'date_accord': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-input'}),
            'observations': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }


class DecaissementForm(forms.ModelForm):
    class Meta:
        model = Decaissement
        fields = ['montant', 'date_decaissement', 'reference', 'description']
        widgets = {
            'montant': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'date_decaissement': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'reference': forms.TextInput(attrs={'class': 'form-input'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
        }
