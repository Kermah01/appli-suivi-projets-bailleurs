# FICHE DE SIZING — HÉBERGEMENT SERVEUR
## Plateforme de Suivi des Projets des Bailleurs de Fonds

**Destinataire :** Service Informatique du Ministère  
**Date :** Mai 2026  

---

## 1. RESSOURCES MATÉRIELLES

### 1.1 Serveur d'application (héberge l'application web)

| Ressource | Minimum requis | Recommandé (production) |
|---|---|---|
| **vCPU** | 2 vCPU | 4 vCPU |
| **RAM** | 2 Go | 4 Go |
| **Stockage OS + application** | 10 Go SSD | 20 Go SSD |
| **Stockage données (fichiers uploadés)** | 20 Go HDD/SSD | 50 Go SSD |
| **Bande passante réseau** | 10 Mbps | 100 Mbps |

> **Justification CPU/RAM :** L'application tourne avec Gunicorn (serveur WSGI Python). La formule de dimensionnement standard est `2 × nb_vCPU + 1` workers. Avec 4 vCPU → 9 workers max, chaque worker consomme environ 150–200 Mo de RAM. Pour 10 à 50 utilisateurs simultanés (usage interne ministériel), 4 Go de RAM sont largement suffisants.

> **Justification stockage :** Le répertoire `/media/` accueille les logos des bailleurs (PNG/SVG) et les pièces jointes des projets (PDF, DOCX, XLSX). Le volume est proportionnel au nombre de documents attachés. 50 Go offre une marge confortable pour plusieurs années d'exploitation.

---

### 1.2 Serveur de base de données

> Peut être mutualisé sur le même serveur physique si les ressources le permettent.

| Ressource | Minimum requis | Recommandé (production) |
|---|---|---|
| **vCPU** | 2 vCPU | 4 vCPU |
| **RAM** | 1 Go | 4 Go |
| **Stockage base de données** | 5 Go SSD | 20 Go SSD |
| **Bande passante réseau** | Réseau interne LAN | Réseau interne LAN |

> **Justification :** La base de données héberge des tables structurées de taille modérée (projets, financements, décaissements, utilisateurs, audit log). Pour plusieurs centaines de projets et des milliers d'enregistrements, le volume de données reste inférieur à 1 Go. 20 Go couvrent plusieurs années avec une grande marge.

---

### 1.3 Récapitulatif — Configuration cible (serveur unique mutualisé)

> Si un seul serveur doit tout héberger (application + base de données) :

| Ressource | Configuration cible |
|---|---|
| **vCPU** | **4 vCPU** |
| **RAM** | **8 Go** |
| **Stockage** | **80 Go SSD** (OS 20 Go + App 10 Go + BDD 10 Go + Media 40 Go) |
| **Bande passante** | **100 Mbps** |
| **Type de disque** | SSD (obligatoire pour la base de données) |

---

## 2. RESSOURCES LOGICIELLES

### 2.1 Système d'exploitation

| Composant | Valeur retenue |
|---|---|
| **OS recommandé** | Ubuntu Server 22.04 LTS (Jammy Jellyfish) |
| **Alternative** | Debian 12 (Bookworm) |
| **Architecture** | x86_64 (64 bits) |
| **Mode** | Serveur (sans interface graphique) |

---

### 2.2 Runtimes applicatifs

| Runtime | Version requise | Notes |
|---|---|---|
| **Python** | **3.11.x** | Version exacte requise par l'application |
| **pip** | ≥ 23.x | Gestionnaire de paquets Python |
| **virtualenv / venv** | Natif Python 3.11 | Isolation de l'environnement |

> ⚠️ Python 3.11 est impératif. Les versions 3.12+ peuvent être utilisées mais nécessitent une vérification de compatibilité. Python 3.10 et inférieurs ne sont **pas supportés**.

---

### 2.3 Moteur de base de données

| Composant | Valeur retenue |
|---|---|
| **SGBD** | **PostgreSQL** |
| **Version minimale** | PostgreSQL 14 |
| **Version recommandée** | PostgreSQL 15 ou 16 |
| **Pilote Python** | psycopg2-binary ≥ 2.9.9 (installé automatiquement via pip) |
| **Dépendance système** | `libpq-dev` (bibliothèque client PostgreSQL) |
| **Encodage** | UTF-8 |
| **Nom de la base** | `appli_suivi_projets` (configurable) |

> ❌ MySQL / MariaDB **non supportés** — l'application est conçue exclusivement pour PostgreSQL en production.  
> ℹ️ SQLite est disponible uniquement pour les tests locaux, pas pour la production.

