import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Projet, Secteur
from .forms import ProjetForm
from bailleurs.models import Bailleur
from financements.models import Financement, Decaissement
from accounts.decorators import login_required_custom, edit_permission_required


@login_required_custom
def liste(request):
    query = request.GET.get('q', '')
    statut_filter = request.GET.get('statut', '')
    secteur_filter = request.GET.get('secteur', '')
    bailleur_filter = request.GET.get('bailleur', '')
    projets = Projet.objects.select_related('secteur', 'bailleur_principal').prefetch_related('financements__bailleur').all()

    if query:
        projets = projets.filter(Q(titre__icontains=query) | Q(code__icontains=query))
    if statut_filter:
        projets = projets.filter(statut=statut_filter)
    if secteur_filter:
        projets = projets.filter(secteur_id=secteur_filter)
    if bailleur_filter:
        projets = projets.filter(
            Q(bailleur_principal_id=bailleur_filter) |
            Q(financements__bailleur_id=bailleur_filter)
        ).distinct()

    from bailleurs.models import Bailleur
    context = {
        'projets': projets,
        'query': query,
        'statut_filter': statut_filter,
        'secteur_filter': secteur_filter,
        'bailleur_filter': bailleur_filter,
        'statuts': Projet.STATUT_CHOICES,
        'secteurs': Secteur.objects.all(),
        'bailleurs': Bailleur.objects.all(),
    }
    return render(request, 'projets/liste.html', context)


@login_required_custom
def detail(request, pk):
    projet = get_object_or_404(
        Projet.objects.select_related('secteur', 'bailleur_principal').prefetch_related('objectifs_pnd__pilier', 'financements__bailleur', 'financements__decaissements'),
        pk=pk
    )
    context = {'projet': projet}
    return render(request, 'projets/detail.html', context)


def _create_financements_from_json(projet, financements_json_str):
    """Crée les financements à partir du JSON envoyé par le formulaire Alpine.js."""
    if not financements_json_str:
        return 0
    try:
        items = json.loads(financements_json_str)
    except (json.JSONDecodeError, TypeError):
        return 0
    count = 0
    for item in items:
        bailleur_id = item.get('bailleur_id')
        montant = item.get('montant')
        if not bailleur_id or not montant:
            continue
        try:
            bailleur = Bailleur.objects.get(pk=bailleur_id)
        except Bailleur.DoesNotExist:
            continue
        type_fin = item.get('type_financement', 'don') or 'don'
        devise = item.get('devise', projet.devise) or projet.devise
        Financement.objects.update_or_create(
            projet=projet, bailleur=bailleur, type_financement=type_fin,
            defaults={
                'montant_engage': montant,
                'devise': devise,
                'date_accord': projet.date_signature,
            }
        )
        count += 1
    return count


@edit_permission_required
def creer(request):
    bailleur_id = request.GET.get('bailleur')
    if request.method == 'POST':
        form = ProjetForm(request.POST)
        if form.is_valid():
            projet = form.save()
            _create_financements_from_json(projet, form.cleaned_data.get('financements_json'))
            messages.success(request, f'Projet "{projet.titre}" créé avec succès.')
            return redirect('projets:detail', pk=projet.pk)
    else:
        initial = {}
        if bailleur_id:
            initial['bailleur_principal'] = bailleur_id
        form = ProjetForm(initial=initial)
    return render(request, 'projets/form.html', {
        'form': form,
        'titre': 'Nouveau projet',
        'is_creation': True,
    })


@edit_permission_required
def modifier(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.can_edit_projet(projet):
        messages.error(request, "Vous n'êtes pas point focal de ce bailleur.")
        return redirect('projets:detail', pk=projet.pk)
    if request.method == 'POST':
        form = ProjetForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            messages.success(request, f'Projet "{projet.titre}" modifié avec succès.')
            return redirect('projets:detail', pk=projet.pk)
    else:
        form = ProjetForm(instance=projet)
    return render(request, 'projets/form.html', {'form': form, 'titre': f'Modifier le projet', 'projet': projet})


@edit_permission_required
def supprimer(request, pk):
    projet = get_object_or_404(Projet, pk=pk)
    profile = getattr(request.user, 'profile', None)
    if profile and not profile.can_edit_projet(projet):
        messages.error(request, "Vous n'êtes pas point focal de ce bailleur.")
        return redirect('projets:detail', pk=projet.pk)
    if request.method == 'POST':
        titre = projet.titre
        projet.delete()
        messages.success(request, f'Projet "{titre}" supprimé.')
        return redirect('projets:liste')
    return render(request, 'projets/confirmer_suppression.html', {'projet': projet})
