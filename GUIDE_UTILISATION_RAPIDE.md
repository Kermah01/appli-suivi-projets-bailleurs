# 📘 Guide de prise en main rapide
## Plateforme de Suivi des Projets Financés par les Bailleurs

---

## 🔐 Connexion

**URL** : https://appli-suivi-projets-bailleurs.onrender.com

**Identifiants de démonstration** :
- **Nom d'utilisateur** : `admin`
- **Mot de passe** : `admin123`

⚠️ Ces identifiants sont temporaires. En production, chaque utilisateur aura son propre compte.

---

## 🗺️ Structure de la plateforme

La plateforme est organisée autour d'une **barre latérale** (à gauche) qui donne accès à toutes les sections. Voici le détail de chaque onglet, dans l'ordre où ils apparaissent.

---

## 📌 Section « Navigation »

### 🖥️ Tableau de bord

C'est la page d'accueil après connexion. Elle offre une vue stratégique d'ensemble du portefeuille de projets.

**Indicateurs clés (KPI) en haut de page** :
- **Total projets** — nombre total de projets avec variation mensuelle (↗ ou ↘)
- **Bailleurs** — nombre de partenaires techniques et financiers
- **Total engagé** — montant total des engagements (en USD)
- **Total décaissé** — montant effectivement versé, avec taux de décaissement global
- **Projets en retard** — projets dont la date de fin prévue est dépassée

**3 onglets** sont disponibles sous les KPI :

#### Onglet « Synthèse »
Vue globale avec graphiques :
- **Engagements par bailleur** (Top 10) — graphique à barres horizontales
- **Répartition par statut** — graphique en donut (en cours, terminé, en retard, etc.)
- **Distribution par secteur** — treemap interactif (Santé, Éducation, Infrastructure, etc.)
- **Projets par bailleur** — graphique en barres

#### Onglet « Analyses avancées »
Analyses personnalisées avec filtres dynamiques :
- **Filtres disponibles** : bailleur, secteur, statut, période
- **Graphiques générés** : évolution temporelle, comparaisons entre bailleurs, répartition sectorielle
- Les graphiques se mettent à jour en temps réel quand on modifie les filtres

#### Onglet « Carte interactive »
Visualisation géographique des projets :
- **Carte Leaflet** avec contours des régions de Côte d'Ivoire
- Chaque région affiche le nombre de projets et les montants associés
- **Clic sur une région** : popup avec détails (nombre de projets, montants engagés et décaissés)
- Couleurs dynamiques selon l'intensité des engagements

---

### 📁 Projets

Gestion complète du portefeuille de projets.

