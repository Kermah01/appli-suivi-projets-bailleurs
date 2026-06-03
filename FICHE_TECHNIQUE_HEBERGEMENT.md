# FICHE TECHNIQUE D'HÉBERGEMENT
## Plateforme de Suivi des Projets des Bailleurs de Fonds

---

**Document destiné à :** Service Informatique du Ministère  
**Objet :** Faisabilité d'hébergement sur serveur ministériel  
**Application :** Plateforme de Suivi des Projets cofinancés par les Partenaires Techniques et Financiers  
**Date :** Mai 2026  
**Version :** 1.0  

---

## 1. DESCRIPTION GÉNÉRALE DE L'APPLICATION

| Champ | Détail |
|---|---|
| **Nom de l'application** | Plateforme de Suivi des Projets des Bailleurs de Fonds |
| **Destinataires** | Cabinet du Ministère en charge de la Planification du Développement |
| **Nature** | Application web de gestion et de suivi |
| **Architecture** | Application web monolithique (backend + frontend intégrés) |
| **Type de déploiement** | Application serveur (hébergement dédié ou VPS) |
| **Accès** | Navigateur web — aucune installation côté client |
| **Langue** | Français |
| **Fuseau horaire** | Africa/Abidjan (UTC+0) |

### Fonctionnalités principales

- **Tableau de bord** : KPIs, graphiques interactifs (ECharts, ApexCharts), alertes temps réel, cartographie géographique (Leaflet.js)
- **Gestion des projets** : Suivi complet du cycle de vie des projets (identification → clôture), avancement physique et financier
- **Gestion des bailleurs** : Fiches bailleurs avec portefeuille de projets et logos
- **Financements & décaissements** : Suivi des engagements, décaissements, pipeline de validation, taux de décaissement
- **Alignement PND** : Couverture des piliers et sous-objectifs du Plan National de Développement
- **Assistant IA** : Interface conversationnelle propulsée par Google Gemini pour l'analyse des données
- **Import Excel** : Chargement en masse via fichier `.xlsx` (bailleurs, projets, financements, décaissements)
- **Export** : Exports Excel (`.xlsx`) et PDF des synthèses KPI et rapports
- **Gestion des utilisateurs** : Rôles différenciés, journal d'activité (audit log), approbation des comptes
- **Tableau de bord Ministre** : Vue ultra-synthétique et sécurisée pour la prise de décision

---

## 2. STACK TECHNOLOGIQUE

### 2.1 Backend

| Composant | Technologie | Version |
|---|---|---|
| **Langage** | Python | 3.11.x |
| **Framework web** | Django | ≥ 5.2, < 6.0 |
| **Serveur WSGI** | Gunicorn | ≥ 21.2.0 |
| **ORM** | Django ORM (natif) | — |
| **Adaptateur PostgreSQL** | psycopg2-binary | ≥ 2.9.9 |
| **Lecture/écriture Excel** | openpyxl | ≥ 3.1.0 |
| **Gestion des fichiers statiques** | WhiteNoise | ≥ 6.6.0 |
| **Parsing URL de base de données** | dj-database-url | ≥ 2.1.0 |
| **Client IA (Google Gemini)** | google-generativeai | ≥ 0.3.0 |

### 2.2 Frontend (servi par le backend, aucun build séparé)

| Composant | Technologie | Source |
|---|---|---|
| **Framework CSS** | TailwindCSS | CDN |
| **Graphiques analytiques** | Apache ECharts 5.5.0 | CDN |
| **Graphiques dashboard** | ApexCharts 3.44.0 | CDN |
| **Cartographie interactive** | Leaflet.js 1.9.4 | CDN |
| **Export côté client** | SheetJS (xlsx) 0.18.5 | CDN |
| **Capture écran** | html2canvas 1.4.1 | CDN |
| **Rendu Markdown** | marked.js | CDN |
| **Réactivité UI** | Alpine.js 3.x | CDN |
| **Polices** | Inter + Material Symbols | Google Fonts CDN |
| **Moteur de templates** | Django Templates (Jinja-compatible) | Natif |

