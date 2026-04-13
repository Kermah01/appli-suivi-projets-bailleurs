from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from .forms import LoginForm, RegisterForm
from .models import UserProfile
from .decorators import login_required_custom, admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Check approval
            profile = getattr(user, 'profile', None)
            if user.is_superuser or (profile and profile.is_approved):
                messages.success(request, f'Bienvenue, {user.get_full_name() or user.username} !')
                return redirect(request.GET.get('next', 'dashboard:index'))
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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Votre compte a été créé. Il sera activé après validation par l'administrateur.")
            return redirect('accounts:login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


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
    messages.success(request, f'Le compte de {profile.user.get_full_name() or profile.user.username} a été approuvé.')
    return redirect('accounts:user_management')


@admin_required
def reject_user(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    username = profile.user.get_full_name() or profile.user.username
    profile.user.delete()
    messages.success(request, f'Le compte de {username} a été rejeté et supprimé.')
    return redirect('accounts:user_management')


@admin_required
def change_role(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in dict(UserProfile.ROLE_CHOICES):
            profile.role = new_role
            profile.save()
            messages.success(request, f'Rôle de {profile.user.get_full_name() or profile.user.username} changé en "{profile.get_role_display()}".')
    return redirect('accounts:user_management')


@admin_required
def toggle_active(request, pk):
    profile = get_object_or_404(UserProfile, pk=pk)
    user = profile.user
    if not user.is_superuser:
        profile.is_approved = not profile.is_approved
        profile.save()
        status = "approuvé" if profile.is_approved else "suspendu"
        messages.success(request, f'Compte de {user.get_full_name() or user.username} {status}.')
    return redirect('accounts:user_management')
