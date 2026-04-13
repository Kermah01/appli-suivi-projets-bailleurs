import json
import os
from decimal import Decimal
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from projets.models import Projet, Secteur
from bailleurs.models import Bailleur
from financements.models import Financement, Decaissement
from pnd.models import PlanNational, Pilier, SousObjectif
from accounts.decorators import login_required_custom


def _decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


@login_required_custom
def index(request):
    today = timezone.now().date()
    one_month_ago = today - timezone.timedelta(days=30)

    # ── KPIs ──
    total_projets = Projet.objects.count()
    projets_en_cours = Projet.objects.filter(statut='en_cours').count()
    projets_en_retard = Projet.objects.filter(
        statut='en_cours', date_fin_prevue__lt=today
    ).count()
    total_bailleurs = Bailleur.objects.count()

    total_engage = Financement.objects.aggregate(
        total=Sum('montant_engage')
    )['total'] or 0
    total_decaisse = Decaissement.objects.aggregate(
        total=Sum('montant')
    )['total'] or 0
    taux_decaissement_global = round(
        (float(total_decaisse) / float(total_engage) * 100), 1
    ) if total_engage > 0 else 0

    # ── Variation vs last month ──
    projets_prev = Projet.objects.filter(date_creation__lt=one_month_ago).count()
    var_projets = total_projets - projets_prev

    engage_prev = float(Financement.objects.filter(
        date_creation__lt=one_month_ago
    ).aggregate(t=Sum('montant_engage'))['t'] or 0)
    var_engage = float(total_engage) - engage_prev

    decaisse_prev = float(Decaissement.objects.filter(
        date_decaissement__lt=one_month_ago
    ).aggregate(t=Sum('montant'))['t'] or 0)
    var_decaisse = float(total_decaisse) - decaisse_prev

    retard_prev = Projet.objects.filter(
        statut='en_cours', date_fin_prevue__lt=one_month_ago
    ).count()
    var_retard = projets_en_retard - retard_prev

    # ── Raw datasets for client-side analytics engine ──

    # All bailleurs with category info
    bailleurs_list = list(
        Bailleur.objects.values('id', 'nom', 'sigle', 'type_bailleur', 'categorie_institutionnelle', 'pays_siege')
    )
    # Enrich with financials
    for b in bailleurs_list:
        b['label'] = b['sigle'] or b['nom'][:20]
        b['engage'] = float(Financement.objects.filter(bailleur_id=b['id']).aggregate(t=Sum('montant_engage'))['t'] or 0)
        b['decaisse'] = float(Decaissement.objects.filter(financement__bailleur_id=b['id']).aggregate(t=Sum('montant'))['t'] or 0)
        b['nb_projets'] = Financement.objects.filter(bailleur_id=b['id']).values('projet').distinct().count()
        # Category display
        cat_map = dict(Bailleur.CATEGORIE_CHOICES)
        b['categorie_label'] = cat_map.get(b['categorie_institutionnelle'], 'Autre')

    # All projects with denormalized fields for analytics
    projets_list = []
    for p in Projet.objects.select_related('secteur', 'bailleur_principal').all():
        projets_list.append({
            'id': p.id,
            'code': p.code,
            'titre': p.titre[:60],
            'secteur': p.secteur.nom if p.secteur else 'Non défini',
            'secteur_couleur': p.secteur.couleur if p.secteur else '#94A3B8',
            'bailleur_id': p.bailleur_principal_id,
            'bailleur': (p.bailleur_principal.sigle or p.bailleur_principal.nom[:20]) if p.bailleur_principal else 'Non défini',
            'bailleur_categorie': p.bailleur_principal.categorie_institutionnelle if p.bailleur_principal else 'autre',
            'est_cofinance': p.est_cofinance,
            'nombre_bailleurs': p.nombre_bailleurs,
            'bailleurs_list': [{'id': b.id, 'sigle': b.sigle or b.nom[:20]} for b in p.bailleurs_list],
            'statut': p.get_statut_display(),
            'statut_code': p.statut,
            'montant': float(p.montant_total),
            'devise': p.devise,
            'zone': p.zone_geographique or 'Non précisé',
            'taux_avancement': float(p.taux_avancement),
            'taux_decaissement': float(p.taux_decaissement),
            'date_debut': p.date_debut.isoformat() if p.date_debut else None,
            'date_fin_prevue': p.date_fin_prevue.isoformat() if p.date_fin_prevue else None,
            'en_retard': p.est_en_retard,
        })

    # All financements
    financements_list = list(
        Financement.objects.select_related('projet', 'bailleur').values(
            'id', 'projet__code', 'projet__titre',
            'bailleur__sigle', 'bailleur__nom', 'bailleur__categorie_institutionnelle',
            'bailleur_id',
            'type_financement', 'montant_engage', 'devise',
        )
    )
    for f in financements_list:
        f['montant_engage'] = float(f['montant_engage'])
        f['bailleur_label'] = f['bailleur__sigle'] or (f['bailleur__nom'] or '')[:20]
        dec_total = Decaissement.objects.filter(financement_id=f['id']).aggregate(t=Sum('montant'))['t'] or 0
        f['decaisse'] = float(dec_total)

    # Secteurs
    secteurs_list = list(
        Secteur.objects.annotate(nb_projets=Count('projet')).values('id', 'nom', 'couleur', 'nb_projets')
    )

    # Statut choices for filters
    statut_choices = [{'code': code, 'label': label} for code, label in Projet.STATUT_CHOICES]

    # Category choices
    categorie_choices = [{'code': code, 'label': label} for code, label in Bailleur.CATEGORIE_CHOICES]

    # Zones (unique)
    zones = sorted(set(p['zone'] for p in projets_list if p['zone'] != 'Non précisé'))

    # ── Couverture PND ──
    plan_actif = PlanNational.objects.filter(actif=True).first()
    piliers_data = []
    if plan_actif:
        for pilier in plan_actif.piliers.all():
            nb = Projet.objects.filter(objectifs_pnd__pilier=pilier).distinct().count()
            montant = Financement.objects.filter(
                projet__objectifs_pnd__pilier=pilier
            ).distinct().aggregate(total=Sum('montant_engage'))['total'] or 0
            piliers_data.append({
                'pilier': pilier,
                'nb_projets': nb,
                'montant': float(montant),
            })

    # ── Lists for tables ──
    derniers_projets = Projet.objects.select_related(
        'secteur', 'bailleur_principal'
    ).order_by('-date_creation')[:5]

    projets_retard_list = Projet.objects.filter(
        statut='en_cours', date_fin_prevue__lt=today
    ).select_related('secteur', 'bailleur_principal').order_by('date_fin_prevue')[:5]

    projets_faible_decaissement = []
    for p in Projet.objects.filter(statut='en_cours').select_related('secteur', 'bailleur_principal'):
        if p.taux_decaissement < 30 and p.montant_total > 0:
            projets_faible_decaissement.append(p)
        if len(projets_faible_decaissement) >= 5:
            break

    # ── Regions of Côte d'Ivoire for map ──
    ci_regions = [
        {'nom': 'Abidjan', 'lat': 5.3600, 'lng': -4.0083},
        {'nom': 'Yamoussoukro', 'lat': 6.8276, 'lng': -5.2893},
        {'nom': 'Bouaké', 'lat': 7.6881, 'lng': -5.0305},
        {'nom': 'San-Pédro', 'lat': 4.7392, 'lng': -6.6363},
        {'nom': 'Daloa', 'lat': 6.8774, 'lng': -6.4502},
        {'nom': 'Korhogo', 'lat': 9.4580, 'lng': -5.6292},
        {'nom': 'Man', 'lat': 7.4127, 'lng': -7.5539},
        {'nom': 'Gagnoa', 'lat': 6.1319, 'lng': -5.9506},
        {'nom': 'Odienné', 'lat': 9.5085, 'lng': -7.5660},
        {'nom': 'Bondoukou', 'lat': 8.0400, 'lng': -2.8000},
        {'nom': 'Sassandra', 'lat': 4.9500, 'lng': -6.0833},
        {'nom': 'Divo', 'lat': 5.8372, 'lng': -5.3571},
        {'nom': 'Abengourou', 'lat': 6.7297, 'lng': -3.4964},
        {'nom': 'Agboville', 'lat': 5.9282, 'lng': -4.2132},
        {'nom': 'Séguéla', 'lat': 7.9614, 'lng': -6.6731},
        {'nom': 'Dabou', 'lat': 5.3256, 'lng': -4.3767},
        {'nom': 'Grand-Bassam', 'lat': 5.2139, 'lng': -3.7340},
        {'nom': 'Ferkessédougou', 'lat': 9.5935, 'lng': -5.1986},
        {'nom': 'Dimbokro', 'lat': 6.6500, 'lng': -4.7000},
        {'nom': 'Bouaflé', 'lat': 6.9833, 'lng': -5.7500},
        {'nom': 'Issia', 'lat': 6.4900, 'lng': -6.5800},
        {'nom': 'Katiola', 'lat': 8.1400, 'lng': -5.1000},
        {'nom': 'Soubré', 'lat': 5.7833, 'lng': -6.5833},
        {'nom': 'Tingréla', 'lat': 10.4833, 'lng': -6.3833},
        {'nom': 'National', 'lat': 7.54, 'lng': -5.55},
    ]

    context = {
        'total_projets': total_projets,
        'projets_en_cours': projets_en_cours,
        'projets_en_retard': projets_en_retard,
        'total_bailleurs': total_bailleurs,
        'total_engage': total_engage,
        'total_decaisse': total_decaisse,
        'taux_decaissement_global': json.dumps(taux_decaissement_global),
        'var_projets': var_projets,
        'var_engage': var_engage,
        'var_decaisse': var_decaisse,
        'var_retard': var_retard,
        'piliers_data': piliers_data,
        'plan_actif': plan_actif,
        'derniers_projets': derniers_projets,
        'projets_retard_list': projets_retard_list,
        'projets_faible_decaissement': projets_faible_decaissement,
        # JSON datasets for analytics engine
        'projets_json': json.dumps(projets_list, default=_decimal_default),
        'bailleurs_json': json.dumps(bailleurs_list, default=_decimal_default),
        'financements_json': json.dumps(financements_list, default=_decimal_default),
        'secteurs_json': json.dumps(secteurs_list, default=_decimal_default),
        'statut_choices_json': json.dumps(statut_choices),
        'categorie_choices_json': json.dumps(categorie_choices),
        'zones_json': json.dumps(zones),
        'ci_regions_json': json.dumps(ci_regions),
    }
    return render(request, 'dashboard/index.html', context)


@login_required_custom
def regions_geojson(request):
    filepath = os.path.join(settings.BASE_DIR, 'static', 'data', 'regions.geojson')
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    response = JsonResponse(data, json_dumps_params={'ensure_ascii': False})
    response['Cache-Control'] = 'public, max-age=86400'
    return response


@login_required_custom
def api_search(request):
    """Global search across projets, bailleurs, financements."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    results = []

    # Search projets
    for p in Projet.objects.filter(
        Q(code__icontains=q) | Q(titre__icontains=q)
    ).select_related('bailleur_principal', 'secteur')[:8]:
        results.append({
            'type': 'projet',
            'icon': 'folder_open',
            'label': f'[{p.code}] {p.titre[:60]}',
            'sub': p.bailleur_principal.sigle if p.bailleur_principal else '',
            'url': f'/projets/{p.pk}/',
        })

    # Search bailleurs
    for b in Bailleur.objects.filter(
        Q(nom__icontains=q) | Q(sigle__icontains=q)
    )[:5]:
        results.append({
            'type': 'bailleur',
            'icon': 'account_balance',
            'label': b.nom,
            'sub': b.get_type_bailleur_display(),
            'url': f'/bailleurs/{b.pk}/',
        })

    # Search financements by project code or bailleur
    for f in Financement.objects.filter(
        Q(projet__code__icontains=q) | Q(bailleur__sigle__icontains=q) | Q(reference__icontains=q)
    ).select_related('projet', 'bailleur')[:5]:
        results.append({
            'type': 'financement',
            'icon': 'payments',
            'label': f'{f.bailleur.sigle or f.bailleur.nom[:20]} → {f.projet.code}',
            'sub': f.get_type_financement_display(),
            'url': f'/financements/{f.pk}/',
        })

    return JsonResponse({'results': results[:15]})


@login_required_custom
def api_notifications(request):
    """Return actionable notifications/alerts."""
    today = timezone.now().date()
    notifs = []

    # Projects en retard
    retards = Projet.objects.filter(
        statut='en_cours', date_fin_prevue__lt=today
    ).select_related('bailleur_principal').order_by('date_fin_prevue')[:5]
    for p in retards:
        days_late = (today - p.date_fin_prevue).days
        notifs.append({
            'type': 'warning',
            'icon': 'warning',
            'title': f'{p.code} en retard',
            'message': f'{days_late}j de retard — fin prévue {p.date_fin_prevue.strftime("%d/%m/%Y")}',
            'url': f'/projets/{p.pk}/',
            'time': f'{days_late}j',
        })

    # Low disbursement projects
    for p in Projet.objects.filter(statut='en_cours').select_related('bailleur_principal'):
        if p.taux_decaissement < 20 and float(p.montant_total) > 0:
            notifs.append({
                'type': 'alert',
                'icon': 'trending_down',
                'title': f'{p.code} — décaissement faible',
                'message': f'Taux de décaissement: {p.taux_decaissement}%',
                'url': f'/projets/{p.pk}/',
                'time': '',
            })
        if len(notifs) >= 10:
            break

    # Recent projects (last 7 days)
    recent = Projet.objects.filter(
        date_creation__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-date_creation')[:3]
    for p in recent:
        days_ago = (today - p.date_creation.date()).days
        notifs.append({
            'type': 'info',
            'icon': 'add_circle',
            'title': f'Nouveau projet: {p.code}',
            'message': p.titre[:50],
            'url': f'/projets/{p.pk}/',
            'time': f'{days_ago}j' if days_ago > 0 else "Aujourd'hui",
        })

    return JsonResponse({'notifications': notifs[:10], 'count': len(notifs)})