> **Note importante :** Tous les assets frontend sont chargés depuis des CDN publics (jsDelivr, unpkg, Google).  
> **Si le réseau ministériel est fermé/filtré**, il faudra télécharger et héberger ces assets en local (voir §8).

### 2.3 Base de données

| Paramètre | Valeur |
|---|---|
| **Moteur** | PostgreSQL (recommandé en production) |
| **Version minimale recommandée** | PostgreSQL 14.x ou supérieur |
| **Alternative (développement/test)** | SQLite 3 (fichier local, non recommandé en production) |
| **Nom de la base** | `appli_suivi_projets` (configurable) |
| **Connexion** | Via variable d'environnement `DATABASE_URL` |
| **Persistance des sessions** | Base de données (table `django_session`) |

---

## 3. ARCHITECTURE APPLICATIVE

```
┌─────────────────────────────────────────────────────────────────┐
│                        NAVIGATEUR CLIENT                        │
│              (Chrome, Firefox, Edge — version récente)          │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (port 443)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   REVERSE PROXY (Nginx recommandé)              │
│          Gestion SSL/TLS, compression, fichiers statiques       │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTP (port interne, ex. 8000)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SERVEUR WSGI — Gunicorn                      │
│           Application Django (Python 3.11)                      │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────────┐   │
│  │dashboard │ projets  │bailleurs │financem. │  assistant   │   │
│  │ accounts │  imports │   pnd    │  alertes │  (IA/Gemini) │   │
│  └──────────┴──────────┴──────────┴──────────┴──────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQL / psycopg2
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BASE DE DONNÉES PostgreSQL                    │
│                  (même serveur ou serveur dédié)                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│               STOCKAGE FICHIERS (système de fichiers)           │
│   /media/ : logos bailleurs, pièces jointes projets (.pdf,      │
│             .docx, .xlsx, images)                               │
│   /static/ : CSS compilé, JS, images, GeoJSON                  │
└─────────────────────────────────────────────────────────────────┘
```

### Modules applicatifs Django

| Module | Rôle |
|---|---|
| `config` | Configuration centrale Django (settings, URLs, WSGI) |
| `dashboard` | Tableau de bord KPI, graphiques, export Excel/PDF |
| `projets` | CRUD projets, secteurs, programmes, pièces jointes |
| `bailleurs` | CRUD partenaires financiers (logos, catégories) |
| `financements` | Gestion engagements et décaissements |
| `pnd` | Plan National de Développement (piliers, sous-objectifs) |
| `accounts` | Authentification, rôles, audit log, gestion utilisateurs |
| `imports` | Moteur d'import Excel intelligent |
| `assistant` | Interface IA conversationnelle (Google Gemini API) |
| `alertes` | Système de notifications et alertes |

---

## 4. CONFIGURATION SYSTÈME REQUISE

### 4.1 Serveur d'application

| Ressource | Minimum | Recommandé |
|---|---|---|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 2 Go | 4 Go |
| **Disque OS + application** | 10 Go | 20 Go (SSD recommandé) |
| **Disque données (media)** | 10 Go | 50 Go (selon volume documents) |
| **OS** | Ubuntu 20.04 LTS / Debian 11 | Ubuntu 22.04 LTS |
| **Connexion réseau** | 10 Mbps | 100 Mbps |

> **Justification RAM :** Gunicorn avec workers synchrones. Recommandé : 2–4 workers = ~200 Mo/worker.

### 4.2 Serveur de base de données (peut être mutualisé)

| Ressource | Minimum | Recommandé |
|---|---|---|
| **CPU** | 2 vCPU | 4 vCPU |
| **RAM** | 1 Go | 4 Go |
| **Disque** | 5 Go | 20 Go (SSD) |
| **SGBD** | PostgreSQL 14 | PostgreSQL 15 ou 16 |

### 4.3 Logiciels à installer sur le serveur

