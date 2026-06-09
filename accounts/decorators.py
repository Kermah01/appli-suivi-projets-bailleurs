from functools import wraps
from urllib.parse import urlencode
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden


def login_required_custom(view_func):
    """Redirige vers la page de connexion si non authentifié, et vers pending si non approuvé."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
            login_url = '/comptes/connexion/'
            next_url = request.get_full_path()
            return redirect(f'{login_url}?{urlencode({"next": next_url})}')
        if not request.user.is_superuser:
            profile = getattr(request.user, 'profile', None)
            if not profile or not profile.is_approved:
                return redirect('accounts:pending')
        return view_func(request, *args, **kwargs)
    return wrapper


def approved_required(view_func):
    """Vérifie que l'utilisateur est authentifié ET approuvé."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_approved:
            return redirect('accounts:pending')
        return view_func(request, *args, **kwargs)
    return wrapper


def edit_permission_required(view_func):
    """Vérifie que l'utilisateur peut modifier (superadmin/directeur ou point_focal approuvé)."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_approved:
            return redirect('accounts:pending')
        if profile.role == 'lecteur':
            messages.error(request, "Vous n'avez pas la permission de modifier des données.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Réservé aux superadmin et directeurs."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_directeur:
            messages.error(request, "Accès réservé aux administrateurs.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def ministre_required(view_func):
    """Réservé au Ministre, au DirCab et aux superadmin."""
    FONCTIONS_AUTORISEES = ('ministre', 'dircab')

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = '/comptes/connexion/'
            from urllib.parse import urlencode
            return redirect(f'{login_url}?{urlencode({"next": request.get_full_path()})}')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        profile = getattr(request.user, 'profile', None)
        if not profile or not profile.is_approved:
            return redirect('accounts:pending')
        if profile.role == 'superadmin' or profile.fonction in FONCTIONS_AUTORISEES:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Cette page est réservée au Ministre, au Directeur de Cabinet et aux administrateurs.")
        return redirect('dashboard:index')
    return wrapper
