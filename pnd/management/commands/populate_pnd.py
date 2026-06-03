"""
Commande Django : populate_pnd
Crée ou met à jour le PND avec les 6 piliers et axes stratégiques officiels.
Usage : python manage.py populate_pnd
"""
from django.core.management.base import BaseCommand
from pnd.models import PlanNational, Pilier, SousObjectif

PND_DATA = {
    'nom': 'Plan National de Développement',
    'sigle': 'PND',
    'annee_debut': 2025,
    'annee_fin': 2030,
    'description': "Plan National de Développement de la Côte d'Ivoire",
    'piliers': [
        {
            'numero': 1,
            'nom': 'Paix, sécurité et stabilité durables',
            'description': (
                "Ce pilier constitue le socle du développement du pays et vise à adapter "
                "le dispositif national aux exigences sécuritaires et géopolitiques actuelles."
            ),
            'axes': [
                'Préservation de la stabilité politique et sociale.',
                'Renforcement des capacités de prévention, d\'anticipation et de réponse rapide.',
                'Renforcement de l\'efficacité des institutions en charge de la protection civile.',
            ],
        },
        {
            'numero': 2,
            'nom': (
                "Modernisation de l'agriculture, consolidation de la sécurisation foncière rurale, "
                "accroissement de la productivité et renforcement des chaînes de valeurs agricoles"
            ),
            'description': (
                "Ce pilier cherche à transformer l'agriculture, l'élevage et la pêche en secteurs "
                "modernes, compétitifs, résilients et souverains."
            ),
            'axes': [
                'Renforcement de la gouvernance du secteur agricole.',
                'Accélération de la modernisation agricole et résilience de l\'agriculture.',
                'Renforcement de la sécurisation foncière agricole.',
                'Promotion de la valorisation des productions agricoles, animales et halieutiques dans un environnement de contribution accrue du secteur privé.',
                'Stratégie d\'utilisation concertée/conjuguée des eaux de surface et souterraines pour l\'irrigation.',
                'Renforcement de la sécurité et de la souveraineté alimentaires.',
                'Développement de l\'économie circulaire.',
            ],
        },
        {
            'numero': 3,
            'nom': "Promotion de l'investissement privé, des champions nationaux et réduction de l'informalité",
            'description': (
                "L'objectif est d'asseoir un nouveau pacte avec les entreprises pour faire du secteur "
                "privé le moteur principal de l'industrialisation et de la croissance."
            ),
            'axes': [
                'Accélération et renforcement de l\'industrialisation.',
                'Renforcement de l\'appui aux opérateurs économiques locaux.',
                'Incubation et émergence de champions nationaux compétitifs.',
                'Attraction et optimisation des Investissements Directs Étrangers (IDE).',
                'Accélération de la réduction de l\'informalité de l\'économie.',
            ],
        },
        {
            'numero': 4,
            'nom': "Développement du capital humain, des compétences et création d'emplois décents",
            'description': (
                "Il vise à bâtir une population qualifiée, en bonne santé et épanouie pour répondre "
                "directement aux besoins de l'économie moderne et de l'industrialisation."
            ),
            'axes': [
                'Développement d\'un système éducatif performant (intégrant les principes de l\'économie circulaire).',
                'Renforcement de l\'employabilité des jeunes et création d\'emplois décents.',
                'Promotion de l\'adéquation compétence-emploi.',
                'Amélioration de la santé et du bien-être des populations.',
                'Renforcement de la sécurité nutritionnelle.',
                'Promotion de l\'égalité de genre et de l\'autonomisation des femmes.',
                'Renforcement de l\'inclusion sociale.',
            ],
        },
        {
            'numero': 5,
            'nom': (
                "Développement des infrastructures stratégiques et des pôles économiques régionaux, "
                "transition écologique, résilience climatique et économie circulaire"
            ),
            'description': (
                "Ce pilier cherche à corriger les disparités géographiques en équipant les villes "
                "secondaires et en verdissant le développement territorial."
            ),
            'axes': [
                'Renforcement des infrastructures stratégiques.',
                'Développement des pôles économiques régionaux comme moteurs de croissance territoriale.',
                'Aménagement équilibré du territoire à travers le développement des villes secondaires et l\'élargissement de l\'accès aux services publics.',
                'Intégration de la transition écologique dans le développement et la promotion d\'une économie verte et résiliente.',
                'Développement d\'une économie circulaire pour l\'autonomisation et la résilience des territoires.',
            ],
        },
        {
            'numero': 6,
            'nom': "Promotion de la bonne gouvernance et modernisation de l'État",
            'description': (
                "Il cible l'avènement d'une administration publique transparente, décentralisée et "
                "axée sur la redevabilité et la performance."
            ),
            'axes': [
                'Renforcement de la gouvernance administrative, locale et judiciaire.',
                'Renforcement de la gouvernance économique et financière.',
                'Amélioration de la mobilisation des ressources et du financement de l\'économie.',
            ],
        },
    ],
}


class Command(BaseCommand):
    help = "Crée ou met à jour le PND avec les 6 piliers et axes stratégiques officiels."

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Supprime et recrée tous les piliers/axes (attention : efface les liens projets-PND)',
        )

    def handle(self, *args, **options):
        plan, created = PlanNational.objects.get_or_create(
            sigle=PND_DATA['sigle'],
            defaults={
                'nom': PND_DATA['nom'],
                'annee_debut': PND_DATA['annee_debut'],
                'annee_fin': PND_DATA['annee_fin'],
                'description': PND_DATA['description'],
                'actif': True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f"Plan '{plan}' créé."))
        else:
            plan.nom = PND_DATA['nom']
            plan.annee_debut = PND_DATA['annee_debut']
            plan.annee_fin = PND_DATA['annee_fin']
            plan.description = PND_DATA['description']
            plan.actif = True
            plan.save()
            self.stdout.write(f"Plan '{plan}' mis à jour.")

        if options['reset']:
            plan.piliers.all().delete()
            self.stdout.write(self.style.WARNING("Piliers et axes existants supprimés."))

        for p_data in PND_DATA['piliers']:
            pilier, p_created = Pilier.objects.update_or_create(
                plan=plan,
                numero=p_data['numero'],
                defaults={
                    'nom': p_data['nom'],
                    'description': p_data['description'],
                },
            )
            action = "créé" if p_created else "mis à jour"
            self.stdout.write(f"  Pilier {pilier.numero} {action}.")

            for i, axe_nom in enumerate(p_data['axes'], 1):
                axe_num = f"Axe {i}"
                SousObjectif.objects.update_or_create(
                    pilier=pilier,
                    numero=axe_num,
                    defaults={'nom': axe_nom},
                )

        nb_piliers = plan.piliers.count()
        nb_axes = SousObjectif.objects.filter(pilier__plan=plan).count()
        self.stdout.write(self.style.SUCCESS(
            f"\nPND mis à jour : {nb_piliers} piliers, {nb_axes} axes stratégiques."
        ))