```
- Python 3.11.x
- pip (gestionnaire de paquets Python)
- PostgreSQL 14+ (ou accès à un serveur PostgreSQL distant)
- Nginx (reverse proxy)
- Git (optionnel, pour les mises à jour)
- Certbot/Let's Encrypt (si certificat SSL à générer)
- libpq-dev (bibliothèque C pour psycopg2)
- gcc, build-essential (compilation Python)
```

---

## 5. VARIABLES D'ENVIRONNEMENT REQUISES

L'application est entièrement configurée par des variables d'environnement (aucun secret dans le code source).

| Variable | Obligatoire | Description | Exemple |
|---|---|---|---|
| `SECRET_KEY` | ✅ Oui | Clé secrète Django (cryptographie sessions/CSRF) | Chaîne aléatoire de 50+ caractères |
| `DATABASE_URL` | ✅ Oui | URL de connexion PostgreSQL | `postgres://user:pass@host:5432/dbname` |
| `DEBUG` | ✅ Oui | Mode debug (`False` en production) | `False` |
| `ALLOWED_HOSTS` | ✅ Oui | Domaine(s) autorisé(s) | `mon-domaine.gouv.ci` |
| `GEMINI_API_KEY` | ⚠️ Optionnel | Clé API Google Gemini (assistant IA) | Clé fournie par Google AI Studio |

> ⚠️ **Note sur GEMINI_API_KEY :** La fonctionnalité "Assistant IA" nécessite un accès internet sortant vers l'API Google Gemini (`generativelanguage.googleapis.com`). Si le réseau est cloisonné, cette fonctionnalité sera non disponible mais **l'application fonctionnera normalement** sur toutes les autres fonctions.

---

## 6. MODÈLE DE DONNÉES — SCHÉMA SIMPLIFIÉ

### Tables principales

| Table | Description | Champs clés |
|---|---|---|
| `auth_user` | Utilisateurs Django natifs | username, password, email, is_active |
| `accounts_userprofile` | Profils étendus | role, fonction, is_approved, bailleurs (M2M) |
| `accounts_activitylog` | Journal d'audit complet | user, action, model_name, timestamp |
| `bailleurs_bailleur` | Partenaires financiers | nom, sigle, type, catégorie, logo |
| `projets_secteur` | Secteurs d'activité | nom, code, couleur |
| `projets_programme` | Programmes stratégiques | code, nom, secteur, dates |
| `projets_projet` | Projets de développement | code, titre, statut, montant, taux_avancement, zone |
| `projets_piecejointe` | Documents joints aux projets | projet, type, fichier (upload) |
| `projets_responsablelocal` | Responsables terrain | projet, nom, région |
| `financements_financement` | Accords de financement | projet, bailleur, type, montant_engage, devise |
| `financements_decaissement` | Décaissements effectifs | financement, montant, date, référence |
| `pnd_plannational` | Plans Nationaux de Développement | nom, sigle, période |
| `pnd_pilier` | Piliers du PND | plan, numéro, nom |
| `pnd_sousobjectif` | Sous-objectifs du PND | pilier, numéro, nom |

### Relations clés

```
Bailleur ──< Financement >── Projet ──> Secteur
                 │                └──> Programme
                 └──< Décaissement     └──> SousObjectif(PND) [M2M]

User ──── UserProfile ──< Bailleur [M2M]
Projet ──< PièceJointe
Projet ──< ResponsableLocal
```

### Devises gérées

XOF (Franc CFA), USD, EUR, GBP, JPY, CHF, CNY, UC (Unité de Compte BAD)  
→ Conversion automatique vers FCFA intégrée dans l'application.

---

## 7. SÉCURITÉ

### Mécanismes en place

| Mécanisme | Description |
|---|---|
| **Authentification** | Système Django natif (hash bcrypt/PBKDF2) |
| **Gestion des sessions** | Sessions côté serveur (base de données), cookie `HttpOnly` |
| **Protection CSRF** | Middleware Django CSRF activé sur tous les formulaires |
| **Protection XSS** | Échappement automatique dans les templates Django |
| **En-têtes sécurité** | `SecurityMiddleware` Django (HSTS, X-Frame-Options, etc.) |
| **Contrôle d'accès** | RBAC (Role-Based Access Control) à 4 niveaux |
| **Audit log** | Toutes les actions CRUD sont journalisées avec horodatage |
| **Approbation des comptes** | Les nouveaux comptes requièrent validation par l'administrateur |

