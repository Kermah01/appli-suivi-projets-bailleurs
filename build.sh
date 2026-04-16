#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Initialiser les données de production (compte admin, etc.)
python init_production.py

# Créer les données de démonstration (optionnel, commentez si vous ne voulez pas)
python manage.py seed_data
