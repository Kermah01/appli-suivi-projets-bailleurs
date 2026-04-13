"""
Moteur d'import intelligent : parse un Excel, détecte créations/mises à jour,
et exécute l'import avec un rapport détaillé.
"""
import openpyxl
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from collections import OrderedDict

from bailleurs.models import Bailleur
from projets.models import Secteur, Projet
from financements.models import Financement, Decaissement


# ── Mappings label → valeur DB ─────────────────────────────────────
TYPE_BAILLEUR_MAP = {
    'multilatéral': 'multilateral', 'multilateral': 'multilateral',
    'bilatéral': 'bilateral', 'bilateral': 'bilateral',
    'régional': 'regional', 'regional': 'regional',
    'privé': 'prive', 'prive': 'prive',
    'ong internationale': 'ong',
    'autre': 'autre',
}

CATEGORIE_MAP = {
    'institutions de bretton woods': 'bretton_woods',
    'système des nations unies': 'systeme_nu',
    'banques multilatérales de développement': 'banque_multilaterale',
    'coopération bilatérale': 'cooperation_bilaterale',
    'institutions régionales africaines': 'institution_regionale',
    'fonds verticaux / thématiques': 'fonds_vertical',
    'secteur privé / fondations': 'secteur_prive',
    'ong internationales': 'ong_internationale',
    'autre': 'autre',
}

STATUT_MAP = {
    'identification': 'identification',
    'préparation': 'preparation', 'preparation': 'preparation',
    'négociation': 'negociation', 'negociation': 'negociation',
    "en cours d'exécution": 'en_cours', 'en cours': 'en_cours', 'en_cours': 'en_cours',
    'suspendu': 'suspendu',
    'clôturé': 'cloture', 'cloture': 'cloture',
    'annulé': 'annule', 'annule': 'annule',
}

TYPE_FIN_MAP = {
    'don': 'don',
    'prêt concessionnel': 'pret_concessionnel', 'pret concessionnel': 'pret_concessionnel',
    'prêt non concessionnel': 'pret_non_concessionnel', 'pret non concessionnel': 'pret_non_concessionnel',
    'assistance technique': 'assistance_technique',
    'cofinancement': 'cofinancement',
    'contrepartie nationale': 'contrepartie',
    'autre': 'autre',
}


def _clean(val):
    """Nettoie une valeur de cellule."""
    if val is None:
        return ''
    if isinstance(val, str):
        return val.strip()
    return val


def _to_str(val):
    v = _clean(val)
    return str(v) if v != '' else ''


def _to_decimal(val):
    v = _clean(val)
    if v == '' or v is None:
        return Decimal('0')
    try:
        return Decimal(str(v).replace(',', '.').replace(' ', ''))
    except (InvalidOperation, ValueError):
        return None


def _to_date(val):
    v = _clean(val)
    if not v:
        return None
    if isinstance(v, (date, datetime)):
        return v if isinstance(v, date) and not isinstance(v, datetime) else v.date() if isinstance(v, datetime) else v
    try:
        return datetime.strptime(str(v)[:10], '%Y-%m-%d').date()
    except (ValueError, TypeError):
        try:
            return datetime.strptime(str(v)[:10], '%d/%m/%Y').date()
        except (ValueError, TypeError):
            return None


def _read_sheet(ws, header_row=4, data_start=5):
    """Lit une feuille à partir de header_row et retourne une liste de dicts."""
    rows_data = []
    headers = []
    for cell in ws[header_row]:
        h = _clean(cell.value)
        if h:
            headers.append(h.replace(' *', '').strip())
        else:
            headers.append(f'col_{cell.column}')

    for row in ws.iter_rows(min_row=data_start, values_only=True):
        if all(v is None or str(v).strip() == '' for v in row):
            continue
        row_dict = {}
        for i, v in enumerate(row):
            if i < len(headers):
                row_dict[headers[i]] = _clean(v)
        rows_data.append(row_dict)
    return rows_data