### Rôles utilisateurs

| Rôle | Accès |
|---|---|
| **Super Administrateur** | Accès total + gestion des utilisateurs |
| **Directeur / Haute fonction** | Lecture et modification de toutes les données |
| **Point Focal** | Modification limitée aux bailleurs qui lui sont assignés |
| **Lecteur** | Consultation seule (aucune modification) |

### Recommandations pour le déploiement sécurisé

- Activer HTTPS obligatoire (certificat SSL/TLS)
- Configurer `SECRET_KEY` unique et complexe (jamais partagée)
- Mettre `DEBUG=False` impérativement en production
- Restreindre l'accès à l'interface d'administration Django (`/admin/`) à des IPs spécifiques
- Configurer des sauvegardes automatiques de la base de données PostgreSQL
- Mettre en place un pare-feu applicatif (WAF) si disponible

---

## 8. STOCKAGE FICHIERS

| Répertoire | Contenu | Taille estimée |
|---|---|---|
| `/staticfiles/` | CSS, JS, images compilés (collectstatic) | ~5–10 Mo |
| `/media/bailleurs/logos/` | Logos des bailleurs (PNG/SVG) | ~50 Mo max |
| `/media/projets/*/pieces_jointes/` | Documents joints aux projets (PDF, DOCX, XLSX) | Variable — prévoir 10–50 Go selon usage |
| `/static/data/` | Fichier GeoJSON des régions de Côte d'Ivoire | ~2 Mo |

> **Politique de sauvegarde recommandée :** Sauvegarde quotidienne du répertoire `/media/` et de la base de données PostgreSQL.

---

## 9. RÉSEAU ET CONNECTIVITÉ

### Ports à ouvrir

