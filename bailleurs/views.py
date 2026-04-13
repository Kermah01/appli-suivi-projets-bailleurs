import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Bailleur
from .forms import BailleurForm
from accounts.decorators import login_required_custom, edit_permission_required


def _dec(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


@login_required_custom
def liste(request):
    query = request.GET.get('q', '')
    type_filter = request.GET.get('type', '')
    bailleurs = Bailleur.objects.all()

    if query:
        bailleurs = bailleurs.filter(Q(nom__icontains=query) | Q(sigle__icontains=query))
    if type_filter:
        bailleurs = bailleurs.filter(type_bailleur=type_filter)

    context = {
        'bailleurs': bailleurs,
        'query': query,
        'type_filter': type_filter,
        'types': Bailleur.TYPE_CHOICES,
    }
    return render(request, 'bailleurs/liste.html', context)


@login_required_custom
def detail(request, pk):
    from financements.models import Financement, Decaissement
    bailleur = get_object_or_404(Bailleur, pk=pk)
    projets = bailleur.projets_finances
    financements = bailleur.financements.select_related('projet').all()

    total_engage = float(financements.aggregate(t=Sum('montant_engage'))['t'] or 0)
    total_decaisse = float(Decaissement.objects.filter(
        financement__bailleur=bailleur
    ).aggregate(t=Sum('montant'))['t'] or 0)
    taux_dec = round((total_decaisse / total_engage * 100), 1) if total_engage > 0 else 0

    # By sector
    by_sector = {}
    for p in projets:
        s = p.secteur.nom if p.secteur else 'Non défini'
        if s not in by_sector:
            by_sector[s] = {'count': 0, 'montant': 0}
        by_sector[s]['count'] += 1
        by_sector[s]['montant'] += float(p.montant_total)

    # By status
    by_status = {}
    for p in projets:
        st = p.get_statut_display()
        by_status[st] = by_status.get(st, 0) + 1

    # By zone
    by_zone = {}
    for p in projets:
        z = p.zone_geographique or 'Non précisé'
        if z not in by_zone:
            by_zone[z] = {'count': 0, 'montant': 0}
        by_zone[z]['count'] += 1
        by_zone[z]['montant'] += float(p.montant_total)

    # Financements by type
    by_type = {}
    for f in financements:
        t = f.get_type_financement_display()
        by_type[t] = by_type.get(t, 0) + float(f.montant_engage)

    # Project list for charts
    projets_json = []
    for p in projets:
        projets_json.append({
            'id': p.id, 'code': p.code, 'titre': p.titre[:50],
            'secteur': p.secteur.nom if p.secteur else 'Non défini',
            'statut': p.get_statut_display(),
            'zone': p.zone_geographique or 'Non précisé',
            'montant': float(p.montant_total),
            'taux_avancement': float(p.taux_avancement),
            'taux_decaissement': float(p.taux_decaissement),
        })

    # CI regions for map
    ci_regions = [
        {'nom': 'Abidjan', 'lat': 5.36, 'lng': -4.0083},
        {'nom': 'Yamoussoukro', 'lat': 6.8276, 'lng': -5.2893},
        {'nom': 'Bouaké', 'lat': 7.6881, 'lng': -5.0305},
        {'nom': 'San-Pédro', 'lat': 4.7392, 'lng': -6.6363},
        {'nom': 'Daloa', 'lat': 6.8774, 'lng': -6.4502},
        {'nom': 'Korhogo', 'lat': 9.458, 'lng': -5.6292},
        {'nom': 'Man', 'lat': 7.4127, 'lng': -7.5539},
        {'nom': 'Gagnoa', 'lat': 6.1319, 'lng': -5.9506},
        {'nom': 'Bondoukou', 'lat': 8.04, 'lng': -2.8},
        {'nom': 'Soubré', 'lat': 5.7833, 'lng': -6.5833},
        {'nom': 'Ferkessédougou', 'lat': 9.5935, 'lng': -5.1986},
        {'nom': 'Dimbokro', 'lat': 6.65, 'lng': -4.7},
        {'nom': 'Odienné', 'lat': 9.5085, 'lng': -7.566},
        {'nom': 'National', 'lat': 7.54, 'lng': -5.55},
    ]

    context = {
        'bailleur': bailleur,
        'projets': projets,
        'financements': financements,
        'total_engage': total_engage,
        'total_decaisse': total_decaisse,
        'taux_dec': taux_dec,
        'taux_dec_js': json.dumps(taux_dec),
        'by_sector_json': json.dumps(by_sector, default=_dec),
        'by_status_json': json.dumps(by_status, default=_dec),
        'by_zone_json': json.dumps(by_zone, default=_dec),
        'by_type_json': json.dumps(by_type, default=_dec),
        'projets_chart_json': json.dumps(projets_json, default=_dec),
        'ci_regions_json': json.dumps(ci_regions),
    }
    return render(request, 'bailleurs/detail.html', context)


@edit_permission_required
def creer(request):
    if request.method == 'POST':
        form = BailleurForm(request.POST)
        if form.is_valid():
            bailleur = form.save()
            messages.success(request, f'Bailleur "{bailleur.nom}" créé avec succès.')
            return redirect('bailleurs:detail', pk=bailleur.pk)
    else:
        form = BailleurForm()
    return render(request, 'bailleurs/form.html', {'form': form, 'titre': 'Nouveau bailleur'})


@edit_permission_required
def modifier(request, pk):
    bailleur = get_object_or_404(Bailleur, pk=pk)
    if request.method == 'POST':
        form = BailleurForm(request.POST, instance=bailleur)
        if form.is_valid():
            form.save()
            messages.success(request, f'Bailleur "{bailleur.nom}" modifié avec succès.')
            return redirect('bailleurs:detail', pk=bailleur.pk)
    else:
        form = BailleurForm(instance=bailleur)
    return render(request, 'bailleurs/form.html', {'form': form, 'titre': f'Modifier {bailleur}', 'bailleur': bailleur})


@edit_permission_required
def supprimer(request, pk):
    bailleur = get_object_or_404(Bailleur, pk=pk)
    if request.method == 'POST':
        nom = bailleur.nom
        bailleur.delete()
        messages.success(request, f'Bailleur "{nom}" supprimé.')
        return redirect('bailleurs:liste')
    return render(request, 'bailleurs/confirmer_suppression.html', {'bailleur': bailleur})