# ── ANALYSE (preview sans écriture) ───────────────────────────────

def analyze_file(file_obj):
    """
    Analyse un fichier Excel et retourne un rapport de preview.
    Retourne: {
        'bailleurs': {'create': [...], 'update': [...], 'skip': [...], 'errors': [...]},
        'projets': {...},
        'financements': {...},
        'decaissements': {...},
        'summary': {...}
    }
    """
    wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    report = OrderedDict()

    # ── Bailleurs ──
    if 'Bailleurs' in wb.sheetnames:
        report['bailleurs'] = _analyze_bailleurs(wb['Bailleurs'])
    else:
        report['bailleurs'] = {'create': [], 'update': [], 'skip': [], 'errors': []}

    # ── Projets ──
    if 'Projets' in wb.sheetnames:
        report['projets'] = _analyze_projets(wb['Projets'])
    else:
        report['projets'] = {'create': [], 'update': [], 'skip': [], 'errors': []}

    # ── Financements ──
    if 'Financements' in wb.sheetnames:
        report['financements'] = _analyze_financements(wb['Financements'])
    else:
        report['financements'] = {'create': [], 'update': [], 'skip': [], 'errors': []}

    # ── Décaissements ──
    if 'Décaissements' in wb.sheetnames:
        report['decaissements'] = _analyze_decaissements(wb['Décaissements'])
    else:
        report['decaissements'] = {'create': [], 'update': [], 'skip': [], 'errors': []}

    # Summary
    report['summary'] = {
        'total_create': sum(len(v['create']) for v in report.values() if isinstance(v, dict) and 'create' in v),
        'total_update': sum(len(v['update']) for v in report.values() if isinstance(v, dict) and 'update' in v),
        'total_errors': sum(len(v['errors']) for v in report.values() if isinstance(v, dict) and 'errors' in v),
    }

    wb.close()
    return report


def _analyze_bailleurs(ws):
    rows = _read_sheet(ws)
    result = {'create': [], 'update': [], 'skip': [], 'errors': []}

    for i, row in enumerate(rows, 5):
        sigle = _to_str(row.get('Sigle', ''))
        nom = _to_str(row.get('Nom complet', ''))

        if not sigle:
            result['errors'].append(f"Ligne {i}: Sigle manquant")
            continue
        if not nom:
            result['errors'].append(f"Ligne {i}: Nom complet manquant")
            continue

        existing = Bailleur.objects.filter(sigle__iexact=sigle).first()
        info = f"{sigle} - {nom}"
        if existing:
            result['update'].append({'line': i, 'info': info, 'detail': f"Mise à jour de '{existing.nom}'"})
        else:
            result['create'].append({'line': i, 'info': info})

    return result


def _analyze_projets(ws):
    rows = _read_sheet(ws)
    result = {'create': [], 'update': [], 'skip': [], 'errors': []}

    for i, row in enumerate(rows, 5):
        code = _to_str(row.get('Code projet', ''))
        titre = _to_str(row.get('Titre', ''))

        if not code:
            result['errors'].append(f"Ligne {i}: Code projet manquant")
            continue
        if not titre:
            result['errors'].append(f"Ligne {i}: Titre manquant")
            continue

        bailleur_sigle = _to_str(row.get('Bailleur principal (sigle)', ''))
        if bailleur_sigle and not Bailleur.objects.filter(sigle__iexact=bailleur_sigle).exists():
            result['errors'].append(f"Ligne {i}: Bailleur '{bailleur_sigle}' introuvable")
            continue

        secteur_code = _to_str(row.get('Secteur (code)', ''))
        if secteur_code and not Secteur.objects.filter(code__iexact=secteur_code).exists():
            result['errors'].append(f"Ligne {i}: Secteur '{secteur_code}' introuvable")
            continue

        montant = _to_decimal(row.get('Montant total', 0))
        if montant is None:
            result['errors'].append(f"Ligne {i}: Montant total invalide")
            continue

        existing = Projet.objects.filter(code__iexact=code).first()
        info = f"[{code}] {titre}"
        if existing:
            result['update'].append({'line': i, 'info': info, 'detail': f"Mise à jour de '{existing.titre}'"})
        else:
            result['create'].append({'line': i, 'info': info})

    return result