| Port | Protocole | Direction | Usage |
|---|---|---|---|
| `443` | HTTPS | Entrant | Accès utilisateurs (HTTPS) |
| `80` | HTTP | Entrant | Redirection vers HTTPS |
| `5432` | PostgreSQL | Interne | Connexion app → base de données |
| `8000` | HTTP | Interne | Gunicorn (entre Nginx et l'app) |

### Connectivité internet sortante (optionnelle)

| Destination | Usage | Critique ? |
|---|---|---|
| `generativelanguage.googleapis.com` | Google Gemini IA | ❌ Non (fonctionnalité optionnelle) |
| `cdn.tailwindcss.com` | CSS Tailwind | ⚠️ Oui (sauf si hébergé en local) |
| `cdn.jsdelivr.net` | ECharts, ApexCharts, SheetJS, Alpine.js | ⚠️ Oui (sauf si hébergé en local) |
| `unpkg.com` | Leaflet.js | ⚠️ Oui (sauf si hébergé en local) |
| `fonts.googleapis.com` | Polices Inter + Material Symbols | ⚠️ Oui (sauf si hébergé en local) |

> **Si le réseau ministériel est isolé (pas d'accès internet)**, il est nécessaire de télécharger et héberger en local tous les assets CDN listés ci-dessus. Cette opération est réalisable et ne modifie pas le code applicatif de façon majeure.

---

## 10. PROCÉDURE DE DÉPLOIEMENT

### Étapes de mise en production

```bash
# 1. Cloner le dépôt ou copier les sources sur le serveur
# 2. Créer un environnement virtuel Python
python3.11 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
export SECRET_KEY="<clé-secrète-complexe>"
export DATABASE_URL="postgres://user:pass@localhost:5432/appli_suivi_projets"
export DEBUG="False"
export ALLOWED_HOSTS="mon-domaine.gouv.ci"

# 5. Initialiser la base de données
python manage.py migrate

# 6. Collecter les fichiers statiques
python manage.py collectstatic --no-input

# 7. Créer le compte administrateur
python manage.py createsuperuser

# 8. Démarrer le serveur applicatif
gunicorn config.wsgi:application --workers 3 --bind 0.0.0.0:8000
```

### Configuration Nginx (reverse proxy recommandé)

```nginx
server {
    listen 443 ssl;
    server_name mon-domaine.gouv.ci;

    ssl_certificate     /etc/ssl/certs/mon-domaine.crt;
    ssl_certificate_key /etc/ssl/private/mon-domaine.key;

    location /static/ {
        alias /chemin/vers/app/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias /chemin/vers/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
}
```

### Démarrage automatique (systemd)

```ini
# /etc/systemd/system/suivi-projets.service
[Unit]
Description=Plateforme Suivi Projets Bailleurs
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/chemin/vers/app
EnvironmentFile=/chemin/vers/.env
ExecStart=/chemin/vers/venv/bin/gunicorn config.wsgi:application --workers 3 --bind 127.0.0.1:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 11. PERFORMANCES ET MONTÉE EN CHARGE

| Indicateur | Valeur estimée |
|---|---|
| **Utilisateurs simultanés** | 10–50 (usage ministériel interne) |
| **Nombre de projets** | Plusieurs centaines (application légère) |
| **Temps de réponse cible** | < 2 secondes par page |
| **Workers Gunicorn recommandés** | 3 à 5 (formule : `2 × nb_CPU + 1`) |
| **Connexions DB max** | `conn_max_age=600` (pool de connexions actif) |

> L'application est conçue pour un usage interne ministériel. Elle n'est pas dimensionnée pour un accès grand public.

---

## 12. SAUVEGARDE ET RESTAURATION

### Stratégie recommandée

| Élément | Fréquence | Méthode |
|---|---|---|
| **Base de données PostgreSQL** | Quotidienne (nuit) | `pg_dump appli_suivi_projets > backup_$(date +%F).sql` |
| **Répertoire /media/** | Quotidienne | `rsync` ou `tar` vers stockage sécurisé |
| **Code source** | À chaque mise à jour | Versionné via Git |
| **Conservation des sauvegardes** | 30 jours minimum | — |

---

## 13. MISES À JOUR

La procédure de mise à jour est la suivante :

```bash
# 1. Sauvegarder la base de données avant toute mise à jour
# 2. Déployer les nouvelles sources
# 3. Installer les nouvelles dépendances (si ajoutées)
pip install -r requirements.txt
# 4. Appliquer les migrations de base de données
python manage.py migrate
# 5. Recollectar les fichiers statiques
python manage.py collectstatic --no-input
# 6. Redémarrer le service
systemctl restart suivi-projets
```

> Les mises à jour applicatives sont **sans perte de données** grâce au système de migrations Django.

---

## 14. RÉSUMÉ EXÉCUTIF — CHECKLIST POUR LE SERVICE INFORMATIQUE

| # | Élément | Statut |
|---|---|---|
| 1 | Serveur Linux (Ubuntu 22.04 LTS recommandé) | À provisionner |
| 2 | Python 3.11.x installé | À installer |
| 3 | PostgreSQL 14+ installé et configuré | À installer |
| 4 | Nginx installé (reverse proxy) | À installer |
| 5 | Certificat SSL/TLS disponible | À fournir |
| 6 | Variables d'environnement configurées | À configurer |
| 7 | Nom de domaine / IP fixe attribuée | À attribuer |
| 8 | Pare-feu configuré (ports 80, 443 entrants) | À configurer |
| 9 | Politique de sauvegarde automatique | À mettre en place |
| 10 | Accès CDN internet OU assets hébergés en local | À décider selon politique réseau |
| 11 | Clé API Google Gemini (si Assistant IA souhaité) | À obtenir (optionnel) |

---

## 15. CONTACT ET INFORMATIONS COMPLÉMENTAIRES

Pour toute question technique relative à l'application, se rapprocher du développeur de la plateforme ou du responsable de la Direction de la Planification ayant commandité le projet.

---

*Document généré à partir de l'analyse du code source de l'application — Mai 2026*
