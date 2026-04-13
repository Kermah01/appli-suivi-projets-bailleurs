"""
Script d'initialisation de la base de données de production.
À exécuter une seule fois après le premier déploiement.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User

def init_production():
    print("🚀 Initialisation de la base de données de production...")
    
    # Créer le superuser si il n'existe pas
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        print("✅ Compte admin créé (username: admin, password: admin123)")
        print("⚠️  IMPORTANT: Changez ce mot de passe après la première connexion!")
    else:
        print("ℹ️  Le compte admin existe déjà")
    
    print("\n✅ Initialisation terminée!")
    print("🌐 Vous pouvez maintenant vous connecter à l'application")

if __name__ == '__main__':
    init_production()
