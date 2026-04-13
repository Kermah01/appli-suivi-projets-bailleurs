def user_profile(request):
    """Make user profile safely available in all templates."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        return {
            'user_profile': profile,
            'can_edit': profile and (profile.can_edit_all or (profile.role == 'point_focal' and profile.is_approved)),
            'is_admin': request.user.is_superuser or (profile and profile.is_directeur),
        }
    return {'user_profile': None, 'can_edit': False, 'is_admin': False}
