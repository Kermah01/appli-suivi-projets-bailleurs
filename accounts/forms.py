from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from bailleurs.models import Bailleur
from .models import UserProfile


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'auth-input', 'placeholder': "Nom d'utilisateur",
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'auth-input', 'placeholder': 'Mot de passe',
        })
    )


class RegisterForm(forms.Form):
    first_name = forms.CharField(
        label="Prénom", max_length=150,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Prénom'})
    )
    last_name = forms.CharField(
        label="Nom", max_length=150,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Nom de famille'})
    )
    email = forms.EmailField(
        label="Email professionnel",
        widget=forms.EmailInput(attrs={'class': 'auth-input', 'placeholder': 'prenom.nom@ministere.gouv.ci'})
    )
    username = forms.CharField(
        label="Nom d'utilisateur", max_length=150,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': "Identifiant de connexion"})
    )
    password = forms.CharField(
        label="Mot de passe", min_length=8,
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Minimum 8 caractères'})
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'auth-input', 'placeholder': 'Répétez le mot de passe'})
    )
    fonction = forms.ChoiceField(
        label="Fonction",
        choices=UserProfile.FONCTION_CHOICES,
        widget=forms.Select(attrs={'class': 'auth-input'})
    )
    titre_poste = forms.CharField(
        label="Titre du poste", max_length=150, required=False,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': 'Ex: Chargé de programme BM'})
    )
    telephone = forms.CharField(
        label="Téléphone", max_length=30, required=False,
        widget=forms.TextInput(attrs={'class': 'auth-input', 'placeholder': '+225 XX XX XX XX XX'})
    )
    bailleurs = forms.ModelMultipleChoiceField(
        label="Bailleurs suivis",
        queryset=Bailleur.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'bailleur-checkbox'}),
        help_text="Sélectionnez les bailleurs que vous suivez."
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte existe déjà avec cet email.")
        return email

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw2 = cleaned.get('password_confirm')
        if pw and pw2 and pw != pw2:
            self.add_error('password_confirm', 'Les mots de passe ne correspondent pas.')
        # Unicité des fonctions de direction
        fonction = cleaned.get('fonction')
        if fonction in UserProfile.UNIQUE_FONCTIONS:
            exists = UserProfile.objects.filter(
                fonction=fonction, is_approved=True
            ).exists()
            if exists:
                label = dict(UserProfile.FONCTION_CHOICES).get(fonction, fonction)
                self.add_error('fonction', f'Un compte "{label}" approuvé existe déjà. Cette fonction est unique.')
        # Bailleurs obligatoires pour certaines fonctions
        if fonction and fonction not in UserProfile.FONCTIONS_SANS_BAILLEUR:
            if not cleaned.get('bailleurs'):
                self.add_error('bailleurs', 'Veuillez sélectionner au moins un bailleur pour votre fonction.')
        return cleaned

    def save(self):
        data = self.cleaned_data
        fonction = data['fonction']
        # Attribuer rôle selon fonction
        if fonction in ('ministre', 'dircab', 'dircab_adjoint', 'chef_cabinet', 'dg'):
            role = 'directeur'
        else:
            role = 'point_focal'
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            is_active=True,
        )
        profile = UserProfile.objects.create(
            user=user,
            role=role,
            fonction=fonction,
            titre_poste=data.get('titre_poste', ''),
            telephone=data.get('telephone', ''),
            is_approved=False,
        )
        if data.get('bailleurs') and fonction not in UserProfile.FONCTIONS_SANS_BAILLEUR:
            profile.bailleurs.set(data['bailleurs'])
        return user
