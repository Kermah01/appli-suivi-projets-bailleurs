"""
Génère le fichier Excel type à transmettre aux bailleurs.
4 feuilles : Bailleurs, Projets, Financements, Décaissements
"""
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from io import BytesIO


# ── Couleurs & Styles ──────────────────────────────────────────────
ORANGE = "F77F00"
GREEN = "009A44"
DARK = "1E293B"
LIGHT_ORANGE = "FFF7ED"
LIGHT_GREEN = "F0FDF4"
LIGHT_BLUE = "EFF6FF"
LIGHT_GRAY = "F8FAFC"
WHITE = "FFFFFF"

HEADER_FONT = Font(name="Calibri", bold=True, size=11, color=WHITE)
HEADER_FILL = PatternFill(start_color=DARK, end_color=DARK, fill_type="solid")
HEADER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)

TITLE_FONT = Font(name="Calibri", bold=True, size=14, color=ORANGE)
SUBTITLE_FONT = Font(name="Calibri", italic=True, size=10, color="64748B")

KEY_FILL = PatternFill(start_color=LIGHT_ORANGE, end_color=LIGHT_ORANGE, fill_type="solid")
KEY_FONT = Font(name="Calibri", bold=True, size=11, color="C2410C")

EXAMPLE_FONT = Font(name="Calibri", italic=True, size=10, color="94A3B8")
EXAMPLE_FILL = PatternFill(start_color=LIGHT_GRAY, end_color=LIGHT_GRAY, fill_type="solid")

THIN_BORDER = Border(
    left=Side(style="thin", color="E2E8F0"),
    right=Side(style="thin", color="E2E8F0"),
    top=Side(style="thin", color="E2E8F0"),
    bottom=Side(style="thin", color="E2E8F0"),
)


def _style_header(ws, row, col_count):
    for c in range(1, col_count + 1):
        cell = ws.cell(row=row, column=c)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = HEADER_ALIGN
        cell.border = THIN_BORDER


def _style_key_column(ws, row, col):
    cell = ws.cell(row=row, column=col)
    cell.fill = KEY_FILL
    cell.font = KEY_FONT


def _add_example_row(ws, row, values):
    for c, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=c, value=v)
        cell.font = EXAMPLE_FONT
        cell.fill = EXAMPLE_FILL
        cell.border = THIN_BORDER


def _auto_width(ws, col_count, min_width=14, max_width=40):
    for c in range(1, col_count + 1):
        letter = get_column_letter(c)
        lengths = []
        for row in ws.iter_rows(min_col=c, max_col=c, values_only=False):
            for cell in row:
                if cell.value:
                    lengths.append(len(str(cell.value)))
        best = max(lengths) if lengths else min_width
        ws.column_dimensions[letter].width = min(max(best + 3, min_width), max_width)