def _analyze_financements(ws):
    rows = _read_sheet(ws)
    result = {'create': [], 'update': [], 'skip': [], 'errors': []}

    for i, row in enumerate(rows, 5):
        code_projet = _to_str(row.get('Code projet', ''))
        sigle_bailleur = _to_str(row.get('Sigle bailleur', ''))

        if not code_projet:
            result['errors'].append(f"Ligne {i}: Code projet manquant")
            continue
        if not sigle_bailleur:
            result['errors'].append(f"Ligne {i}: Sigle bailleur manquant")
            continue

        projet = Projet.objects.filter(code__iexact=code_projet).first()
        if not projet:
            result['errors'].append(f"Ligne {i}: Projet '{code_projet}' introuvable")
            continue

        bailleur = Bailleur.objects.filter(sigle__iexact=sigle_bailleur).first()
        if not bailleur:
            result['errors'].append(f"Ligne {i}: Bailleur '{sigle_bailleur}' introuvable")
            continue

        montant = _to_decimal(row.get('Montant engagé', 0))
        if montant is None:
            result['errors'].append(f"Ligne {i}: Montant engagé invalide")
            continue

        type_raw = _to_str(row.get('Type de financement', '')).lower()
        type_fin = TYPE_FIN_MAP.get(type_raw, 'don')
        existing = Financement.objects.filter(projet=projet, bailleur=bailleur, type_financement=type_fin).first()
        info = f"{sigle_bailleur} → {code_projet} ({montant:,.0f})"
        if existing:
            result['update'].append({'line': i, 'info': info, 'detail': f"Montant {existing.montant_engage:,.0f} → {montant:,.0f}"})
        else:
            result['create'].append({'line': i, 'info': info})

    return result


def _analyze_decaissements(ws):
    rows = _read_sheet(ws)
    result = {'create': [], 'update': [], 'skip': [], 'errors': []}

    for i, row in enumerate(rows, 5):
        code_projet = _to_str(row.get('Code projet', ''))
        sigle_bailleur = _to_str(row.get('Sigle bailleur', ''))
        montant = _to_decimal(row.get('Montant décaissé', 0))
        date_dec = _to_date(row.get('Date de décaissement', ''))
        reference = _to_str(row.get('Référence', ''))

        if not code_projet:
            result['errors'].append(f"Ligne {i}: Code projet manquant")
            continue
        if montant is None or montant == 0:
            result['errors'].append(f"Ligne {i}: Montant décaissé invalide ou nul")
            continue
        if not date_dec:
            result['errors'].append(f"Ligne {i}: Date de décaissement manquante ou invalide")
            continue

        projet = Projet.objects.filter(code__iexact=code_projet).first()
        if not projet:
            result['errors'].append(f"Ligne {i}: Projet '{code_projet}' introuvable")
            continue

        bailleur = Bailleur.objects.filter(sigle__iexact=sigle_bailleur).first()
        if not bailleur:
            result['errors'].append(f"Ligne {i}: Bailleur '{sigle_bailleur}' introuvable")
            continue

        financement = Financement.objects.filter(projet=projet, bailleur=bailleur).first()
        if not financement:
            result['errors'].append(f"Ligne {i}: Aucun financement {sigle_bailleur} → {code_projet}")
            continue

        # Check if decaissement exists by reference + date
        existing = None
        if reference:
            existing = Decaissement.objects.filter(
                financement=financement, reference=reference, date_decaissement=date_dec
            ).first()

        info = f"{code_projet} | {montant:,.0f} | {date_dec}"
        if existing:
            result['update'].append({'line': i, 'info': info, 'detail': f"Montant {existing.montant:,.0f} → {montant:,.0f}"})
        else:
            result['create'].append({'line': i, 'info': info})

    return result


