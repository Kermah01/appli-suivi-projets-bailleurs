# Suivi des Projets Bailleurs — Application Django

Application web pour le suivi et l'analyse des projets de développement financés par les bailleurs de fonds, destinée au Cabinet du Ministère en charge de la Planification du Développement.

## Fonctionnalités

- **Tableau de bord** — KPIs, graphiques interactifs (Chart.js), alertes projets en retard
- **Gestion des projets** — CRUD complet, filtres multi-critères, suivi d'avancement et de décaissement
- **Gestion des bailleurs** — Fiche bailleur avec portefeuille de projets et financements
- **Financements & décaissements** — Suivi détaillé engagements/décaissements, taux de décaissement
- **Plan National de Développement (PND)** — Structure piliers/sous-objectifs, couverture par les projets, identification des gaps

## Architecture

| App | Rôle |
|---|---|
| `config` | Configuration Django |
| `dashboard` | Tableau de bord et indicateurs |
| `bailleurs` | Gestion des partenaires financiers |
| `projets` | Gestion des projets et secteurs |
| `financements` | Financements et décaissements |
| `pnd` | Plan National de Développement |

## Stack technique

- **Backend** : Django 5.2 / Python 3.11 / SQLite
- **Frontend** : TailwindCSS (CDN), Chart.js, Alpine.js
- **Base de données** : SQLite (dev), compatible PostgreSQL (prod)

## Installation

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data        # Données de démonstration
python manage.py createsuperuser  # Compte admin
python manage.py runserver
```

Accédez à l'application : http://127.0.0.1:8000

Interface d'administration : http://127.0.0.1:8000/admin/

## Compte admin par défaut (démo)

- **Utilisateur** : `admin`
- **Mot de passe** : `admin123`

## Structure des modèles

```
Bailleur (nom, sigle, type, pays)
  └── Financement (type, montant_engagé, devise)
        └── Décaissement (montant, date)

Secteur (nom, code, couleur)
  └── Projet (code, titre, statut, montant, avancement)
        └── objectifs_pnd → SousObjectif (M2M)

PlanNational (nom, période)
  └── Pilier (numéro, nom)
        └── SousObjectif (numéro, nom)
```
