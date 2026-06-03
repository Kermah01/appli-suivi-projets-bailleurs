def user_profile(request):
    """Make user profile safely available in all templates."""
    if request.user.is_authenticated:
        profile = getattr(request.user, 'profile', None)
        is_ministre = bool(profile and profile.fonction == 'ministre' and not request.user.is_superuser)
        return {
            'user_profile': profile,
            'can_edit': request.user.is_superuser or (profile and (profile.can_edit_all or (profile.role == 'point_focal' and profile.is_approved))),
            'is_admin': request.user.is_superuser or (profile and profile.is_directeur),
            'is_ministre': is_ministre,
            'is_dircab': bool(profile and profile.fonction in ('dircab', 'dircab_adjoint')),
        }
    return {'user_profile': None, 'can_edit': False, 'is_admin': False, 'is_ministre': False, 'is_dircab': False}
