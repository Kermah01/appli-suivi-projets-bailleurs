from functools import wraps
from urllib.parse import urlencode
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseForbidden


def login_required_custom(view_func):
    """Redirige vers la page de connexion si non authentifié."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
            login_url = '/comptes/connexion/'
            next_url = request.get_full_path()
            return redirect(f'{login_url}?{urlencode({"next": next_url})}')
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
