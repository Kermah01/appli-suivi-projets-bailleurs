# 📋 Étapes pour déployer sur Render

## ✅ Préparation (TERMINÉE)

Tous les fichiers de configuration ont été créés :
- ✅ `requirements.txt` - Dépendances Python avec PostgreSQL
- ✅ `build.sh` - Script de build automatique
- ✅ `render.yaml` - Configuration Render (base de données + web service)
- ✅ `init_production.py` - Initialisation automatique du compte admin
- ✅ `.gitignore` - Fichiers à ignorer
- ✅ `config/settings.py` - Configuré pour production (PostgreSQL, WhiteNoise, variables d'environnement)
- ✅ Git initialisé et premier commit effectué

## 🚀 Prochaines étapes (À FAIRE)

### 1. Créer un repository GitHub

1. Allez sur https://github.com/new
2. Nom du repository : `appli-suivi-projets-bailleurs`
3. Visibilité : **Private** (recommandé) ou Public
4. **NE PAS** initialiser avec README, .gitignore ou licence
5. Cliquez sur **"Create repository"**

### 2. Pousser le code sur GitHub

Copiez et exécutez ces commandes dans le terminal :

```bash
cd c:\Users\MIVS\Appli_suivi_projets_bailleurs

# Remplacez VOTRE-USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/VOTRE-USERNAME/appli-suivi-projets-bailleurs.git

git branch -M main
git push -u origin main
```

### 3. Créer un compte Render (gratuit)

1. Allez sur https://render.com/
2. Cliquez sur **"Get Started for Free"**
3. Inscrivez-vous avec votre compte GitHub (recommandé)

### 4. Déployer avec Blueprint

1. Dans le dashboard Render : https://dashboard.render.com/
2. Cliquez sur **"New +"** → **"Blueprint"**
3. Connectez votre repository GitHub `appli-suivi-projets-bailleurs`
4. Render détectera automatiquement le fichier `render.yaml`
5. Donnez un nom au Blueprint : `appli-suivi-projets`
6. Cliquez sur **"Apply"**

### 5. Attendre le déploiement (5-10 minutes)

Render va automatiquement :
1. ✅ Créer une base PostgreSQL gratuite (1 Go)
2. ✅ Installer les dépendances Python
3. ✅ Collecter les fichiers statiques
4. ✅ Exécuter les migrations Django
5. ✅ Créer le compte admin automatiquement
6. ✅ Démarrer le serveur Gunicorn

### 6. Accéder à l'application

Une fois le déploiement terminé :
- **URL** : `https://appli-suivi-projets-bailleurs.onrender.com`
- **Login** : `admin`
- **Password** : `admin123`

⚠️ **IMPORTANT** : Changez le mot de passe immédiatement après la première connexion !

## 🔧 Configuration post-déploiement

### Ajouter la clé API Gemini (optionnel)

1. Dans Render Dashboard → Votre service web
2. **Environment** → **Environment Variables**
3. Ajoutez : `GEMINI_API_KEY` = `AIzaSyAVZyFImCQDNbBwXnLWpMSWcIGMakSijVQ`
4. Sauvegardez (l'app redémarrera automatiquement)

### Désactiver le mode DEBUG (recommandé pour production)

1. Dans Render Dashboard → Votre service web
2. **Environment** → **Environment Variables**
3. Ajoutez : `DEBUG` = `False`
4. Sauvegardez

## 📊 Gestion de la base de données PostgreSQL

### Voir les informations de connexion

1. Dashboard Render → **Databases** → `appli-suivi-projets-db`
2. Vous verrez :
   - **Internal Database URL** (pour l'app)
   - **External Database URL** (pour connexion externe)
   - Hostname, Port, Database, Username, Password

### Exécuter des commandes Django

1. Dans le service web → **Shell** (bouton en haut à droite)
2. Commandes utiles :

```bash
# Créer un nouveau superuser
python manage.py createsuperuser

# Charger des données
python manage.py loaddata data.json

# Accéder au shell Django
python manage.py shell

# Voir les migrations
python manage.py showmigrations
```

### Sauvegarder la base de données

```bash
# Exporter toutes les données (format JSON)
python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > backup.json

# Télécharger le fichier via le dashboard Render
```

### Restaurer une sauvegarde

```bash
# Dans le Shell Render
python manage.py loaddata backup.json
```

## 🔄 Mettre à jour l'application

Après avoir modifié le code localement :

```bash
git add .
git commit -m "Description des modifications"
git push origin main
```

Render redéploiera automatiquement en 2-3 minutes ! 🎉

## ⚠️ Limitations du plan gratuit

- **Web Service** : 750 heures/mois (suffisant pour 1 app)
- **PostgreSQL** : 1 Go de stockage, 90 jours de rétention
- **Mise en veille** : Après 15 min d'inactivité (redémarre en ~30s à la prochaine visite)
- **Builds** : Illimités mais peuvent être lents

## 📞 Support

- **Documentation Render** : https://render.com/docs
- **Dashboard** : https://dashboard.render.com/
- **Status** : https://status.render.com/

## 🎯 Checklist finale

- [ ] Repository GitHub créé
- [ ] Code poussé sur GitHub
- [ ] Compte Render créé
- [ ] Blueprint déployé
- [ ] Application accessible en ligne
- [ ] Connexion admin testée
- [ ] Mot de passe admin changé
- [ ] Clé API Gemini configurée (optionnel)
- [ ] Mode DEBUG désactivé (recommandé)
