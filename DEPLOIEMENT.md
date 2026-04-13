# 🚀 Guide de Déploiement sur Render

## Prérequis
- Un compte GitHub (gratuit)
- Un compte Render (gratuit)

## Étapes de déploiement

### 1. Pousser le code sur GitHub

```bash
# Initialiser git (si pas déjà fait)
git init
git add .
git commit -m "Préparation pour déploiement Render"

# Créer un nouveau repository sur GitHub, puis:
git remote add origin https://github.com/VOTRE-USERNAME/appli-suivi-projets.git
git branch -M main
git push -u origin main
```

### 2. Déployer sur Render

1. **Connectez-vous à Render** : https://dashboard.render.com/
2. **Cliquez sur "New +"** → **"Blueprint"**
3. **Connectez votre repository GitHub**
4. **Sélectionnez le repository** `appli-suivi-projets`
5. **Render détectera automatiquement** le fichier `render.yaml`
6. **Cliquez sur "Apply"**

Render va automatiquement :
- ✅ Créer une base de données PostgreSQL (gratuite)
- ✅ Déployer l'application web
- ✅ Exécuter les migrations
- ✅ Créer le compte admin (username: `admin`, password: `admin123`)

### 3. Accéder à l'application

Une fois le déploiement terminé (5-10 minutes) :
- **URL de l'application** : `https://appli-suivi-projets-bailleurs.onrender.com`
- **Connexion** : `admin` / `admin123`

⚠️ **IMPORTANT** : Changez le mot de passe admin après la première connexion !

## Gestion de la base de données

### Accéder à la base de données PostgreSQL

1. Dans le dashboard Render, allez dans **"Databases"**
2. Cliquez sur `appli-suivi-projets-db`
3. Vous verrez :
   - **Connection String** : URL complète de connexion
   - **Hostname**, **Port**, **Database**, **Username**, **Password**

### Sauvegarder la base de données

```bash
# Installer PostgreSQL client localement
# Puis exécuter:
pg_dump -h <hostname> -U <username> -d <database> > backup.sql
```

### Restaurer une sauvegarde

```bash
psql -h <hostname> -U <username> -d <database> < backup.sql
```

### Exporter les données depuis SQLite local vers PostgreSQL

```bash
# 1. Exporter depuis SQLite
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > data.json

# 2. Sur Render, via Shell:
python manage.py loaddata data.json
```

## Commandes utiles

### Accéder au shell Django sur Render

1. Dans le dashboard Render, allez dans votre service web
2. Cliquez sur **"Shell"** (en haut à droite)
3. Exécutez des commandes Django :

```bash
python manage.py shell
python manage.py createsuperuser
python manage.py migrate
```

### Voir les logs

Dans le dashboard Render → **"Logs"** (temps réel)

### Variables d'environnement

Dans le dashboard Render → **"Environment"** → **"Environment Variables"**

Variables automatiques :
- `DATABASE_URL` : URL PostgreSQL
- `SECRET_KEY` : Clé secrète générée
- `PYTHON_VERSION` : 3.11.0

Vous pouvez ajouter :
- `DEBUG=False` (pour désactiver le mode debug)
- `GEMINI_API_KEY=votre_clé` (si différente)

## Plan gratuit Render

- ✅ **Web Service** : 750 heures/mois (suffisant pour 1 app)
- ✅ **PostgreSQL** : 1 Go de stockage
- ⚠️ **Limitation** : L'app se met en veille après 15 min d'inactivité (redémarre en ~30s)
- ⚠️ **Données** : Sauvegardées pendant 90 jours après suppression

## Mettre à jour l'application

```bash
# Après avoir modifié le code localement:
git add .
git commit -m "Description des changements"
git push origin main
```

Render redéploiera automatiquement ! 🎉

## Support

- Documentation Render : https://render.com/docs
- Dashboard : https://dashboard.render.com/
