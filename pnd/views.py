from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Sum
from .models import PlanNational, Pilier, SousObjectif
from projets.models import Projet
from financements.models import Financement
from accounts.decorators import login_required_custom


@login_required_custom
def index(request):
    plans = PlanNational.objects.prefetch_related('piliers__sous_objectifs').all()
    plan_actif = PlanNational.objects.filter(actif=True).first()

    piliers_stats = []
    if plan_actif:
        for pilier in plan_actif.piliers.prefetch_related('sous_objectifs').all():
            nb_projets = Projet.objects.filter(objectifs_pnd__pilier=pilier).distinct().count()
            montant = Financement.objects.filter(
                projet__objectifs_pnd__pilier=pilier
            ).distinct().aggregate(total=Sum('montant_engage'))['total'] or 0
            sous_obj_stats = []
            for so in pilier.sous_objectifs.all():
                so_nb = so.projets.count()
                sous_obj_stats.append({'sous_objectif': so, 'nb_projets': so_nb})
            piliers_stats.append({
                'pilier': pilier,
                'nb_projets': nb_projets,
                'montant': montant,
                'sous_objectifs': sous_obj_stats,
            })

    context = {
        'plans': plans,
        'plan_actif': plan_actif,
        'piliers_stats': piliers_stats,
    }
    return render(request, 'pnd/index.html', context)


@login_required_custom
def pilier_detail(request, pk):
    pilier = get_object_or_404(Pilier.objects.select_related('plan').prefetch_related('sous_objectifs'), pk=pk)
    projets = Projet.objects.filter(objectifs_pnd__pilier=pilier).distinct().select_related('secteur', 'bailleur_principal')
    montant = Financement.objects.filter(
        projet__objectifs_pnd__pilier=pilier
    ).distinct().aggregate(total=Sum('montant_engage'))['total'] or 0

    context = {
        'pilier': pilier,
        'projets': projets,
        'montant_total': montant,
    }
    return render(request, 'pnd/pilier_detail.html', context)