---

### 2.4 Serveur web / Reverse proxy

| Composant | Rôle | Version |
|---|---|---|
| **Nginx** | Reverse proxy, SSL/TLS, fichiers statiques | ≥ 1.18 |
| **Gunicorn** | Serveur WSGI Python (interface entre Nginx et Django) | ≥ 21.2.0 |

**Flux :** `Navigateur → Nginx (HTTPS:443) → Gunicorn (HTTP:8000) → Django`

> Gunicorn est installé automatiquement via `pip install -r requirements.txt`. Nginx doit être installé séparément via le gestionnaire de paquets système.

---

### 2.5 Dépendances système (packages Linux à installer)

```bash
apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3.11-dev \
    python3-pip \
    libpq-dev \
    gcc \
    build-essential \
    nginx \
    postgresql \
    postgresql-contrib \
    curl \
    git
```

---

### 2.6 Dépendances Python (installées automatiquement)

Toutes les dépendances Python sont définies dans le fichier `requirements.txt` et s'installent avec une seule commande :

```bash
pip install -r requirements.txt
```

| Paquet Python | Version | Usage |
|---|---|---|
| `django` | ≥ 5.2, < 6.0 | Framework web principal |
| `gunicorn` | ≥ 21.2.0 | Serveur WSGI de production |
| `psycopg2-binary` | ≥ 2.9.9 | Connecteur PostgreSQL |
| `openpyxl` | ≥ 3.1.0 | Lecture/écriture fichiers Excel (.xlsx) |
| `whitenoise` | ≥ 6.6.0 | Service des fichiers statiques |
| `dj-database-url` | ≥ 2.1.0 | Parsing URL de connexion base de données |
| `google-generativeai` | ≥ 0.3.0 | Client API Google Gemini (Assistant IA) |

---

### 2.7 Protocoles et ports réseau requis

| Port | Protocole | Direction | Usage |
|---|---|---|---|
| **443** | HTTPS/TLS | Entrant | Accès navigateurs (production) |
| **80** | HTTP | Entrant | Redirection automatique vers HTTPS |
| **5432** | TCP | Interne serveur | Communication Django ↔ PostgreSQL |
| **8000** | HTTP | Interne serveur | Communication Nginx ↔ Gunicorn |

---

### 2.8 Certificat SSL/TLS

Un certificat SSL/TLS est **obligatoire** pour la mise en production.

| Option | Description |
|---|---|
| **Certificat ministériel** | Si le Ministère dispose d'une autorité de certification interne (PKI) — solution préférée |
| **Let's Encrypt (Certbot)** | Certificat gratuit et automatique si le serveur a accès à internet |
| **Certificat commercial** | Achat auprès d'un tiers de confiance (DigiCert, Sectigo, etc.) |

---

## 3. RÉCAPITULATIF GLOBAL

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FICHE DE SIZING — RÉSUMÉ                         │
├──────────────────────────┬──────────────────────────────────────────┤
│  MATÉRIEL                │                                          │
│  vCPU                    │  4 vCPU (minimum : 2)                    │
│  RAM                     │  8 Go  (minimum : 4 Go)                  │
│  Stockage                │  80 Go SSD (minimum : 40 Go)             │
│  Bande passante          │  100 Mbps                                │
├──────────────────────────┼──────────────────────────────────────────┤
│  LOGICIEL                │                                          │
│  Système d'exploitation  │  Ubuntu Server 22.04 LTS (x86_64)       │
│  Langage                 │  Python 3.11.x                           │
│  Framework               │  Django 5.2 (installé via pip)          │
│  Serveur WSGI            │  Gunicorn 21.2+ (installé via pip)      │
│  Reverse proxy           │  Nginx ≥ 1.18                           │
│  Base de données         │  PostgreSQL 15 ou 16                     │
│  SSL/TLS                 │  Certificat requis (PKI interne ou CA)   │
├──────────────────────────┼──────────────────────────────────────────┤
│  CONNECTIVITÉ            │                                          │
│  Ports entrants          │  80 (HTTP), 443 (HTTPS)                 │
│  Ports internes          │  5432 (PostgreSQL), 8000 (Gunicorn)     │
│  Internet sortant        │  Optionnel (requis pour l'Assistant IA)  │
└──────────────────────────┴──────────────────────────────────────────┘
```

---

*Document établi sur la base de l'analyse du code source de l'application — Mai 2026*
