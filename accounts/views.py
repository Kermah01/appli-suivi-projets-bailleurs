import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from bailleurs.models import Bailleur
from .forms import LoginForm, RegisterForm
from .models import UserProfile, ActivityLog
from .decorators import login_required_custom, admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            remember_me = request.POST.get('remember_me')
            if remember_me:
                request.session.set_expiry(30 * 24 * 60 * 60)
            else:
                request.session.set_expiry(0)
            # Check approval
            profile = getattr(user, 'profile', None)
            if user.is_superuser or (profile and profile.is_approved):
                messages.success(request, f'Bienvenue, {user.get_full_name() or user.username} !')
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                # Routing par fonction
                if profile and profile.fonction in ('ministre', 'dircab', 'dircab_adjoint', 'chef_cabinet'):
                    return redirect('dashboard:ministre')
                return redirect('dashboard:index')
            else:
                return redirect('accounts:pending')
        else:
            messages.error(request, "Identifiants incorrects. Veuillez réessayer.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    # Fonctions déjà prises (approuvées, donc grisées)
    fonctions_taken = list(
        UserProfile.objects.filter(is_approved=True)
        .values_list('fonction', flat=True)
    )
    fonctions_sans_bailleur = json.dumps(UserProfile.FONCTIONS_SANS_BAILLEUR)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Votre compte a été créé. Il sera activé après validation par l'administrateur.")
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {
        'form': form,
        'fonctions_taken': fonctions_taken,
        'fonctions_sans_bailleur': fonctions_sans_bailleur,
    })


def logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('accounts:login')


@login_required_custom
def pending_view(request):
    profile = getattr(request.user, 'profile', None)
    if request.user.is_superuser or (profile and profile.is_approved):
        return redirect('dashboard:index')
    return render(request, 'accounts/pending.html')


@admin_required
def user_management_view(request):
    profiles = UserProfile.objects.select_related('user').prefetch_related('bailleurs').all()

    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')

    if status_filter == 'pending':
        profiles = profiles.filter(is_approved=False)
    elif status_filter == 'approved':
        profiles = profiles.filter(is_approved=True)

    if role_filter:
        profiles = profiles.filter(role=role_filter)

    pending_count = UserProfile.objects.filter(is_approved=False).count()

    context = {
        'profiles': profiles,
        'pending_count': pending_count,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'roles': UserProfile.ROLE_CHOICES,
    }
    return render(request, 'accounts/user_management.html', context)


@admin_required
def approve_user(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    profile.is_approved = True
    profile.approved_by = request.user
    profile.date_approbation = timezone.now()
    profile.save()
    name = profile.user.get_full_name() or profile.user.username
    ActivityLog.log(request.user, 'approve', 'Utilisateur', name, profile.pk,
                    f'Fonction: {profile.get_fonction_display()}')
    messages.success(request, f'Le compte de {name} a été approuvé.')
    return redirect('accounts:user_management')


@admin_required
def reject_user(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    name = profile.user.get_full_name() or profile.user.username
    ActivityLog.log(request.user, 'delete', 'Utilisateur', name, profile.pk, 'Compte rejeté et supprimé')
    profile.user.delete()
    messages.success(request, f'Le compte de {name} a été rejeté et supprimé.')
    return redirect('accounts:user_management')


@admin_required
def change_role(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(UserProfile.ROLE_CHOICES):
            old_role = profile.get_role_display()
            profile.role = new_role
            profile.save()
            name = profile.user.get_full_name() or profile.user.username
            ActivityLog.log(request.user, 'update', 'Utilisateur', name, profile.pk,
                            f'Rôle: {old_role} → {profile.get_role_display()}')
            messages.success(request, f'Rôle de {name} changé en "{profile.get_role_display()}".')
    return redirect('accounts:user_management')


@admin_required
def toggle_active(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    user = profile.user
    if not user.is_superuser:
        profile.is_approved = not profile.is_approved
        profile.save()
        status = "approuvé" if profile.is_approved else "suspendu"
        name = user.get_full_name() or user.username
        ActivityLog.log(request.user, 'update', 'Utilisateur', name, profile.pk, f'Compte {status}')
        messages.success(request, f'Compte de {name} {status}.')
    return redirect('accounts:user_management')


@admin_required
def edit_user(request, pk):
    profile = get_object_or_404(UserProfile.objects.select_related('user').prefetch_related('bailleurs'), pk=pk)
    user = profile.user
    if request.method == 'POST':
        # Update User fields
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        new_pw = request.POST.get('password', '').strip()
        if new_pw:
            user.set_password(new_pw)
        user.save()
        # Update Profile fields
        new_role = request.POST.get('role', profile.role)
        if new_role in dict(UserProfile.ROLE_CHOICES):
            profile.role = new_role
        new_fonction = request.POST.get('fonction', profile.fonction)
        if new_fonction in dict(UserProfile.FONCTION_CHOICES):
            profile.fonction = new_fonction
        profile.titre_poste = request.POST.get('titre_poste', profile.titre_poste)
        profile.telephone = request.POST.get('telephone', profile.telephone)
        is_approved = request.POST.get('is_approved') == '1'
        profile.is_approved = is_approved
        profile.notes_admin = request.POST.get('notes_admin', profile.notes_admin)
        profile.save()
        # Update bailleurs
        bailleur_ids = request.POST.getlist('bailleurs')
        profile.bailleurs.set(Bailleur.objects.filter(pk__in=bailleur_ids))
        ActivityLog.log(request.user, 'update', 'Utilisateur',
                        user.get_full_name() or user.username, profile.pk, 'Profil modifié par admin')
        messages.success(request, f'Profil de {user.get_full_name() or user.username} mis à jour.')
        return redirect('accounts:user_management')
    return render(request, 'accounts/edit_user.html', {
        'profile': profile,
        'all_bailleurs': Bailleur.objects.all(),
        'role_choices': UserProfile.ROLE_CHOICES,
        'fonction_choices': UserProfile.FONCTION_CHOICES,
    })


@admin_required
def audit_log_view(request):
    logs = ActivityLog.objects.select_related('user').all()[:200]
    return render(request, 'accounts/audit_log.html', {'logs': logs})
