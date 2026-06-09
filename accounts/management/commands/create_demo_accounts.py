"""
Commande de gestion : crée les comptes de démo pour la présentation.

Usage :
    python manage.py create_demo_accounts
    python manage.py create_demo_accounts --reset   # recrée même s'ils existent
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone


DEMO_ACCOUNTS = [
    {
        'username': 'ministre',
        'password': 'Ministre@2026',
        'first_name': 'Monsieur le',
        'last_name': 'Ministre',
        'email': 'ministre@mivs.gouv.ci',
        'role': 'directeur',
        'fonction': 'ministre',
        'titre_poste': 'Ministre',
        'bailleurs': [],
    },
    {
        'username': 'dircab',
        'password': 'DirCab@2026',
        'first_name': 'Directeur de',
        'last_name': 'Cabinet',
        'email': 'dircab@mivs.gouv.ci',
        'role': 'superadmin',
        'fonction': 'dircab',
        'titre_poste': 'Directeur de Cabinet',
        'bailleurs': [],
    },
    {
        'username': 'pt_bad',
        'password': 'PointFocal@2026',
        'first_name': 'Point Focal',
        'last_name': 'BAD',
        'email': 'ptfocal.bad@mivs.gouv.ci',
        'role': 'point_focal',
        'fonction': 'point_focal',
        'titre_poste': 'Point Focal BAD',
        'bailleurs': ['BAD'],
    },
    {
        'username': 'pt_bm',
        'password': 'PointFocal@2026',
        'first_name': 'Point Focal',
        'last_name': 'Banque Mondiale',
        'email': 'ptfocal.bm@mivs.gouv.ci',
        'role': 'point_focal',
        'fonction': 'point_focal',
        'titre_poste': 'Point Focal Banque Mondiale',
        'bailleurs': ['BM', 'IDA'],
    },
    {
        'username': 'pt_afd',
        'password': 'PointFocal@2026',
        'first_name': 'Point Focal',
        'last_name': 'AFD',
        'email': 'ptfocal.afd@mivs.gouv.ci',
        'role': 'point_focal',
        'fonction': 'point_focal',
        'titre_poste': 'Point Focal AFD / France',
        'bailleurs': ['AFD'],
    },
    {
        'username': 'lecteur',
        'password': 'Lecteur@2026',
        'first_name': 'Utilisateur',
        'last_name': 'Lecture',
        'email': 'lecteur@mivs.gouv.ci',
        'role': 'lecteur',
        'fonction': 'charge_etudes',
        'titre_poste': "Chargé d'Études",
        'bailleurs': [],
    },
]


class Command(BaseCommand):
    help = "Crée les comptes de démo pour la présentation (ministre, dircab, points focaux)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Recrée les comptes même s\'ils existent déjà (réinitialise le mot de passe)'
        )

    def handle(self, *args, **options):
        from accounts.models import UserProfile
        from bailleurs.models import Bailleur

        reset = options['reset']
        created_count = 0
        updated_count = 0

        self.stdout.write(self.style.MIGRATE_HEADING('\n╔══════════════════════════════════════════╗'))
        self.stdout.write(self.style.MIGRATE_HEADING(  '║     CRÉATION DES COMPTES DE DÉMO         ║'))
        self.stdout.write(self.style.MIGRATE_HEADING(  '╚══════════════════════════════════════════╝\n'))

        for cfg in DEMO_ACCOUNTS:
            username = cfg['username']
            exists = User.objects.filter(username=username).exists()

            if exists and not reset:
                self.stdout.write(f"  ⏭  {username} — déjà existant (--reset pour réinitialiser)")
                continue

            if exists:
                user = User.objects.get(username=username)
                user.set_password(cfg['password'])
                user.first_name = cfg['first_name']
                user.last_name = cfg['last_name']
                user.email = cfg['email']
                user.is_active = True
                user.save()
                updated_count += 1
                action = "mise à jour"
            else:
                user = User.objects.create_user(
                    username=username,
                    password=cfg['password'],
                    first_name=cfg['first_name'],
                    last_name=cfg['last_name'],
                    email=cfg['email'],
                )
                created_count += 1
                action = "créé"

            # Profil
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = cfg['role']
            profile.fonction = cfg['fonction']
            profile.titre_poste = cfg['titre_poste']
            profile.is_approved = True
            profile.date_approbation = timezone.now()

            # Bailleurs associés (point focal)
            if cfg['bailleurs']:
                profile.save()
                for sigle in cfg['bailleurs']:
                    b = Bailleur.objects.filter(sigle__iexact=sigle).first()
                    if b:
                        profile.bailleurs.add(b)
                        self.stdout.write(f"       → Bailleur associé : {b.sigle} — {b.nom[:40]}")
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"       ⚠ Bailleur '{sigle}' non trouvé en base — associer manuellement")
                        )
            else:
                profile.save()

            role_label = dict(UserProfile.ROLE_CHOICES).get(cfg['role'], cfg['role'])
            self.stdout.write(
                self.style.SUCCESS(f"  ✅  {username} ({action}) — {role_label} | {cfg['titre_poste']}")
            )
            self.stdout.write(f"       Mot de passe : {cfg['password']}")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f"Terminé : {created_count} compte(s) créé(s), {updated_count} mis à jour."))
        self.stdout.write('')
        self.stdout.write(self.style.MIGRATE_HEADING('─── RÉCAPITULATIF CONNEXIONS ──────────────────────'))
        self.stdout.write(f"  {'COMPTE':<15} {'MOT DE PASSE':<22} {'ACCÈS'}")
        self.stdout.write(f"  {'─'*15} {'─'*22} {'─'*30}")
        for cfg in DEMO_ACCOUNTS:
            role_label = dict(UserProfile.ROLE_CHOICES).get(cfg['role'], cfg['role'])
            self.stdout.write(f"  {cfg['username']:<15} {cfg['password']:<22} {role_label}")
        self.stdout.write('')