# ── EXÉCUTION (écriture en base) ──────────────────────────────────

def execute_import(file_obj):
    """
    Exécute l'import et retourne un rapport avec les compteurs.
    """
    wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
    counts = OrderedDict([
        ('bailleurs', {'created': 0, 'updated': 0, 'errors': []}),
        ('projets', {'created': 0, 'updated': 0, 'errors': []}),
        ('financements', {'created': 0, 'updated': 0, 'errors': []}),
        ('decaissements', {'created': 0, 'updated': 0, 'errors': []}),
    ])

    # Import dans l'ordre: Bailleurs → Projets → Financements → Décaissements
    if 'Bailleurs' in wb.sheetnames:
        _import_bailleurs(wb['Bailleurs'], counts['bailleurs'])

    if 'Projets' in wb.sheetnames:
        _import_projets(wb['Projets'], counts['projets'])

    if 'Financements' in wb.sheetnames:
        _import_financements(wb['Financements'], counts['financements'])

    if 'Décaissements' in wb.sheetnames:
        _import_decaissements(wb['Décaissements'], counts['decaissements'])

    wb.close()
    return counts


def _import_bailleurs(ws, counts):
    rows = _read_sheet(ws)
    for i, row in enumerate(rows, 5):
        try:
            sigle = _to_str(row.get('Sigle', ''))
            nom = _to_str(row.get('Nom complet', ''))
            if not sigle or not nom:
                continue

            type_raw = _to_str(row.get('Type de bailleur', '')).lower()
            cat_raw = _to_str(row.get('Catégorie institutionnelle', '')).lower()

            defaults = {
                'nom': nom,
                'type_bailleur': TYPE_BAILLEUR_MAP.get(type_raw, 'autre'),
                'categorie_institutionnelle': CATEGORIE_MAP.get(cat_raw, ''),
                'pays_siege': _to_str(row.get('Pays du siège', '')),
                'description': _to_str(row.get('Description', '')),
                'site_web': _to_str(row.get('Site web', '')),
                'contact_email': _to_str(row.get('Email de contact', '')),
            }

            obj, created = Bailleur.objects.update_or_create(
                sigle__iexact=sigle,
                defaults={**defaults, 'sigle': sigle}
            )

            if created:
                counts['created'] += 1
            else:
                counts['updated'] += 1

        except Exception as e:
            counts['errors'].append(f"Ligne {i}: {str(e)}")


def _import_projets(ws, counts):
    rows = _read_sheet(ws)
    for i, row in enumerate(rows, 5):
        try:
            code = _to_str(row.get('Code projet', ''))
            titre = _to_str(row.get('Titre', ''))
            if not code or not titre:
                continue

            bailleur_sigle = _to_str(row.get('Bailleur principal (sigle)', ''))
            bailleur = Bailleur.objects.filter(sigle__iexact=bailleur_sigle).first() if bailleur_sigle else None

            secteur_code = _to_str(row.get('Secteur (code)', ''))
            secteur = Secteur.objects.filter(code__iexact=secteur_code).first() if secteur_code else None

            statut_raw = _to_str(row.get('Statut', '')).lower()
            montant = _to_decimal(row.get('Montant total', 0)) or Decimal('0')
            taux = _to_decimal(row.get("Taux d'avancement (%)", 0)) or Decimal('0')

            defaults = {
                'titre': titre,
                'description': _to_str(row.get('Description', '')),
                'secteur': secteur,
                'bailleur_principal': bailleur,
                'devise': _to_str(row.get('Devise', 'USD')) or 'USD',
                'montant_total': montant,
                'date_signature': _to_date(row.get('Date de signature', '')),
                'date_debut': _to_date(row.get('Date de début', '')),
                'date_fin_prevue': _to_date(row.get('Date de fin prévue', '')),
                'statut': STATUT_MAP.get(statut_raw, 'identification'),
                'taux_avancement': taux,
                'zone_geographique': _to_str(row.get('Zone géographique', '')),
                'responsable': _to_str(row.get('Responsable', '')),
            }

            obj, created = Projet.objects.update_or_create(
                code__iexact=code,
                defaults={**defaults, 'code': code}
            )

            if created:
                counts['created'] += 1
            else:
                counts['updated'] += 1

        except Exception as e:
            counts['errors'].append(f"Ligne {i}: {str(e)}")