**Page « Liste des projets »** :
- **Barre de recherche** : rechercher par code ou titre de projet
- **Filtres combinables** : statut (en cours, terminé, en retard, etc.), secteur, bailleur
- **Tableau** affichant : code, titre, bailleur(s), secteur, montant, taux d'avancement, statut
- **Badge « Cofinancé »** : apparaît quand un projet est financé par plusieurs bailleurs
- **Bouton « + Nouveau projet »** : créer un projet (réservé aux utilisateurs avec droits d'édition)

**Page « Détail d'un projet »** (accessible en cliquant sur un projet) :
- **Informations générales** : code, titre, description, secteur, dates (signature, début, fin prévue, fin effective), statut, taux d'avancement, zone géographique, responsable
- **Bailleurs** : liste de tous les bailleurs finançant le projet. Le bailleur principal est surligné en orange, les cofinanciers apparaissent en gris
- **Section « Cofinancement »** (si plusieurs bailleurs) :
  - Barres de progression montrant la part de chaque bailleur
  - **Graphique en donut** (ApexCharts) : répartition visuelle des engagements par bailleur
  - Pourcentages et montants détaillés
- **Indicateurs financiers** : montant total, montant engagé, montant décaissé, taux de décaissement, reste à décaisser
- **Avancement vs Décaissement** : comparaison visuelle entre l'avancement physique (%) et le taux de décaissement financier (%)
- **Alignement PND** : objectifs du Plan National de Développement auxquels le projet contribue
- **Historique des décaissements** : tableau chronologique des versements

**Page « Créer / Modifier un projet »** :
- **Informations générales** : code, titre, secteur, bailleur principal, devise, montant total, dates, statut, taux d'avancement, zone géographique, responsable, objectifs PND
- **Section « Financements »** (à la création) : ajout dynamique de un ou plusieurs financements :
  - Sélection du bailleur
  - Type de financement (Don, Prêt, Assistance technique, etc.)
  - Montant engagé
  - Devise
  - Bouton « Ajouter un financement » pour ajouter d'autres bailleurs (cofinancement)
  - Total des financements affiché en temps réel
- **Convertisseur FCFA** : conversion automatique du montant total en FCFA selon la devise choisie

---

### 🏦 Bailleurs

Répertoire des partenaires techniques et financiers.

**Page « Liste des bailleurs »** :
- **Tableau** : nom, sigle, type (multilatéral, bilatéral, régional), pays siège, nombre de projets, montant engagé, taux de décaissement
- Le **nombre de projets** compte tous les projets où le bailleur a un financement (pas seulement en tant que bailleur principal)
- **Bouton « + Nouveau bailleur »** : ajouter un partenaire

**Page « Détail d'un bailleur »** (en cliquant sur un bailleur) :
- **Informations institutionnelles** : nom complet, sigle, type, pays siège, catégorie institutionnelle
- **Statistiques financières** : montant total engagé, montant décaissé, taux de décaissement (avec jauge circulaire)
- **Liste des projets financés** : tableau de tous les projets où ce bailleur apporte un financement
  - Badge **« Cofinancé »** sur les projets partagés avec d'autres bailleurs
  - Colonnes : code, titre, secteur, montant, avancement, statut
- **6 panneaux d'analyse** :
  1. **Répartition par secteur** — graphique en donut
  2. **Évolution temporelle** — engagements et décaissements par année
  3. **Distribution par statut** — graphique en barres (en cours, terminé, etc.)
  4. **Taux de décaissement** — graphique radial par projet
  5. **Projets par région** — graphique en barres
  6. **Carte géographique** — carte Leaflet des projets par région

---

### 💰 Financements

Gestion des engagements financiers et des décaissements.

**Page « Liste des financements »** :
- **Tableau** : projet, bailleur, type de financement, montant engagé, devise, taux de décaissement, date d'accord
- **Filtres** : par bailleur, par type de financement
- **Bouton « + Nouveau financement »** : créer un engagement

**Types de financement disponibles** :
- Don
- Prêt concessionnel
- Prêt non concessionnel
- Assistance technique
- Cofinancement
- Contrepartie nationale
- Autre

**Page « Détail d'un financement »** :
- Informations : projet, bailleur, type, montant engagé, devise, date d'accord, référence, observations
- **Taux de décaissement** calculé automatiquement
- **Reste à décaisser**
- **Historique des décaissements** : tableau avec montant, date, référence, description
- **Bouton « + Ajouter un décaissement »** : enregistrer un nouveau versement
  - Saisir : montant, date, référence (optionnel), description (optionnel)
  - Le taux de décaissement est recalculé automatiquement après enregistrement

---

## 📌 Section « Stratégie »

### 🎯 Alignements sur le PND

Suivi de l'alignement des projets sur le Plan National de Développement.

**Page principale** :
- **Vue d'ensemble** du PND : nombre de piliers, objectifs, projets alignés
- **Piliers stratégiques** : liste des grands axes du PND
  - Clic sur un pilier → détail des sous-objectifs
  - Projets associés à chaque objectif
  - Statistiques : nombre de projets et montants par pilier

⚠️ **Note** : Les données PND actuellement affichées sont **fictives et provisoires**. Elles seront remplacées par les éléments officiels du PND 2026-2030 dès réception de la documentation.

---

## 📌 Section « Outils »

### 🤖 Assistant IA

Assistant intelligent alimenté par l'intelligence artificielle (Gemini).

**Fonctionnalités** :
- **Interface de chat** : poser des questions en langage naturel sur les projets et financements
- Exemples de questions :
  - « Quel est le taux de décaissement moyen des projets de la Banque Mondiale ? »
  - « Quels secteurs ont le plus de projets en retard ? »
  - « Comparez les engagements de l'AFD et de la BAD »
- L'assistant analyse les données de la plateforme en temps réel
- **Historique de conversation** sauvegardé localement

⚠️ **Note** : Cet onglet nécessite une clé API Gemini configurée. Si la clé n'est pas active, un message d'information s'affiche.

### 📥 Import Excel *(visible uniquement pour les administrateurs)*

Importation massive de données via fichier Excel standardisé.

**Fonctionnalités** :
- **Télécharger le modèle Excel** : fichier template pré-formaté avec 4 feuilles (Bailleurs, Projets, Financements, Décaissements)
- **Importer un fichier** : charger un fichier Excel rempli avec vos données
  - Validation automatique des formats et cohérence des données
  - **Rapport d'import** détaillé : lignes importées, erreurs, avertissements
  - **Prévisualisation** des données avant validation finale
- **Support du cofinancement** : plusieurs lignes de financement pour un même projet avec des bailleurs différents

**Structure du fichier Excel** :
- Feuille **Bailleurs** : nom, sigle, type, pays
- Feuille **Projets** : code, titre, secteur, bailleur principal, montant, dates, statut
- Feuille **Financements** : projet, bailleur, type, montant engagé, devise
- Feuille **Décaissements** : financement, montant, date, référence
- Instructions et exemples intégrés dans le fichier

---

## 📌 Section « Administration » *(visible uniquement pour les administrateurs)*

### 👥 Utilisateurs

Gestion des comptes utilisateurs et des permissions.

**Fonctionnalités** :
- **Liste des utilisateurs** avec statut (actif, en attente, désactivé)
- **Approbation** des nouvelles inscriptions
- **Attribution des rôles** :
  - **Administrateur** : accès complet à toutes les fonctionnalités
  - **Point focal bailleur** : peut modifier les projets de son bailleur uniquement
  - **Lecteur** : consultation uniquement, pas de modification
- **Activation / désactivation** de comptes

### ⚙️ Admin Django

Lien vers l'interface d'administration native de Django (réservé aux administrateurs techniques). Permet une gestion fine de la base de données.

---

## 🔍 Fonctionnalités transversales

### Recherche globale
- **Barre de recherche** en haut au centre de la barre de navigation
- Recherche instantanée sur les projets et bailleurs
- Résultats affichés en menu déroulant avec type (projet/bailleur), nom et sous-titre

### Notifications
- **Icône cloche** en haut à droite dans la barre de navigation
- Alertes automatiques : projets en retard, échéances proches
- Clic sur une notification → accès direct au projet concerné

### Conversions automatiques
- Tous les montants sont convertis en **FCFA** pour comparaison
- Taux de change intégrés : USD (615), EUR (655,96), GBP (775), JPY (4,10), CHF (685)
- Affichage dans la devise d'origine + équivalent FCFA

### Cofinancement
- Un projet peut avoir **plusieurs bailleurs**, chacun avec un type de financement différent
- La **répartition** est visible en pourcentage et en montants sur la fiche projet
- Un badge **« Cofinancé »** identifie visuellement les projets multi-bailleurs dans les listes

---

## ⚠️ Points d'attention (Version de démonstration)

| Élément | État actuel | État final |
|---------|-------------|------------|
| **Projets** | 20 projets fictifs | Projets réels du portefeuille |
| **Bailleurs** | 10 bailleurs réels, montants fictifs | Montants réels |
| **PND** | Piliers et objectifs fictifs | PND 2026-2030 officiel |
| **Identifiants** | admin / admin123 (unique) | Comptes individuels sécurisés |
| **Assistant IA** | Peut être inactif | Configuré avec clé API |

---

**Version** : 1.0 (Démonstration)
**Date** : Avril 2026
**Plateforme** : https://appli-suivi-projets-bailleurs.onrender.com