def generate_template():
    """Retourne un BytesIO contenant le fichier Excel template."""
    wb = openpyxl.Workbook()

    # ════════════════════════════════════════════════════════════════
    # FEUILLE 1 : BAILLEURS
    # ════════════════════════════════════════════════════════════════
    ws1 = wb.active
    ws1.title = "Bailleurs"
    ws1.sheet_properties.tabColor = ORANGE

    ws1.cell(row=1, column=1, value="FICHE BAILLEURS").font = TITLE_FONT
    ws1.cell(row=2, column=1, value="La colonne 'Sigle' sert de clé unique. Si un bailleur avec ce sigle existe déjà, ses informations seront mises à jour.").font = SUBTITLE_FONT

    headers_b = [
        "Sigle *", "Nom complet *", "Type de bailleur *",
        "Catégorie institutionnelle", "Pays du siège",
        "Description", "Site web", "Email de contact"
    ]
    for c, h in enumerate(headers_b, 1):
        ws1.cell(row=4, column=c, value=h)
    _style_header(ws1, 4, len(headers_b))

    # Exemple
    _add_example_row(ws1, 5, [
        "BM", "Banque Mondiale", "Multilatéral",
        "Institutions de Bretton Woods", "États-Unis",
        "Institution financière internationale", "https://worldbank.org", "info@worldbank.org"
    ])
    _add_example_row(ws1, 6, [
        "AFD", "Agence Française de Développement", "Bilatéral",
        "Coopération bilatérale", "France",
        "Agence de développement française", "https://afd.fr", ""
    ])

    # Validations
    type_bailleur_vals = '"Multilatéral,Bilatéral,Régional,Privé,ONG Internationale,Autre"'
    dv_type = DataValidation(type="list", formula1=type_bailleur_vals, allow_blank=False)
    dv_type.error = "Choisir : Multilatéral, Bilatéral, Régional, Privé, ONG Internationale, Autre"
    dv_type.errorTitle = "Type invalide"
    ws1.add_data_validation(dv_type)
    dv_type.add(f"C5:C1000")

    cat_vals = '"Institutions de Bretton Woods,Système des Nations Unies,Banques multilatérales de développement,Coopération bilatérale,Institutions régionales africaines,Fonds verticaux / thématiques,Secteur privé / Fondations,ONG internationales,Autre"'
    dv_cat = DataValidation(type="list", formula1=cat_vals, allow_blank=True)
    ws1.add_data_validation(dv_cat)
    dv_cat.add(f"D5:D1000")

    _auto_width(ws1, len(headers_b))

    # ════════════════════════════════════════════════════════════════
    # FEUILLE 2 : PROJETS
    # ════════════════════════════════════════════════════════════════
    ws2 = wb.create_sheet("Projets")
    ws2.sheet_properties.tabColor = GREEN

    ws2.cell(row=1, column=1, value="FICHE PROJETS").font = TITLE_FONT
    ws2.cell(row=2, column=1, value="La colonne 'Code projet' sert de clé unique. Si un projet avec ce code existe déjà, il sera mis à jour.").font = SUBTITLE_FONT

    headers_p = [
        "Code projet *", "Titre *", "Description",
        "Secteur (code)", "Bailleur principal (sigle)",
        "Devise", "Montant total",
        "Date de signature", "Date de début", "Date de fin prévue",
        "Statut", "Taux d'avancement (%)",
        "Zone géographique", "Responsable"
    ]
    for c, h in enumerate(headers_p, 1):
        ws2.cell(row=4, column=c, value=h)
    _style_header(ws2, 4, len(headers_p))

    _add_example_row(ws2, 5, [
        "PRJ-001", "Programme d'appui au secteur de la santé",
        "Programme visant à renforcer le système de santé",
        "SAN", "BM", "USD", 45000000,
        "2023-01-15", "2023-03-01", "2027-12-31",
        "En cours d'exécution", 62,
        "Abidjan", "Direction SAN"
    ])
    _add_example_row(ws2, 6, [
        "PRJ-NEW", "Nouveau projet éducatif",
        "Projet pilote d'éducation numérique",
        "EDU", "AFD", "EUR", 5000000,
        "2025-06-01", "2025-09-01", "2028-08-31",
        "Préparation", 0,
        "Bouaké", "Direction EDU"
    ])

    # Validations projets
    dv_devise = DataValidation(type="list", formula1='"USD,EUR,XOF,GBP,JPY,CHF,CNY"', allow_blank=True)
    ws2.add_data_validation(dv_devise)
    dv_devise.add("F5:F1000")

    dv_statut = DataValidation(
        type="list",
        formula1='"Identification,Préparation,Négociation,En cours d\'exécution,Suspendu,Clôturé,Annulé"',
        allow_blank=True
    )
    ws2.add_data_validation(dv_statut)
    dv_statut.add("K5:K1000")

    _auto_width(ws2, len(headers_p))

    # ════════════════════════════════════════════════════════════════
    # FEUILLE 3 : FINANCEMENTS
    # ════════════════════════════════════════════════════════════════
    ws3 = wb.create_sheet("Financements")
    ws3.sheet_properties.tabColor = "3B82F6"

    ws3.cell(row=1, column=1, value="FICHE FINANCEMENTS").font = TITLE_FONT
    ws3.cell(row=2, column=1, value="Le triplet (Code projet + Sigle bailleur + Type de financement) identifie un financement. Un même projet peut avoir plusieurs bailleurs (cofinancement). Un même bailleur peut apporter plusieurs types de financement.").font = SUBTITLE_FONT

    headers_f = [
        "Code projet *", "Sigle bailleur *",
        "Type de financement", "Montant engagé *",
        "Devise", "Date d'accord",
        "Référence accord", "Observations"
    ]
    for c, h in enumerate(headers_f, 1):
        ws3.cell(row=4, column=c, value=h)
    _style_header(ws3, 4, len(headers_f))

    _add_example_row(ws3, 5, [
        "PRJ-001", "BM", "Don", 35000000,
        "USD", "2023-01-15", "IDA-12345", "Financement principal du bailleur chef de file"
    ])
    _add_example_row(ws3, 6, [
        "PRJ-001", "AFD", "Prêt concessionnel", 8000000,
        "EUR", "2023-06-01", "AFD-PRET-456", "Cofinancement — 2ème bailleur"
    ])
    _add_example_row(ws3, 7, [
        "PRJ-001", "UE", "Don", 5000000,
        "EUR", "2023-09-01", "EU-GRANT-789", "Cofinancement — 3ème bailleur"
    ])

    dv_type_fin = DataValidation(
        type="list",
        formula1='"Don,Prêt concessionnel,Prêt non concessionnel,Assistance technique,Cofinancement,Contrepartie nationale,Autre"',
        allow_blank=True
    )
    ws3.add_data_validation(dv_type_fin)
    dv_type_fin.add("C5:C1000")

    dv_devise_f = DataValidation(type="list", formula1='"USD,EUR,XOF,GBP,JPY,CHF"', allow_blank=True)
    ws3.add_data_validation(dv_devise_f)
    dv_devise_f.add("E5:E1000")

    _auto_width(ws3, len(headers_f))

    # ════════════════════════════════════════════════════════════════
    # FEUILLE 4 : DÉCAISSEMENTS
    # ════════════════════════════════════════════════════════════════
    ws4 = wb.create_sheet("Décaissements")
    ws4.sheet_properties.tabColor = "22C55E"

    ws4.cell(row=1, column=1, value="FICHE DÉCAISSEMENTS").font = TITLE_FONT
    ws4.cell(row=2, column=1, value="La paire (Référence + Date) sert de clé. Si elle existe déjà, le montant sera mis à jour. Sinon un nouveau décaissement sera créé.").font = SUBTITLE_FONT

    headers_d = [
        "Code projet *", "Sigle bailleur *",
        "Montant décaissé *", "Date de décaissement *",
        "Référence", "Description"
    ]
    for c, h in enumerate(headers_d, 1):
        ws4.cell(row=4, column=c, value=h)
    _style_header(ws4, 4, len(headers_d))

    _add_example_row(ws4, 5, [
        "PRJ-001", "BM", 8000000, "2024-03-15",
        "DEC-PRJ-001-001", "Décaissement tranche 1"
    ])
    _add_example_row(ws4, 6, [
        "PRJ-001", "BM", 12000000, "2024-09-30",
        "DEC-PRJ-001-002", "Décaissement tranche 2"
    ])

    _auto_width(ws4, len(headers_d))

    # ════════════════════════════════════════════════════════════════
    # FEUILLE 5 : INSTRUCTIONS
    # ════════════════════════════════════════════════════════════════
    ws5 = wb.create_sheet("Instructions")
    ws5.sheet_properties.tabColor = "8B5CF6"

    instructions = [
        ("GUIDE DE REMPLISSAGE", TITLE_FONT),
        ("", None),
        ("RÈGLES GÉNÉRALES", Font(name="Calibri", bold=True, size=12, color=DARK)),
        ("• Les colonnes marquées d'un astérisque (*) sont obligatoires.", None),
        ("• Les lignes d'exemple (en gris) doivent être supprimées ou remplacées.", None),
        ("• Les dates doivent être au format AAAA-MM-JJ (ex: 2025-03-15).", None),
        ("• Les montants doivent être des nombres sans espaces ni symboles monétaires.", None),
        ("• Utilisez les listes déroulantes lorsqu'elles sont disponibles.", None),
        ("", None),
        ("COFINANCEMENT", Font(name="Calibri", bold=True, size=12, color=DARK)),
        ("• Un projet peut être financé par PLUSIEURS bailleurs. C'est le cofinancement.", None),
        ("• Pour saisir un cofinancement, ajoutez PLUSIEURS lignes dans la feuille Financements avec le même code projet mais des bailleurs différents.", None),
        ("• Exemple : PRJ-001 financé par BM (Don 35M), AFD (Prêt 8M) et UE (Don 5M) = 3 lignes dans Financements.", None),
        ("• Le 'Bailleur principal' de la feuille Projets indique le chef de file, mais tous les bailleurs sont saisis dans Financements.", None),
        ("• Un même bailleur peut aussi apporter plusieurs types de financement au même projet (ex: Don + Assistance technique).", None),
        ("", None),
        ("LOGIQUE DE MISE À JOUR INTELLIGENTE", Font(name="Calibri", bold=True, size=12, color=DARK)),
        ("• Bailleurs : Le SIGLE sert d'identifiant unique. Si un bailleur avec ce sigle existe déjà, ses infos seront mises à jour.", None),
        ("• Projets : Le CODE PROJET sert d'identifiant unique. Si un projet avec ce code existe déjà, il sera mis à jour.", None),
        ("• Financements : Le triplet (CODE PROJET + SIGLE BAILLEUR + TYPE) identifie un financement. Existant = mise à jour.", None),
        ("• Décaissements : La combinaison (CODE PROJET + SIGLE BAILLEUR + RÉFÉRENCE + DATE) identifie un décaissement.", None),
        ("", None),
        ("ORDRE DE REMPLISSAGE RECOMMANDÉ", Font(name="Calibri", bold=True, size=12, color=DARK)),
        ("1. D'abord remplir la feuille Bailleurs (créer les organismes financeurs)", None),
        ("2. Puis la feuille Projets (qui référencent les bailleurs par leur sigle)", None),
        ("3. Puis Financements (qui lient projets et bailleurs — plusieurs lignes par projet pour le cofinancement)", None),
        ("4. Enfin Décaissements (qui référencent un financement existant)", None),
        ("", None),
        ("VALEURS ACCEPTÉES", Font(name="Calibri", bold=True, size=12, color=DARK)),
        ("Type de bailleur : Multilatéral, Bilatéral, Régional, Privé, ONG Internationale, Autre", None),
        ("Devise : USD, EUR, XOF, GBP, JPY, CHF, CNY", None),
        ("Statut projet : Identification, Préparation, Négociation, En cours d'exécution, Suspendu, Clôturé, Annulé", None),
        ("Type de financement : Don, Prêt concessionnel, Prêt non concessionnel, Assistance technique, Cofinancement, Contrepartie nationale, Autre", None),
    ]

    for i, (text, font) in enumerate(instructions, 1):
        cell = ws5.cell(row=i, column=1, value=text)
        if font:
            cell.font = font
        else:
            cell.font = Font(name="Calibri", size=10, color="334155")

    ws5.column_dimensions["A"].width = 100

    # Sauvegarder
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer
