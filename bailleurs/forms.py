from django import forms
from .models import Bailleur


class BailleurForm(forms.ModelForm):
    class Meta:
        model = Bailleur
        fields = ['nom', 'sigle', 'type_bailleur', 'categorie_institutionnelle', 'pays_siege', 'description', 'site_web', 'contact_email']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Banque Mondiale'}),
            'sigle': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: BM'}),
            'type_bailleur': forms.Select(attrs={'class': 'form-input'}),
            'categorie_institutionnelle': forms.Select(attrs={'class': 'form-input'}),
            'pays_siege': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: États-Unis'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
            'site_web': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input'}),
        }
