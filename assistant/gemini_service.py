"""
Service Gemini : construit le contexte DB et interroge l'IA.
Retourne une réponse structurée (texte + données pour graphiques).
"""
import json
from google import genai
from decimal import Decimal
from django.db.models import Sum, Count, Q, Avg
from django.conf import settings

from bailleurs.models import Bailleur
from projets.models import Projet, Secteur
from financements.models import Financement, Decaissement


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super().default(o)


def get_gemini_api_key(user=None):
    """
    Récupère la clé API Gemini en priorité :
    1. Configuration utilisateur (si fourni et actif)
    2. Variable d'environnement GEMINI_API_KEY
    3. None si aucune clé disponible
    """
    # Priorité 1: Clé utilisateur
    if user and hasattr(user, 'gemini_config'):
        config = user.gemini_config
        if config and config.is_active and config.api_key:
            return config.api_key

    # Priorité 2: Variable d'environnement
    return settings.GEMINI_API_KEY or None


def _build_db_context(user=None):
    """Construit un résumé des données filtré par bailleurs autorisés de l'utilisateur."""
    from dashboard.views import _get_user_bailleur_ids
    bailleur_ids = _get_user_bailleur_ids(user) if user else None

    if bailleur_ids is None:
        bailleurs = Bailleur.objects.all()
        projets = Projet.objects.select_related('bailleur_principal', 'secteur').all()
        financements = Financement.objects.select_related('projet', 'bailleur').all()
        decaissements = Decaissement.objects.select_related('financement__projet', 'financement__bailleur').all()
    else:
        bailleurs = Bailleur.objects.filter(pk__in=bailleur_ids)
        projets = Projet.objects.filter(
            Q(bailleur_principal_id__in=bailleur_ids) | Q(financements__bailleur_id__in=bailleur_ids)
        ).distinct().select_related('bailleur_principal', 'secteur')
        financements = Financement.objects.filter(bailleur_id__in=bailleur_ids).select_related('projet', 'bailleur')
        decaissements = Decaissement.objects.filter(
            financement__bailleur_id__in=bailleur_ids
        ).select_related('financement__projet', 'financement__bailleur')
    secteurs = Secteur.objects.all()

    # ── Statistiques globales ──
    total_projets = projets.count()
    total_bailleurs = bailleurs.count()
    total_engage = financements.aggregate(t=Sum('montant_engage'))['t'] or 0
    total_decaisse = decaissements.aggregate(t=Sum('montant'))['t'] or 0
    taux_global = round(float(total_decaisse) / float(total_engage) * 100, 1) if total_engage else 0

    stats = {
        'total_projets': total_projets,
        'total_bailleurs': total_bailleurs,
        'total_financements': financements.count(),
        'total_decaissements': decaissements.count(),
        'montant_total_engage': float(total_engage),
        'montant_total_decaisse': float(total_decaisse),
        'taux_decaissement_global': taux_global,
    }

    # ── Par statut ──
    par_statut = list(projets.values('statut').annotate(n=Count('id')).order_by('-n'))

    # ── Par secteur ──
    par_secteur = []
    for s in secteurs:
        nb = s.projet_set.count()
        eng = Financement.objects.filter(projet__secteur=s).aggregate(t=Sum('montant_engage'))['t'] or 0
        dec = Decaissement.objects.filter(financement__projet__secteur=s).aggregate(t=Sum('montant'))['t'] or 0
        if nb > 0:
            par_secteur.append({
                'secteur': s.nom, 'code': s.code, 'nb_projets': nb,
                'engage': float(eng), 'decaisse': float(dec),
            })

    # ── Par bailleur ──
    par_bailleur = []
    for b in bailleurs:
        nb = Financement.objects.filter(bailleur=b).values('projet').distinct().count()
        eng = Financement.objects.filter(bailleur=b).aggregate(t=Sum('montant_engage'))['t'] or 0
        dec = Decaissement.objects.filter(financement__bailleur=b).aggregate(t=Sum('montant'))['t'] or 0
        par_bailleur.append({
            'bailleur': str(b), 'sigle': b.sigle, 'type': b.get_type_bailleur_display(),
            'nb_projets': nb, 'engage': float(eng), 'decaisse': float(dec),
        })

    # ── Détail des projets ──
    detail_projets = []
    for p in projets:
        fins = Financement.objects.filter(projet=p).select_related('bailleur')
        eng = float(fins.aggregate(t=Sum('montant_engage'))['t'] or 0)
        dec = float(Decaissement.objects.filter(financement__projet=p).aggregate(t=Sum('montant'))['t'] or 0)
        bailleurs_cofin = [{'sigle': f.bailleur.sigle or f.bailleur.nom[:20], 'type_fin': f.get_type_financement_display(), 'montant': float(f.montant_engage)} for f in fins]
        detail_projets.append({
            'code': p.code, 'titre': p.titre, 'statut': p.get_statut_display(),
            'bailleur_principal': str(p.bailleur_principal) if p.bailleur_principal else '',
            'bailleurs': bailleurs_cofin,
            'est_cofinance': len(set(f.bailleur_id for f in fins)) > 1,
            'nombre_bailleurs': len(set(f.bailleur_id for f in fins)),
            'secteur': str(p.secteur) if p.secteur else '',
            'montant_total': float(p.montant_total), 'devise': p.devise,
            'date_debut': str(p.date_debut) if p.date_debut else '',
            'date_fin_prevue': str(p.date_fin_prevue) if p.date_fin_prevue else '',
            'taux_avancement': float(p.taux_avancement),
            'engage': eng, 'decaisse': dec,
            'zone': p.zone_geographique,
        })

    # ── Projets en retard ──
    from django.utils import timezone
    today = timezone.now().date()
    en_retard = projets.filter(statut='en_cours', date_fin_prevue__lt=today).count()

    context = {
        'statistiques_globales': stats,
        'projets_en_retard': en_retard,
        'repartition_par_statut': par_statut,
        'repartition_par_secteur': par_secteur,
        'repartition_par_bailleur': par_bailleur,
        'detail_projets': detail_projets,
    }

    return json.dumps(context, cls=DecimalEncoder, ensure_ascii=False, indent=1)


