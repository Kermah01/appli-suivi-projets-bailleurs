"""Partie 2 — Sections 5 à 8 + Annexes + Point d'entrée principal"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import datetime

# ── Réimporter les helpers depuis gen_cdc_v2 ──────────────────────────────────
from gen_cdc_v2 import (
    DARK_BLUE, MID_BLUE, ORANGE_CI, VERT_CI, GRAY_DARK, GRAY_MID,
    WHITE, BLACK, BG_ORANGE,
    set_cell_bg, set_cell_borders, no_borders,
    heading1, heading2, heading3, body, bullet, numbered_item,
    info_box, separator, big_table, profile_card, styled_para,
    cover_page, table_des_matieres, avant_propos, abreviations,
    section1, section2, section3, section4
)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 5 — SPÉCIFICATIONS FONCTIONNELLES
# ══════════════════════════════════════════════════════════════════════════════

def section5(doc):
    heading1(doc, "Spécifications fonctionnelles détaillées", num="5.")
    separator(doc)

    # 5.1 TABLEAU DE BORD
    heading2(doc, "Tableau de bord et indicateurs de performance (M1)", num="5.1")
    body(doc,
        "Le tableau de bord est la page d'accueil de la plateforme. Il constitue le point d'entrée "
        "principal pour l'ensemble des profils et doit offrir, en un coup d'œil, une vision synthétique "
        "de l'état du portefeuille. Son contenu s'adapte automatiquement au profil de l'utilisateur "
        "connecté : les données présentées au Ministre sont différentes, en niveau de détail et en "
        "format, de celles présentées à un Point Focal. Le tableau de bord devra être conçu selon "
        "un principe de simplicité et de lisibilité maximale, en évitant toute surcharge informationnelle.")

    heading3(doc, "Indicateurs clés de performance (KPI)", num="5.1.1")
    body(doc,
        "Les KPI constituent le cœur du tableau de bord. Ils seront présentés sous forme de cartes "
        "visuelles de grande taille, lisibles sans effort, avec indication de la tendance (hausse/baisse) "
        "par rapport à la période précédente. La plateforme devra calculer et afficher au minimum "
        "les indicateurs suivants :")
    kpis = [
        ("Nombre total de projets", "Tous statuts, dans le périmètre de l'utilisateur."),
        ("Projets actifs (en cours d'exécution)", "Projets ayant le statut « En cours d'exécution »."),
        ("Projets en retard", "Projets en cours dont la date de fin prévue est dépassée à la date du jour."),
        ("Nombre de bailleurs actifs", "Bailleurs ayant au moins un projet dans le périmètre."),
        ("Montant total engagé (FCFA)", "Cumul de tous les financements, converti en FCFA au taux contractuel."),
        ("Montant total décaissé (FCFA)", "Cumul de tous les décaissements, converti en FCFA."),
        ("Taux de décaissement global (%)", "Montant décaissé / Montant engagé × 100, affiché en jauge."),
        ("Montants en pipeline", "Montants engagés mais non encore décaissés — clarification demandée par la DGP."),
    ]
    big_table(doc, ["KPI", "Définition et mode de calcul"], kpis, col_widths=[5.5, 11], font_size=9.5)

    heading3(doc, "Graphiques de synthèse", num="5.1.2")
    body(doc,
        "Le tableau de bord intégrera des graphiques interactifs permettant une lecture rapide "
        "des tendances. Les graphiques doivent être clairs, étiquetés en français et exportables "
        "en image. La plateforme devra proposer au minimum :")
    bullet(doc, "Répartition des projets par statut (barres horizontales ou camembert).")
    bullet(doc, "Répartition des projets par secteur d'activité (donut ou barres).")
    bullet(doc, "Répartition des financements par type de bailleur (multilatéral, bilatéral, etc.).")
    bullet(doc, "Évolution des décaissements dans le temps (courbe ou aires).")
    bullet(doc, "Cartographie des zones d'intervention (carte interactive — voir module M6).")
    bullet(doc, "Tableau des projets en retard (5 à 10 projets les plus critiques, triés par ancienneté du retard).")
    bullet(doc, "Tableau des projets récemment créés ou modifiés.")

    heading3(doc, "Moteur d'analyse interactive", num="5.1.3")
    body(doc,
        "Pour les profils ayant accès à l'analyse (DirCab, Administrateur), la plateforme proposera "
        "un moteur d'analyse permettant de générer à la volée des graphiques personnalisés selon "
        "des critères choisis par l'utilisateur (axes X/Y, type de graphique, filtres). "
        "Ce moteur devra fonctionner sans rechargement de page.")

    # 5.2 PROJETS
    heading2(doc, "Gestion des projets et programmes (M2)", num="5.2")
    body(doc,
        "Le module de gestion des projets est le cœur opérationnel de la plateforme. Il devra "
        "permettre de gérer l'ensemble du cycle de vie d'un projet de développement, depuis son "
        "identification jusqu'à sa clôture. Une distinction claire devra être opérée entre les "
        "notions de programme (ensemble cohérent d'interventions stratégiques) et de projet "
        "(unité d'intervention spécifique, disposant de ses propres financements et indicateurs). "
        "Cette distinction, demandée par le PHAS/ANStat, devra être reflétée dans la structure "
        "des données et dans l'interface.")

    heading3(doc, "Données descriptives d'un projet", num="5.2.1")
    fields_proj = [
        ("Code du projet", "Identifiant unique alphanumérique (obligatoire). Ex : CI-BAD-2023-001."),
        ("Programme de rattachement", "Programme stratégique auquel appartient le projet (optionnel)."),
        ("Titre du projet", "Intitulé complet officiel du projet (obligatoire)."),
        ("Description et objectifs", "Texte libre décrivant la nature, les objectifs et les résultats attendus."),
        ("Secteur d'activité", "Référentiel sectoriel : Agriculture, Éducation, Santé, Eau & Assainissement, Infrastructure, Énergie, Gouvernance, Environnement, Développement Rural, Secteur Privé, Filets sociaux, Autre."),
        ("Bailleur principal", "Institution chef de file du financement. Distinct du co-financement."),
        ("Statut du projet", "Identification / Préparation / Négociation / En cours d'exécution / Suspendu / Clôturé / Annulé."),
        ("Type de coopération", "Projet d'investissement / Appui budgétaire / Assistance technique / Subvention programme / Autre."),
        ("Devise de référence", "USD, EUR, XOF, JPY, GBP, CHF, CNY — le taux de conversion utilisé est celui contractuellement défini à la date de signature."),
        ("Montant total du projet", "Montant global toutes sources de financement confondues."),
        ("Part de l'État (contrepartie)", "Montant de la contrepartie nationale — pour les projets co-financés par l'État."),
        ("Taux d'avancement physique (%)", "Pourcentage d'exécution physique des activités (0–100 %). Renseigné par le Point Focal."),
        ("Taux d'avancement financier (%)", "Pourcentage d'exécution financière. Calculé ou saisi. Le type de taux affiché devra être explicitement mentionné."),
        ("Date de signature de l'accord", "Date officielle de signature de la convention de financement."),
        ("Date de début des activités", "Date de démarrage effectif des activités sur le terrain."),
        ("Date de fin prévisionnelle", "Date contractuelle de clôture du projet."),
        ("Date de fin effective", "Renseignée après clôture réelle du projet."),
        ("Dates prévisionnelles/effectives d'activités", "Champs additionnels pour les jalons clés du projet (demande DGCOD)."),
        ("Zone géographique d'intervention", "Région(s) concernée(s) sur le territoire ivoirien (sélection multiple possible)."),
        ("Niveau d'intervention géographique", "National / Régional / Local — à cartographier (demande PHAS)."),
        ("Responsable gouvernemental", "Nom, prénom, fonction, email, téléphone du responsable côté gouvernement."),
        ("Structure responsable d'exécution", "Ministère ou direction en charge de la mise en œuvre."),
        ("Responsables locaux", "Noms des responsables intervenant au niveau local (demande DGP/DGATDRL)."),
        ("Motif du retard", "Champ obligatoire si le projet est en retard. Nature désagrégée du retard (administratif, financier, technique, contextuel, autre — demande CCSPPP-BAD)."),
        ("Pièces jointes", "Documents associés au projet : accord de financement, rapports d'avancement, PV de réunion (demande DSID)."),
    ]
    big_table(doc, ["Champ", "Description"], fields_proj, col_widths=[5, 11.5], font_size=9)

    heading3(doc, "Fonctionnalités CRUD et cycle de vie", num="5.2.2")
    bullet(doc, "Création d'un projet avec possibilité d'ajouter simultanément ses financements associés.")
    bullet(doc, "Consultation de la fiche détaillée : toutes les informations du projet, ses financements, ses décaissements, sa localisation cartographique.")
    bullet(doc, "Modification des données par le Point Focal assigné uniquement (contrôle d'accès au niveau de l'objet).")
    bullet(doc, "Suppression avec confirmation explicite, réservée aux profils autorisés.")
    bullet(doc, "Changement de statut avec traçabilité (qui a changé le statut, quand).")
    bullet(doc, "Recherche et filtres multicritères : par code, titre, bailleur, statut, secteur, zone, retard, co-financement.")

    heading3(doc, "Indicateurs calculés automatiquement", num="5.2.3")
    calcs = [
        ("Taux de décaissement (%)", "Total décaissé ÷ Montant total engagé × 100."),
        ("Montant total engagé", "Somme de tous les financements du projet (tous bailleurs)."),
        ("Montant total décaissé", "Somme de tous les décaissements liés au projet."),
        ("Reste à décaisser", "Montant engagé − Montant décaissé."),
        ("Statut de retard", "Automatiquement calculé : en retard si statut=En cours ET date fin prévue < date du jour."),
        ("Nombre de bailleurs / Co-financement", "Nombre de bailleurs distincts finançant le projet. Indicateur co-financement si > 1."),
        ("Alerte discordance physique/financier", "Alerte si écart significatif entre taux d'avancement physique et taux de décaissement."),
    ]
    big_table(doc, ["Indicateur", "Formule / Logique"], calcs, col_widths=[5.5, 11], font_size=9.5)

    # 5.3 BAILLEURS
    heading2(doc, "Gestion des bailleurs de fonds (M3)", num="5.3")
    body(doc,
        "Le module Bailleurs constitue le répertoire de référence de tous les partenaires techniques "
        "et financiers actifs dans le portefeuille. Chaque bailleur dispose d'une fiche détaillée "
        "présentant son profil institutionnel, ses projets financés et ses indicateurs financiers. "
        "La plateforme devra intégrer le logo de chaque bailleur dans sa fiche (demande DSID), "
        "et définir un seuil de significativité en dessous duquel l'intervention d'un bailleur "
        "est considérée comme négligeable (demande DGCOD), ce seuil étant paramétrable par "
        "l'administrateur.")
    bailleur_fields = [
        ("Nom complet", "Dénomination officielle de l'institution."),
        ("Sigle / Acronyme", "Identifiant court (ex. BAD, AFD, BM, PNUD)."),
        ("Logo", "Image du logo officiel de l'institution (format PNG ou SVG)."),
        ("Type de bailleur", "Multilatéral / Bilatéral / Régional / Fonds thématique / ONG Internationale / Secteur privé / Autre."),
        ("Catégorie institutionnelle", "Classification fine : Bretton Woods, Système ONU, Banques multilatérales, Coopération bilatérale, Institutions régionales africaines, Fonds arabes/islamiques, Fonds verticaux/thématiques, Secteur privé/Fondations."),
        ("Pays du siège", "Localisation du siège social."),
        ("Description institutionnelle", "Présentation de la mission et des domaines d'intervention."),
        ("Site web officiel", "URL du site institutionnel."),
        ("Contact de référence", "Email et/ou téléphone du contact institutionnel en Côte d'Ivoire."),
        ("Seuil de significativité", "Montant minimal en dessous duquel le financement n'est pas considéré comme un engagement significatif (paramétrable)."),
    ]
    big_table(doc, ["Champ", "Description"], bailleur_fields, col_widths=[5, 11.5], font_size=9.5)
    body(doc, "La fiche analytique d'un bailleur présentera : nombre de projets financés, montant total engagé, "
        "montant total décaissé, taux de décaissement global, répartition sectorielle, répartition par "
        "statut, répartition par zone géographique, répartition par type de financement, et carte "
        "des projets localisés. Un tableau détaillé de tous les projets financés sera inclus.")

    # 5.4 FINANCEMENTS
    heading2(doc, "Financements et décaissements (M4)", num="5.4")
    body(doc,
        "Le module Financements assure le suivi précis et exhaustif des flux financiers entre "
        "les bailleurs et les projets. Il distingue l'engagement (accord signé) du décaissement "
        "(versement effectif) et permet de calculer à tout moment le reste à décaisser et "
        "le taux de consommation des financements.")

    heading3(doc, "Données d'un financement", num="5.4.1")
    fin_f = [
        ("Projet", "Référence au projet bénéficiaire."),
        ("Bailleur", "Institution pourvoyeuse de fonds."),
        ("Type de financement", "Don / Prêt concessionnel / Prêt non concessionnel / Assistance technique / Appui budgétaire / Contrepartie nationale / Co-financement / Autre."),
        ("Appui budgétaire", "Indicateur booléen — module spécifique si activé (demande DGCOD)."),
        ("Montant engagé", "Montant de l'accord de financement dans la devise de l'accord."),
        ("Devise", "USD, EUR, XOF, JPY, GBP, CHF, CNY."),
        ("Taux de conversion contractuel", "Taux en vigueur à la date de signature, défini contractuellement (demande ENSEA/DGCOD). Stocké en base et non mis à jour automatiquement."),
        ("Date de l'accord", "Date de signature ou d'entrée en vigueur."),
        ("Référence de l'accord", "Numéro ou code de référence officiel."),
        ("Observations", "Notes complémentaires."),
    ]
    big_table(doc, ["Champ", "Description"], fin_f, col_widths=[4.5, 12], font_size=9.5)

    heading3(doc, "Données d'un décaissement", num="5.4.2")
    dec_f = [
        ("Financement de référence", "Lien vers le financement parent (bailleur + projet)."),
        ("Montant décaissé", "Montant du versement dans la devise de l'accord."),
        ("Date du décaissement", "Date effective du versement (obligatoire)."),
        ("Date prévisionnelle de décaissement", "Date planifiée du versement — pour le suivi du pipeline (demande DGCOD)."),
        ("Référence du virement", "Code de traçabilité bancaire ou administrative."),
        ("Description / Objet", "Libellé du décaissement (tranche, activité financée)."),
    ]
    big_table(doc, ["Champ", "Description"], dec_f, col_widths=[4.5, 12], font_size=9.5)

    info_box(doc, "📌  Notion de pipeline :",
        "Les montants engagés mais non encore décaissés constituent le « pipeline » de financement. "
        "La plateforme devra afficher explicitement ce montant, clairement distingué des montants "
        "décaissés, pour chaque projet et en agrégé (demande DGP).",
        bg='FFF3E0', border_color='F77F00')

    # 5.5 ALERTES
    heading2(doc, "Système d'alertes et de signalement (M5)", num="5.5")
    body(doc,
        "Le système d'alertes est l'une des fonctionnalités les plus stratégiques de la plateforme. "
        "Il permet d'identifier automatiquement les projets nécessitant une attention particulière "
        "et d'en informer les niveaux hiérarchiques appropriés, sans que ceux-ci aient besoin "
        "d'analyser manuellement l'ensemble du portefeuille. Les alertes sont différenciées "
        "par niveau de gravité et par profil destinataire.")
    alertes = [
        ("Retard avéré", "Critique", "Ministre, DirCab", "Projet en cours dont la date de fin prévue est dépassée. Affichage du nombre de jours de retard."),
        ("Faible taux de décaissement", "Attention", "DirCab, Point Focal", "Projet en cours avec taux de décaissement inférieur au seuil paramétrable (défaut : 20 %)."),
        ("Discordance physique / financier", "Attention", "DirCab, Point Focal", "Écart significatif entre le taux d'avancement physique et le taux de décaissement (ex. : >30 points d'écart — seuil paramétrable)."),
        ("Données non mises à jour", "Information", "Administrateur, DirCab", "Projet sans mise à jour depuis un délai paramétrable (ex. : 60 jours). Suivi de la ponctualité de saisie."),
        ("Signalement manuel", "Variable", "DirCab, Ministre", "Alert levée manuellement par un Point Focal pour signaler une situation particulière nécessitant l'attention du Cabinet."),
    ]
    big_table(doc, ["Type d'alerte", "Niveau", "Destinataires", "Critère de déclenchement"],
              alertes, col_widths=[3.8, 2.2, 3.5, 7], font_size=9.5)
    body(doc,
        "Les alertes seront visibles dans un centre de notifications accessible depuis toutes les "
        "interfaces (icône dans la barre de navigation). Pour le Ministre, elles seront mises en "
        "évidence en haut de son tableau de bord sous forme de bannières colorées. Un historique "
        "des alertes traitées devra être conservé.")

    # 5.6 CARTOGRAPHIE
    heading2(doc, "Module cartographique (M6)", num="5.6")
    body(doc,
        "La visualisation géographique des projets est une fonctionnalité clé demandée par "
        "l'ensemble des parties prenantes lors des consultations. La plateforme devra intégrer "
        "une carte interactive de la Côte d'Ivoire permettant de visualiser la distribution "
        "territoriale des projets. Plusieurs recommandations précises ont été formulées lors "
        "des consultations et sont intégrées ci-après.")
    bullet(doc, "La carte devra afficher les projets par zone géographique d'intervention, en distinguant clairement le niveau national, régional et local.", bold_prefix="Niveaux d'intervention — ")
    bullet(doc, "Contrairement à une représentation qui additionnerait les montants par région, la carte devra afficher le nombre de projets actifs par région, et non des montants financiers, car un même projet peut intervenir dans plusieurs régions simultanément — ce qui rendrait les montants par région inexacts (demande PHAS/ANStat).", bold_prefix="Pas de montants par région — ")
    bullet(doc, "La fiche détaillée de chaque projet devra intégrer une cartographie spécifique montrant ses zones précises d'intervention (demande PHAS, CCSPPP-BAD).", bold_prefix="Carte dans la fiche projet — ")
    bullet(doc, "Un clic sur une région de la carte principale affiche la liste des projets actifs dans cette région.", bold_prefix="Interactivité — ")
    bullet(doc, "La cartographie des performances (âge du projet + taux de décaissement) permettra d'identifier visuellement les zones géographiques où les projets sont les plus en difficulté (demande Cellule Bailleurs Arabes).", bold_prefix="Carte de performance — ")

    # 5.7 REPORTING
    heading2(doc, "Reporting et export des données (M7)", num="5.7")
    body(doc,
        "La plateforme devra offrir des fonctionnalités d'export permettant aux utilisateurs "
        "autorisés de produire des rapports et extractions de données pour un travail hors connexion, "
        "la préparation de réunions ou la transmission à des tiers.")
    exports = [
        ("Export liste des projets", "Ministre, DirCab, Point Focal", "Excel (.xlsx)", "Liste filtrée des projets avec indicateurs clés (financiers, physiques, retard). Accès accordé explicitement au Ministre et au DirCab (demande PHAS)."),
        ("Export synthèse KPI", "Ministre, DirCab", "Excel ou PDF", "Synthèse des indicateurs clés en format imprimable pour réunions et conseils ministériels (demande ENSEA)."),
        ("Export fiche bailleur", "DirCab, Point Focal", "Excel", "Données analytiques d'un bailleur : portefeuille, financements, décaissements."),
        ("Export rapport retards", "DirCab, Administrateur", "Excel", "Liste des projets en retard avec motifs et délais de retard."),
        ("Export données cartographiques", "DirCab", "Excel", "Projets par région avec indicateurs."),
    ]
    big_table(doc, ["Type d'export", "Profils autorisés", "Format", "Contenu"],
              exports, col_widths=[4, 3.5, 2, 7], font_size=9.5)

    # 5.8 IMPORT
    heading2(doc, "Import de données en masse (M8)", num="5.8")
    body(doc,
        "Pour faciliter l'alimentation initiale de la base de données et les mises à jour "
        "périodiques, la plateforme proposera un module d'import de données par fichier Excel. "
        "L'accès à ce module sera strictement réservé aux utilisateurs habilités désignés "
        "par l'administrateur (demande PHAS/ANStat). Le prestataire fournira un fichier "
        "modèle Excel (template) documenté.")
    body(doc,
        "Le processus d'import se déroulera en deux temps : une phase d'analyse et de prévisualisation, "
        "puis une phase de confirmation et d'exécution. Lors de la prévisualisation, la plateforme "
        "distingue les créations, les mises à jour, les lignes ignorées (doublons) et les erreurs "
        "(données manquantes ou invalides). L'import ne s'exécute que si l'utilisateur confirme "
        "après avoir pris connaissance du rapport de prévisualisation.")
    body(doc, "Le fichier d'import sera structuré en feuilles distinctes : Bailleurs, Projets, "
        "Financements, Décaissements. Chaque feuille dispose d'un en-tête documenté avec les "
        "libellés en français. La logique d'import est idempotente : une ligne existante est "
        "mise à jour plutôt que dupliquée.")

    # 5.9 ASSISTANT IA
    heading2(doc, "Assistant d'analyse par intelligence artificielle (M9)", num="5.9")
    body(doc,
        "La plateforme intégrera un assistant conversationnel basé sur l'intelligence artificielle "
        "permettant aux utilisateurs d'interroger la base de données en langage naturel "
        "(en français) et d'obtenir des réponses structurées, enrichies de graphiques et tableaux. "
        "Cet assistant est accessible selon les profils autorisés (DirCab, Conseillers, Points Focaux).")
    body(doc,
        "À chaque question, l'assistant reçoit un contexte actualisé des données du portefeuille "
        "filtré selon le profil de l'utilisateur — un Point Focal ne verra dans les réponses que "
        "les données de ses bailleurs assignés. L'assistant peut générer des synthèses textuelles, "
        "des tableaux de comparaison et des graphiques dynamiques directement dans l'interface. "
        "Il conserve l'historique de la conversation pour maintenir la cohérence du dialogue. "
        "En cas d'indisponibilité du service IA, les autres modules de la plateforme restent "
        "pleinement opérationnels.")

    # 5.10 ADMINISTRATION
    heading2(doc, "Administration des comptes et des droits (M10)", num="5.10")
    body(doc,
        "L'administration des comptes est centralisée et réservée à l'Administrateur de la plateforme. "
        "Aucun mécanisme d'auto-inscription public n'est prévu. L'Administrateur crée les comptes, "
        "définit les rôles, assigne les bailleurs aux Points Focaux et transmet les identifiants "
        "aux utilisateurs par voie sécurisée. Ce choix, unanimement soutenu lors des consultations, "
        "garantit un contrôle strict des accès.")
    body(doc, "Les fonctionnalités d'administration incluent :")
    bullet(doc, "Création, modification, désactivation et suppression des comptes utilisateurs.")
    bullet(doc, "Attribution des rôles : Administrateur, Directeur/Haute Fonction, Point Focal, Lecteur.")
    bullet(doc, "Assignation des bailleurs autorisés à chaque Point Focal.")
    bullet(doc, "Gestion des fonctions institutionnelles (unicité des fonctions à responsabilité unique).")
    bullet(doc, "Journal d'audit complet : traçabilité de toutes les opérations sensibles (qui, quoi, quand).")
    bullet(doc, "Suivi de la ponctualité de saisie : identification des structures ayant renseigné les données dans les délais impartis (demande ENSEA). Un tableau de bord de ponctualité sera accessible à l'Administrateur et au DirCab.")
    bullet(doc, "Conformité avec la réglementation ivoirienne sur la protection des données personnelles (ARTCI — demande DSID).")
    bullet(doc, "Recherche globale transversale : projets, bailleurs, financements — accessible depuis toutes les interfaces (minimum 2 caractères).")
    bullet(doc, "Barre de navigation rétractable pour maximiser l'espace d'affichage (demande ENSEA).")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 6 — EXIGENCES NON FONCTIONNELLES
# ══════════════════════════════════════════════════════════════════════════════

def section6(doc):
    heading1(doc, "Exigences non fonctionnelles", num="6.")
    separator(doc)

    heading2(doc, "Performance et temps de réponse", num="6.1")
    body(doc,
        "La plateforme devra répondre aux exigences de performance suivantes : les pages principales "
        "(tableau de bord, liste des projets) devront se charger en moins de 3 secondes pour un "
        "portefeuille de 500 projets, sur une connexion internet standard. Les opérations d'export "
        "et d'import de fichiers Excel ne devront pas excéder 30 secondes. Les graphiques interactifs "
        "devront se rafraîchir sans délai perceptible lors d'un changement de filtre.")

    heading2(doc, "Sécurité des données et conformité réglementaire", num="6.2")
    body(doc,
        "La sécurité est une exigence fondamentale de la plateforme. Le prestataire devra "
        "garantir les mesures suivantes : toutes les communications entre les utilisateurs "
        "et la plateforme doivent être chiffrées via le protocole HTTPS. Les mots de passe "
        "doivent être stockés de manière irréversiblement hachée (algorithme bcrypt ou équivalent). "
        "La protection contre les attaques web courantes (injection SQL, XSS, CSRF) doit être "
        "intégralement implémentée. Les identifiants et clés d'API ne doivent jamais être "
        "exposés dans le code source ou les logs.")
    body(doc,
        "La plateforme devra être conforme à la législation ivoirienne relative à la protection "
        "des données à caractère personnel (Loi n°2013-450 et réglementation ARTCI), "
        "notamment en ce qui concerne le consentement, la finalité du traitement et "
        "la durée de conservation des données utilisateurs (demande DSID).")

    heading2(doc, "Ergonomie et accessibilité", num="6.3")
    body(doc,
        "L'interface devra être conçue selon les principes d'ergonomie suivants : navigation "
        "intuitive ne nécessitant pas de formation technique approfondie, libellés en "
        "français correct sans termes anglais non traduits (demande BNPVS), "
        "charte graphique du Ministère du Plan et du Développement respectée "
        "(couleurs institutionnelles, typographie, logo officiel — demande PHAS/ANStat). "
        "La plateforme sera optimisée pour les navigateurs web modernes (Chrome, Firefox, Edge). "
        "Une version adaptée aux tablettes sera considérée comme un plus.")
    body(doc,
        "La plateforme sera accompagnée d'un manuel d'utilisation détaillé et, idéalement, "
        "d'un didacticiel interactif intégré (demande DSID). Un titre approprié et identitaire "
        "devra être proposé pour la plateforme (demande DGCOD).")

    heading2(doc, "Maintenabilité et évolutivité", num="6.4")
    body(doc,
        "Le code source devra être structuré, documenté et livré avec une documentation "
        "technique permettant à la DSID de le maintenir et de le faire évoluer. "
        "L'architecture devra être modulaire pour permettre l'ajout de nouveaux modules "
        "sans refonte majeure. La plateforme sera conçue comme un outil évolutif "
        "(DG DGCOD), avec une feuille de route claire pour la Phase 2.")

    heading2(doc, "Disponibilité et continuité de service", num="6.5")
    body(doc,
        "La plateforme devra être disponible 24h/24, 7j/7, avec un taux de disponibilité "
        "cible de 99,5 % hors maintenance planifiée. Des sauvegardes automatiques de la base "
        "de données devront être configurées (quotidiennes minimum). "
        "En cas d'indisponibilité de services tiers (assistant IA, cartographie), "
        "la plateforme devra continuer à fonctionner sur ses fonctionnalités de base.")


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 7 — ARCHITECTURE TECHNIQUE
# ══════════════════════════════════════════════════════════════════════════════

def section7(doc):
    heading1(doc, "Architecture technique recommandée", num="7.")
    separator(doc)
    body(doc,
        "Le présent cahier des charges ne prescrit pas de technologie particulière. Cependant, "
        "il définit un ensemble d'exigences techniques minimales que le prestataire devra respecter "
        "dans sa proposition. La solution retenue devra s'appuyer sur des technologies pérennes, "
        "maintenables par les équipes de la DSID, et dont la licence ne génère pas de coût "
        "récurrent prohibitif.")
    body(doc, "Les exigences techniques minimales sont les suivantes :")
    exig_tech = [
        ("Application web", "La plateforme sera accessible via navigateur web, sans installation côté client. Elle sera développée en tant qu'application web dynamique (pas un simple tableur en ligne)."),
        ("Base de données relationnelle", "La base de données devra être relationnelle, robuste et sécurisée. PostgreSQL ou MySQL sont recommandés pour la production."),
        ("Hébergement", "La solution pourra être hébergée sur un serveur cloud (SaaS) ou sur l'infrastructure de la DSID (on-premise). Le prestataire précisera les spécifications matérielles minimales requises."),
        ("Chiffrement HTTPS", "Obligatoire en production. Le prestataire fournira les instructions pour la configuration du certificat SSL/TLS."),
        ("Sauvegarde", "Sauvegardes automatiques quotidiennes de la base de données. Procédure de restauration documentée."),
        ("Interface responsive", "L'interface sera au minimum utilisable sur écran d'ordinateur (1280×768 px minimum). Un affichage adapté aux tablettes est souhaitable."),
        ("Cartographie", "Utilisation d'un moteur de cartographie libre (ex. Leaflet.js) avec les données géographiques officielles de la Côte d'Ivoire (GeoJSON régions)."),
        ("Visualisation des données", "Les graphiques interactifs devront être générés par une bibliothèque JavaScript performante (ex. ApexCharts, Chart.js, Highcharts)."),
        ("Export Excel", "L'export de fichiers Excel devra produire des fichiers .xlsx conformes aux standards Microsoft Office."),
        ("Import Excel", "Le moteur d'import devra gérer les fichiers .xlsx sans macro et valider les données avant exécution."),
        ("API Intelligence Artificielle", "Si un assistant IA est intégré, il devra s'appuyer sur une API de modèle de langage éprouvée (ex. Google Gemini, OpenAI GPT). La clé API sera configurée via variable d'environnement sécurisée."),
    ]
    big_table(doc, ["Composant", "Exigence"], exig_tech, col_widths=[4.5, 12], font_size=9.5)


# ══════════════════════════════════════════════════════════════════════════════
#  SECTION 8 — MODALITÉS D'EXÉCUTION
# ══════════════════════════════════════════════════════════════════════════════

def section8(doc):
    heading1(doc, "Modalités d'exécution et livrables attendus", num="8.")
    separator(doc)

    heading2(doc, "Livrables", num="8.1")
    body(doc,
        "Le prestataire retenu devra produire l'ensemble des livrables listés ci-dessous. "
        "Chaque livrable fera l'objet d'une validation par le Cabinet du Ministère avant "
        "paiement de la tranche correspondante.")
    livrables = [
        ("L1", "Note de cadrage et plan de travail détaillé", "J+10 après notification", "Document Word/PDF présentant la compréhension du projet, la méthodologie, l'architecture proposée et le planning détaillé."),
        ("L2", "Maquettes fonctionnelles (wireframes/mockups)", "J+25", "Maquettes de toutes les interfaces principales, validées par le Cabinet avant tout développement."),
        ("L3", "Prototype fonctionnel (version beta)", "J+60", "Version fonctionnelle partielle permettant de valider les choix d'interface et de workflow avec les utilisateurs clés."),
        ("L4", "Application complète testée (version 1.0)", "J+90", "Tous les modules livrés, testés et documentés. Base de données initialisée avec données de test."),
        ("L5", "Déploiement en production", "J+100", "Déploiement sur l'infrastructure définitive, configuration HTTPS, sauvegardes, test de charge."),
        ("L6", "Formation des utilisateurs", "J+105", "Sessions de formation pour l'Administrateur, les Points Focaux et les utilisateurs de niveau Directeur. Support de formation fourni."),
        ("L7", "Manuel d'utilisation", "J+105", "Manuel utilisateur en français, illustré, couvrant tous les profils. Didacticiel interactif intégré si possible."),
        ("L8", "Documentation technique", "J+110", "Documentation du code source, architecture de la base de données, procédures d'installation et de maintenance."),
        ("L9", "Période de garantie et support", "J+110 à J+200", "Correction des anomalies sans surcoût pendant 90 jours après la livraison. Hotline de support."),
    ]
    big_table(doc, ["Réf.", "Livrable", "Délai", "Description"],
              livrables, col_widths=[1, 4, 2.5, 9], font_size=9)

    heading2(doc, "Planning indicatif", num="8.2")
    body(doc,
        "Le tableau ci-dessous présente le planning indicatif du projet. Les délais sont exprimés "
        "en jours ouvrables à compter de la date de notification du marché (J0). Ce planning "
        "sera précisé et confirmé dans le plan de travail détaillé (Livrable L1).")
    planning = [
        ("Phase 0 — Cadrage", "J0 à J+10", "Réunion de lancement, validation du plan de travail, accès aux données existantes."),
        ("Phase 1 — Conception", "J+10 à J+25", "Maquettes fonctionnelles, validation de l'architecture, choix technologiques."),
        ("Phase 2 — Développement", "J+25 à J+85", "Développement des 10 modules, intégration, tests unitaires."),
        ("Phase 3 — Recette", "J+85 à J+100", "Tests fonctionnels avec les utilisateurs clés, corrections, déploiement prod."),
        ("Phase 4 — Formation & livraison", "J+100 à J+110", "Formation, documentation, livraison finale."),
        ("Phase 5 — Garantie", "J+110 à J+200", "Support et corrections sous garantie."),
    ]
    big_table(doc, ["Phase", "Période", "Activités principales"],
              planning, col_widths=[4, 3, 9.5], font_size=9.5)

    heading2(doc, "Profil du prestataire", num="8.3")
    body(doc,
        "Le prestataire retenu devra démontrer les compétences et expériences suivantes "
        "dans son dossier de candidature :")
    bullet(doc, "Expérience avérée dans le développement d'applications web de gestion de données (minimum 3 réalisations similaires documentées).")
    bullet(doc, "Maîtrise des technologies web modernes (framework web, base de données relationnelle, API REST, bibliothèques de visualisation de données).")
    bullet(doc, "Compétence en conception d'interfaces utilisateur adaptées aux profils décideurs (tableaux de bord exécutifs, KPI visuels).")
    bullet(doc, "Expérience en déploiement et administration d'applications web en production.")
    bullet(doc, "Capacité à assurer la formation des utilisateurs et la rédaction de la documentation.")
    bullet(doc, "Connaissance souhaitée du contexte institutionnel de la gestion de l'aide au développement en Afrique.")


# ══════════════════════════════════════════════════════════════════════════════
#  ANNEXES
# ══════════════════════════════════════════════════════════════════════════════

def annexes(doc):
    # Annexe A
    doc.add_page_break()
    heading1(doc, "ANNEXE A — Recensement détaillé des bailleurs PTF (Phase 1)")
    separator(doc)
    body(doc,
        "Le tableau ci-dessous récapitule les partenaires techniques et financiers dont les projets "
        "seront intégrés dans la plateforme lors de la Phase 1. Cette liste sera finalisée et "
        "validée par le Cabinet du Ministère du Plan et du Développement lors de l'atelier "
        "de lancement. Elle est présentée par catégorie institutionnelle.")

    all_bailleurs = [
        # (Catégorie, Sigle, Nom complet, Type, Domaines prioritaires CI)
        ("Bretton Woods", "BM / IDA", "Banque mondiale — Association Internationale de Développement", "Multilatéral", "Infrastructure, éducation, santé, gouvernance, développement urbain"),
        ("Bretton Woods", "BIRD", "Banque Internationale pour la Reconstruction et le Développement", "Multilatéral", "Infrastructure, secteur financier"),
        ("Bretton Woods", "FMI", "Fonds Monétaire International", "Multilatéral", "Stabilité macroéconomique, appuis budgétaires"),
        ("Banques africaines", "BAD / ADB", "Banque Africaine de Développement", "Multilatéral régional", "Infrastructure, eau, énergie, agriculture, secteur privé"),
        ("Banques africaines", "FAD", "Fonds Africain de Développement", "Multilatéral régional", "Guichet concessionnel BAD — tous secteurs"),
        ("Banques africaines", "BOAD", "Banque Ouest Africaine de Développement", "Régional UEMOA", "Infrastructure, énergie, télécommunications"),
        ("Banques africaines", "BIDC", "Banque d'Investissement et de Développement de la CEDEAO", "Régional CEDEAO", "Infrastructure régionale, intégration économique"),
        ("Institutions européennes", "BEI / EIB", "Banque Européenne d'Investissement", "Multilatéral UE", "Infrastructure, secteur privé, énergie"),
        ("Institutions européennes", "UE / FED", "Union Européenne — Fonds Européen de Développement", "Bilatéral/Multi.", "Gouvernance, développement rural, santé"),
        ("Fonds arabes/islamiques", "BIsD / IsDB", "Banque Islamique de Développement", "Multilatéral islamique", "Éducation, santé, agriculture, infrastructure"),
        ("Fonds arabes/islamiques", "FKDEA", "Fonds Koweïtien pour le Développement Économique Arabe", "Bilatéral", "Infrastructure routière, eau, énergie"),
        ("Fonds arabes/islamiques", "FSD", "Fonds Saoudien pour le Développement", "Bilatéral", "Infrastructure, eau et assainissement"),
        ("Fonds arabes/islamiques", "FADES", "Fonds Arabe pour le Développement Économique et Social", "Multilatéral arabe", "Infrastructure, agriculture"),
        ("Fonds arabes/islamiques", "OFID", "Fonds de l'OPEP pour le Développement International", "Multilatéral", "Énergie, eau, agriculture"),
        ("Fonds arabes/islamiques", "FADD / ADFD", "Fonds d'Abu Dhabi pour le Développement", "Bilatéral EAU", "Infrastructure"),
        ("Coopérations bilatérales", "AFD", "Agence Française de Développement", "Bilatéral français", "Eau, assainissement, éducation, santé, développement urbain"),
        ("Coopérations bilatérales", "JICA", "Japan International Cooperation Agency", "Bilatéral japonais", "Agriculture, infrastructure, santé, renforcement des capacités"),
        ("Coopérations bilatérales", "KfW", "Kreditanstalt für Wiederaufbau (Allemagne)", "Bilatéral allemand", "Énergie, eau, environnement"),
        ("Coopérations bilatérales", "MCC", "Millennium Challenge Corporation (États-Unis)", "Bilatéral américain", "Énergie, eau, transport"),
        ("Coopérations bilatérales", "USAID", "US Agency for International Development", "Bilatéral américain", "Santé, gouvernance, agriculture"),
        ("Coopérations bilatérales", "KOICA", "Korea International Cooperation Agency", "Bilatéral coréen", "TIC, agriculture, renforcement capacités"),
        ("Système Nations Unies", "PNUD", "Programme des Nations Unies pour le Développement", "Multilatéral ONU", "Gouvernance, développement humain, résilience climatique"),
        ("Système Nations Unies", "UNICEF", "Fonds des Nations Unies pour l'Enfance", "Multilatéral ONU", "Éducation, nutrition, protection de l'enfance"),
        ("Système Nations Unies", "OMS", "Organisation Mondiale de la Santé", "Multilatéral ONU", "Santé, couverture sanitaire universelle"),
        ("Système Nations Unies", "FAO", "Organisation des Nations Unies pour l'Alimentation", "Multilatéral ONU", "Agriculture, sécurité alimentaire"),
        ("Système Nations Unies", "FIDA / IFAD", "Fonds International de Développement Agricole", "Multilatéral ONU", "Agriculture, développement rural"),
        ("Système Nations Unies", "PAM / WFP", "Programme Alimentaire Mondial", "Multilatéral ONU", "Sécurité alimentaire, filets sociaux"),
    ]
    big_table(doc, ["Catégorie", "Sigle", "Nom complet", "Type", "Domaines CI"],
              all_bailleurs, col_widths=[3.5, 2.0, 5.5, 2.5, 3], font_size=8.5)

    info_box(doc, "📋  Validation requise :",
        "Cette liste devra être validée par le Cabinet du Ministère avant transmission au prestataire. "
        "Des institutions pourront être ajoutées ou retirées selon les attributions effectives "
        "de gouverneur du Ministre à la date de lancement du projet.",
        bg='E8F5E9', border_color='009A44', title_color=VERT_CI)

    # Annexe B
    doc.add_page_break()
    heading1(doc, "ANNEXE B — Synthèse des observations de la démarche consultative")
    separator(doc)
    body(doc,
        "Les tableaux ci-dessous synthétisent l'ensemble des observations et recommandations "
        "formulées lors des séances de consultation tenues du 5 au 8 mai 2026. "
        "Chaque observation est classée par thème et son statut d'intégration dans le "
        "présent cahier des charges est précisé.")

    obs_data = [
        ("DSID", "Intégrer la part de l'État dans le co-financement de chaque projet", "Intégré — §5.2.1"),
        ("DSID", "Système d'alertes automatiques sur discordances physique/financier", "Intégré — §5.5"),
        ("DSID", "Permettre l'ajout de pièces jointes aux fiches projets", "Intégré — §5.2.1"),
        ("DSID", "Ajouter les logos des bailleurs", "Intégré — §5.3"),
        ("DSID", "Élaborer un cahier des charges avec exigences protection données", "Présent document — §6.2"),
        ("DSID", "Rédiger un manuel d'utilisation + didacticiel interactif", "Intégré — §8.1 (L7)"),
        ("Bailleurs Arabes", "Interconnexion avec leur plateforme interne", "Phase 2 — hors périmètre §3.2"),
        ("Bailleurs Arabes", "Cartographie de performance (âge + taux décaissement)", "Intégré — §5.6"),
        ("Bailleurs Arabes", "Colonne motifs de retard", "Intégré — §5.2.1"),
        ("CCSPPP-BAD", "Plateforme = outil d'alerte pour DirCab et Ministre", "Intégré — §2.1 et §5.5"),
        ("CCSPPP-BAD", "Ajouter section aide à la décision synthétique pour le Ministre", "Intégré — §4.2"),
        ("CCSPPP-BAD", "Désagrégation de la nature des retards", "Intégré — §5.2.1"),
        ("CCSPPP-BAD", "Préciser le type de taux d'avancement (physique/financier)", "Intégré — §5.2.1"),
        ("CCSPPP-BAD", "Retirer l'alignement PND (complexité trop élevée Phase 1)", "Intégré — §3.2 (Phase 2)"),
        ("CCSPPP-BAD", "Rédiger un cahier des charges partagé", "Présent document"),
        ("DGP / DGATDRL", "Clarifier montants pipeline (engagés non décaissés)", "Intégré — §5.4"),
        ("DGP / DGATDRL", "Renommer 'Point Focal Bailleur' en 'Point Focal'", "Intégré — §4.1"),
        ("DGP / DGATDRL", "Répertorier responsables locaux des projets", "Intégré — §5.2.1"),
        ("DGP / DGATDRL", "Étudier interconnexion avec SYNAPSE", "Phase 2 — hors périmètre §3.2"),
        ("PHAS / ANStat", "Respecter charte graphique du Ministère", "Intégré — §2.3 et §6.3"),
        ("PHAS / ANStat", "Supprimer bouton 'Créer un compte' — admin gère les accès", "Intégré — §4.1 et §5.10"),
        ("PHAS / ANStat", "Distinction claire Programme / Projet", "Intégré — §5.2"),
        ("PHAS / ANStat", "Retirer montants par région sur la carte", "Intégré — §5.6"),
        ("PHAS / ANStat", "Cartographier niveaux d'intervention géographique", "Intégré — §5.6"),
        ("PHAS / ANStat", "Cartographie dans la fiche projet", "Intégré — §5.6"),
        ("PHAS / ANStat", "Restrictions d'accès pour chargement de données", "Intégré — §5.8 et §5.10"),
        ("PHAS / ANStat", "Export liste des projets pour Ministre et DirCab", "Intégré — §5.7"),
        ("DGCOD", "Tableau de bord simple pour la décision", "Intégré — §4.2 et §5.1"),
        ("DGCOD", "Intégrer l'euro dans les devises", "Intégré — EUR inclus §5.4.1"),
        ("DGCOD", "Attribuer un titre approprié à la plateforme", "Intégré — §6.3"),
        ("DGCOD", "Seuil significativité pour intervention bailleur", "Intégré — §5.3"),
        ("DGCOD", "Dates prévisionnelles et effectives activités/décaissements", "Intégré — §5.4.2"),
        ("DGCOD", "Volet spécifique aux appuis budgétaires", "Intégré — §5.4.1"),
        ("BNPVS", "Coordonnées responsables de projet + structure responsable", "Intégré — §5.2.1"),
        ("BNPVS", "Une seule structure désignée pour saisie d'un projet", "Intégré — §4.4 et §5.10"),
        ("BNPVS", "Traduire tous les termes anglais en français", "Intégré — §6.3"),
        ("ENSEA", "Plateforme usage interne uniquement — pas d'auto-inscription", "Intégré — §4.1"),
        ("ENSEA", "Définir profils et formaliser rôles", "Intégré — §4"),
        ("ENSEA", "Tableau de bord synthétique pour le Ministre", "Intégré — §4.2"),
        ("ENSEA", "Export vue synthétique KPI", "Intégré — §5.7"),
        ("ENSEA", "Barre de navigation rétractable", "Intégré — §5.10"),
        ("ENSEA", "Suivi ponctualité des saisies", "Intégré — §5.10"),
        ("ENSEA", "Taux de conversion contractuels à la date de signature", "Intégré — §5.4.1"),
        ("ENSEA", "Rédiger un cahier des charges", "Présent document"),
    ]
    big_table(doc,
        ["Structure", "Observation / Recommandation", "Statut d'intégration"],
        obs_data, col_widths=[2.8, 8.5, 5.2], font_size=8.5)

    # Annexe C — Glossaire
    doc.add_page_break()
    heading1(doc, "ANNEXE C — Glossaire des termes et définitions")
    separator(doc)
    glossaire = [
        ("Aide Publique au Développement (APD)", "Flux financiers publics provenant de gouvernements ou d'institutions multilatérales, accordés à des conditions concessionnelles à des pays en développement, dans le but de favoriser leur développement économique et social."),
        ("Appui budgétaire", "Mode de financement par lequel le bailleur transfère directement des ressources au budget de l'État bénéficiaire, sans affecter les fonds à des dépenses spécifiques prédéfinies."),
        ("Bailleur de fonds / PTF", "Institution publique ou privée (multilatérale, bilatérale, régionale, ONG, fonds thématique) qui finance des projets de développement dans un pays bénéficiaire."),
        ("Co-financement", "Situation dans laquelle un projet est financé simultanément par plusieurs bailleurs, chacun disposant de son propre accord de financement."),
        ("Contrepartie nationale", "Contribution financière de l'État ivoirien dans le cadre d'un projet co-financé avec un bailleur."),
        ("Décaissement", "Versement effectif d'une tranche du financement accordé à un projet, après réalisation des conditions suspensives prévues à l'accord."),
        ("Don", "Type de financement non remboursable accordé par un bailleur à un pays bénéficiaire."),
        ("Engagement / Montant engagé", "Montant total d'un accord de financement signé entre un bailleur et le gouvernement, représentant la promesse ferme de financement."),
        ("Gouverneur", "Représentant officiel d'un pays membre au sein du conseil des gouverneurs d'une institution financière internationale. Le gouverneur ivoirien représente la Côte d'Ivoire et vote au nom du pays lors des assemblées."),
        ("Pipeline", "Montants déjà engagés (accord signé) mais pas encore décaissés. Représente le potentiel de décaissement à venir."),
        ("Plan National de Développement (PND)", "Document stratégique pluriannuel élaboré par le Ministère du Plan et du Développement, définissant les priorités de développement de la Côte d'Ivoire et le cadre d'intervention des partenaires."),
        ("Point Focal", "Agent de l'administration désigné pour assurer le suivi opérationnel d'un ou plusieurs bailleurs de fonds et maintenir à jour les données de la plateforme."),
        ("Prêt concessionnel", "Prêt accordé à des taux d'intérêt inférieurs à ceux du marché, avec une composante de don significative."),
        ("Programme", "Ensemble cohérent d'interventions stratégiques contribuant à un même objectif de développement. Un programme peut comprendre plusieurs projets."),
        ("Projet", "Unité d'intervention spécifique disposant de ses propres objectifs, financements, indicateurs, dates et responsables."),
        ("Reste à décaisser", "Différence entre le montant total engagé et le montant total décaissé à une date donnée."),
        ("Retard", "Situation d'un projet en cours d'exécution dont la date de fin prévisionnelle est dépassée à la date d'analyse."),
        ("Taux de conversion contractuel", "Taux de change en vigueur à la date de signature de l'accord de financement, tel que défini contractuellement. Ce taux est utilisé pour les conversions en FCFA et ne varie pas au cours du projet."),
        ("Taux de décaissement (%)", "Ratio exprimant le montant décaissé en pourcentage du montant total engagé : (Décaissé / Engagé) × 100."),
        ("Taux d'avancement financier (%)", "Ratio exprimant le niveau d'exécution financière du projet, calculé à partir des dépenses réalisées sur le budget total."),
        ("Taux d'avancement physique (%)", "Estimation du niveau de réalisation des activités et livrables physiques du projet, renseigné par le Point Focal."),
        ("XOF / FCFA", "Franc CFA de l'Afrique de l'Ouest — monnaie officielle de la Côte d'Ivoire et des pays de l'UEMOA."),
    ]
    big_table(doc, ["Terme", "Définition"], glossaire, col_widths=[5, 11.5], font_size=9.5)


# ══════════════════════════════════════════════════════════════════════════════
#  POINT D'ENTRÉE PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def build_all():
    doc = Document()

    # Marges
    for sec in doc.sections:
        sec.top_margin    = Cm(2.5)
        sec.bottom_margin = Cm(2.5)
        sec.left_margin   = Cm(3.0)
        sec.right_margin  = Cm(2.5)

    # Police par défaut
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(10.5)

    cover_page(doc)
    doc.add_page_break()
    avant_propos(doc)
    doc.add_page_break()
    table_des_matieres(doc)
    doc.add_page_break()
    abreviations(doc)
    doc.add_page_break()
    section1(doc)
    doc.add_page_break()
    section2(doc)
    doc.add_page_break()
    section3(doc)
    doc.add_page_break()
    section4(doc)
    doc.add_page_break()
    section5(doc)
    doc.add_page_break()
    section6(doc)
    doc.add_page_break()
    section7(doc)
    doc.add_page_break()
    section8(doc)
    annexes(doc)

    output = 'Cahier_des_Charges_Plateforme_PTF_v2.docx'
    doc.save(output)
    print(f"✅  Document généré : {output}")
    return output


if __name__ == '__main__':
    build_all()