def _import_financements(ws, counts):
    rows = _read_sheet(ws)
    for i, row in enumerate(rows, 5):
        try:
            code_projet = _to_str(row.get('Code projet', ''))
            sigle_bailleur = _to_str(row.get('Sigle bailleur', ''))
            if not code_projet or not sigle_bailleur:
                continue

            projet = Projet.objects.filter(code__iexact=code_projet).first()
            bailleur = Bailleur.objects.filter(sigle__iexact=sigle_bailleur).first()
            if not projet or not bailleur:
                counts['errors'].append(f"Ligne {i}: Projet ou bailleur introuvable")
                continue

            type_raw = _to_str(row.get('Type de financement', '')).lower()
            montant = _to_decimal(row.get('Montant engagé', 0)) or Decimal('0')

            defaults = {
                'type_financement': TYPE_FIN_MAP.get(type_raw, 'don'),
                'montant_engage': montant,
                'devise': _to_str(row.get('Devise', 'USD')) or 'USD',
                'date_accord': _to_date(row.get("Date d'accord", '')),
                'reference': _to_str(row.get('Référence accord', '')),
                'observations': _to_str(row.get('Observations', '')),
            }

            obj, created = Financement.objects.update_or_create(
                projet=projet, bailleur=bailleur,
                type_financement=defaults.pop('type_financement', 'don'),
                defaults=defaults
            )

            if created:
                counts['created'] += 1
            else:
                counts['updated'] += 1

        except Exception as e:
            counts['errors'].append(f"Ligne {i}: {str(e)}")


def _import_decaissements(ws, counts):
    rows = _read_sheet(ws)
    for i, row in enumerate(rows, 5):
        try:
            code_projet = _to_str(row.get('Code projet', ''))
            sigle_bailleur = _to_str(row.get('Sigle bailleur', ''))
            montant = _to_decimal(row.get('Montant décaissé', 0))
            date_dec = _to_date(row.get('Date de décaissement', ''))
            reference = _to_str(row.get('Référence', ''))
            description = _to_str(row.get('Description', ''))

            if not code_projet or not montant or not date_dec:
                continue

            projet = Projet.objects.filter(code__iexact=code_projet).first()
            bailleur = Bailleur.objects.filter(sigle__iexact=sigle_bailleur).first()
            if not projet or not bailleur:
                counts['errors'].append(f"Ligne {i}: Projet ou bailleur introuvable")
                continue

            financement = Financement.objects.filter(projet=projet, bailleur=bailleur).first()
            if not financement:
                counts['errors'].append(f"Ligne {i}: Aucun financement {sigle_bailleur} → {code_projet}")
                continue

            # Try to match existing decaissement
            if reference:
                obj, created = Decaissement.objects.update_or_create(
                    financement=financement,
                    reference=reference,
                    date_decaissement=date_dec,
                    defaults={
                        'montant': montant,
                        'description': description,
                    }
                )
            else:
                # No reference = always create
                Decaissement.objects.create(
                    financement=financement,
                    montant=montant,
                    date_decaissement=date_dec,
                    reference=reference,
                    description=description,
                )
                created = True

            if created:
                counts['created'] += 1
            else:
                counts['updated'] += 1

        except Exception as e:
            counts['errors'].append(f"Ligne {i}: {str(e)}")