SYSTEM_PROMPT = """Tu es l'assistant IA de la plateforme de suivi des projets des bailleurs de fonds en Côte d'Ivoire.
Tu as accès à toutes les données de la plateforme.

RÔLE:
- Répondre aux questions sur les projets, bailleurs, financements, décaissements
- Faire des synthèses, analyses comparatives, résumés
- Proposer des visualisations quand pertinent
- Être précis et factuel, en citant les chiffres exacts de la base de données

FORMAT DE RÉPONSE:
Tu dois TOUJOURS répondre en JSON valide avec cette structure exacte:
{
  "text": "Ta réponse en markdown (utilise **gras**, tableaux, listes, etc.)",
  "chart": null ou un objet graphique,
  "table": null ou un objet tableau
}

POUR LES GRAPHIQUES (chart), utilise cette structure:
{
  "type": "bar" | "line" | "donut" | "pie" | "area" | "radialBar" | "treemap",
  "title": "Titre du graphique",
  "series": [...],
  "categories": [...],
  "colors": [...]
}

Exemples de séries selon le type:
- bar/line/area: {"series": [{"name": "Engagé", "data": [10, 20, 30]}], "categories": ["A", "B", "C"]}
- donut/pie: {"series": [10, 20, 30], "labels": ["A", "B", "C"]}
- radialBar: {"series": [75], "labels": ["Taux"]}
- treemap: {"series": [{"data": [{"x": "A", "y": 10}, {"x": "B", "y": 20}]}]}

POUR LES TABLEAUX (table), utilise cette structure:
{
  "title": "Titre du tableau",
  "headers": ["Col 1", "Col 2", ...],
  "rows": [["val1", "val2", ...], ...]
}

RÈGLES:
- Montants en format lisible (ex: "45 000 000 USD")
- Toujours citer les sources de données
- Si une question ne concerne pas les données, réponds quand même poliment
- Utilise le français
- Sois concis mais complet
- Pour les pourcentages et taux, donne des valeurs précises
- Si tu proposes un graphique, assure-toi que les données correspondent exactement à la BD
"""


MODELS_TO_TRY = [
    'gemini-2.5-flash',
    'gemini-2.0-flash',
    'gemini-2.5-flash-lite',
    'gemini-2.0-flash-lite',
]


def ask_gemini(question, conversation_history=None, user=None):
    """
    Envoie une question à Gemini avec le contexte DB filtré par l'utilisateur.
    Retourne un dict {text, chart, table}.
    Essaie plusieurs modèles en cas de quota dépassé.
    """
    import time

    api_key = get_gemini_api_key(user)
    if not api_key:
        return {
            'text': "⚠️ **Assistant IA non configuré.**\n\nVeuillez configurer votre clé API Gemini dans [les paramètres de l'assistant](/assistant/configurer/).",
            'chart': None,
            'table': None,
        }

    genai.configure(api_key=api_key)

    db_context = _build_db_context(user=user)

    # Build messages
    history_msgs = []
    if conversation_history:
        for msg in conversation_history:
            history_msgs.append({
                'role': msg['role'],
                'parts': [msg['content']],
            })

    user_msg = f"""DONNÉES ACTUELLES DE LA PLATEFORME:
{db_context}

QUESTION DE L'UTILISATEUR:
{question}"""

    last_error = None
    for model_name in MODELS_TO_TRY:
        try:
            model = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=SYSTEM_PROMPT,
            )
            chat = model.start_chat(history=history_msgs if history_msgs else [])
            response = chat.send_message(user_msg)

            # Parse response
            raw = response.text.strip()

            # Extract JSON from response (handle markdown code blocks)
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()

            try:
                result = json.loads(raw)
                if 'text' not in result:
                    result = {'text': raw, 'chart': None, 'table': None}
            except json.JSONDecodeError:
                result = {'text': raw, 'chart': None, 'table': None}

            return result

        except Exception as e:
            last_error = str(e)
            time.sleep(2)
            continue

    return {
        'text': f"⚠️ **Quota API temporairement dépassé.** Veuillez réessayer dans quelques instants.\n\nDétail : {last_error[:200]}",
        'chart': None,
        'table': None,
    }
