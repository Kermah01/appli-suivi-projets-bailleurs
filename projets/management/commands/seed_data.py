import random
from datetime import date, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from bailleurs.models import Bailleur
from projets.models import Secteur, Projet
from financements.models import Financement, Decaissement
from pnd.models import PlanNational, Pilier, SousObjectif


class Command(BaseCommand):
    help = "Génère des données de démonstration pour l'application"

    def handle(self, *args, **options):
        self.stdout.write("Création des données de démonstration...")

        # Bailleurs
        bailleurs_data = [
            {'nom': 'Banque Mondiale', 'sigle': 'BM', 'type_bailleur': 'multilateral', 'pays_siege': 'États-Unis'},
            {'nom': 'Banque Africaine de Développement', 'sigle': 'BAD', 'type_bailleur': 'regional', 'pays_siege': 'Côte d\'Ivoire'},
            {'nom': 'Union Européenne', 'sigle': 'UE', 'type_bailleur': 'multilateral', 'pays_siege': 'Belgique'},
            {'nom': 'Agence Française de Développement', 'sigle': 'AFD', 'type_bailleur': 'bilateral', 'pays_siege': 'France'},
            {'nom': 'Programme des Nations Unies pour le Développement', 'sigle': 'PNUD', 'type_bailleur': 'multilateral', 'pays_siege': 'États-Unis'},
            {'nom': 'Fonds Monétaire International', 'sigle': 'FMI', 'type_bailleur': 'multilateral', 'pays_siege': 'États-Unis'},
            {'nom': 'Coopération Allemande (GIZ)', 'sigle': 'GIZ', 'type_bailleur': 'bilateral', 'pays_siege': 'Allemagne'},
            {'nom': 'Banque Islamique de Développement', 'sigle': 'BID', 'type_bailleur': 'multilateral', 'pays_siege': 'Arabie Saoudite'},
            {'nom': 'Japan International Cooperation Agency', 'sigle': 'JICA', 'type_bailleur': 'bilateral', 'pays_siege': 'Japon'},
            {'nom': 'Fonds Koweïtien pour le Développement', 'sigle': 'FKDEA', 'type_bailleur': 'bilateral', 'pays_siege': 'Koweït'},
        ]
        bailleurs = []
        for data in bailleurs_data:
            b, _ = Bailleur.objects.get_or_create(sigle=data['sigle'], defaults=data)
            bailleurs.append(b)
        self.stdout.write(f"  {len(bailleurs)} bailleurs créés")

        # Secteurs
        secteurs_data = [
            {'nom': 'Santé', 'code': 'SAN', 'couleur': '#ef4444'},
            {'nom': 'Éducation', 'code': 'EDU', 'couleur': '#3b82f6'},
            {'nom': 'Agriculture', 'code': 'AGR', 'couleur': '#22c55e'},
            {'nom': 'Infrastructure & Transport', 'code': 'INF', 'couleur': '#f59e0b'},
            {'nom': 'Énergie', 'code': 'ENE', 'couleur': '#f97316'},
            {'nom': 'Eau & Assainissement', 'code': 'EAU', 'couleur': '#06b6d4'},
            {'nom': 'Gouvernance', 'code': 'GOV', 'couleur': '#8b5cf6'},
            {'nom': 'Environnement & Climat', 'code': 'ENV', 'couleur': '#84cc16'},
            {'nom': 'Développement Urbain', 'code': 'URB', 'couleur': '#ec4899'},
            {'nom': 'Protection Sociale', 'code': 'SOC', 'couleur': '#6366f1'},
        ]
        secteurs = []
        for data in secteurs_data:
            s, _ = Secteur.objects.get_or_create(code=data['code'], defaults=data)
            secteurs.append(s)
        self.stdout.write(f"  {len(secteurs)} secteurs créés")

        # PND
        pnd, _ = PlanNational.objects.get_or_create(
            sigle='PND',
            defaults={
                'nom': 'Plan National de Développement',
                'annee_debut': 2026,
                'annee_fin': 2030,
                'description': 'Plan stratégique quinquennal pour la transformation structurelle de l\'économie et l\'amélioration des conditions de vie des populations.',
                'actif': True,
            }
        )

        piliers_data = [
            {
                'numero': 1, 'nom': 'Capital humain et inclusion sociale',
                'description': 'Renforcer le capital humain et promouvoir l\'inclusion sociale.',
                'sous_objectifs': [
                    '1.1 - Améliorer l\'accès et la qualité de l\'éducation',
                    '1.2 - Renforcer le système de santé',
                    '1.3 - Promouvoir la protection sociale',
                    '1.4 - Améliorer l\'accès à l\'eau potable et à l\'assainissement',
                ]
            },
            {
                'numero': 2, 'nom': 'Transformation économique et création d\'emplois',
                'description': 'Accélérer la transformation structurelle de l\'économie.',
                'sous_objectifs': [
                    '2.1 - Moderniser l\'agriculture et l\'élevage',
                    '2.2 - Développer les infrastructures économiques',
                    '2.3 - Promouvoir l\'industrialisation',
                    '2.4 - Développer le secteur privé et l\'emploi des jeunes',
                ]
            },
            {
                'numero': 3, 'nom': 'Gouvernance, paix et sécurité',
                'description': 'Renforcer la gouvernance et consolider la paix.',
                'sous_objectifs': [
                    '3.1 - Renforcer la gouvernance administrative et économique',
                    '3.2 - Moderniser la gestion des finances publiques',
                    '3.3 - Consolider la paix et la cohésion sociale',
                ]
            },
            {
                'numero': 4, 'nom': 'Développement durable et résilience climatique',
                'description': 'Assurer un développement durable et résilient face au changement climatique.',
                'sous_objectifs': [
                    '4.1 - Protéger l\'environnement et les ressources naturelles',
                    '4.2 - Renforcer la résilience climatique',
                    '4.3 - Promouvoir les énergies renouvelables',
                ]
            },
        ]

        all_sous_objectifs = []
        for p_data in piliers_data:
            pilier, _ = Pilier.objects.get_or_create(
                plan=pnd, numero=p_data['numero'],
                defaults={'nom': p_data['nom'], 'description': p_data['description']}
            )
            for so_text in p_data['sous_objectifs']:
                numero = so_text.split(' - ')[0]
                nom = so_text.split(' - ')[1]
                so, _ = SousObjectif.objects.get_or_create(
                    pilier=pilier, numero=numero,
                    defaults={'nom': nom}
                )
                all_sous_objectifs.append(so)
        self.stdout.write(f"  PND avec {len(piliers_data)} piliers et {len(all_sous_objectifs)} sous-objectifs créés")

        # Projets avec zones géographiques
        projets_data = [
            {'code': 'PRJ-001', 'titre': 'Programme d\'appui au secteur de la santé', 'secteur': 'SAN', 'bailleur': 'BM', 'montant': 45000000, 'statut': 'en_cours', 'avancement': 62, 'zone': 'Abidjan'},
            {'code': 'PRJ-002', 'titre': 'Projet de renforcement du système éducatif', 'secteur': 'EDU', 'bailleur': 'AFD', 'montant': 28000000, 'statut': 'en_cours', 'avancement': 45, 'zone': 'Bouaké'},
            {'code': 'PRJ-003', 'titre': 'Projet d\'appui à la modernisation agricole', 'secteur': 'AGR', 'bailleur': 'BAD', 'montant': 35000000, 'statut': 'en_cours', 'avancement': 30, 'zone': 'Korhogo'},
            {'code': 'PRJ-004', 'titre': 'Programme routier national - Phase 2', 'secteur': 'INF', 'bailleur': 'BM', 'montant': 120000000, 'statut': 'en_cours', 'avancement': 55, 'zone': 'National'},
            {'code': 'PRJ-005', 'titre': 'Projet d\'électrification rurale', 'secteur': 'ENE', 'bailleur': 'BAD', 'montant': 60000000, 'statut': 'en_cours', 'avancement': 25, 'zone': 'Man'},
            {'code': 'PRJ-006', 'titre': 'Programme d\'accès à l\'eau potable', 'secteur': 'EAU', 'bailleur': 'UE', 'montant': 22000000, 'statut': 'en_cours', 'avancement': 70, 'zone': 'Daloa'},
            {'code': 'PRJ-007', 'titre': 'Appui à la gouvernance et modernisation de l\'État', 'secteur': 'GOV', 'bailleur': 'PNUD', 'montant': 8000000, 'statut': 'en_cours', 'avancement': 50, 'zone': 'Yamoussoukro'},
            {'code': 'PRJ-008', 'titre': 'Projet de gestion durable des forêts', 'secteur': 'ENV', 'bailleur': 'GIZ', 'montant': 15000000, 'statut': 'en_cours', 'avancement': 40, 'zone': 'San-Pédro'},
            {'code': 'PRJ-009', 'titre': 'Programme de développement urbain de la capitale', 'secteur': 'URB', 'bailleur': 'AFD', 'montant': 50000000, 'statut': 'preparation', 'avancement': 10, 'zone': 'Abidjan'},
            {'code': 'PRJ-010', 'titre': 'Filet social productif', 'secteur': 'SOC', 'bailleur': 'BM', 'montant': 30000000, 'statut': 'en_cours', 'avancement': 80, 'zone': 'Gagnoa'},
            {'code': 'PRJ-011', 'titre': 'Projet d\'appui au secteur de l\'énergie solaire', 'secteur': 'ENE', 'bailleur': 'BID', 'montant': 40000000, 'statut': 'negociation', 'avancement': 5, 'zone': 'Odienné'},
            {'code': 'PRJ-012', 'titre': 'Programme de formation professionnelle des jeunes', 'secteur': 'EDU', 'bailleur': 'UE', 'montant': 18000000, 'statut': 'en_cours', 'avancement': 35, 'zone': 'Abengourou'},
            {'code': 'PRJ-013', 'titre': 'Projet de construction d\'hôpitaux régionaux', 'secteur': 'SAN', 'bailleur': 'BID', 'montant': 55000000, 'statut': 'en_cours', 'avancement': 20, 'zone': 'Bouaké'},
            {'code': 'PRJ-014', 'titre': 'Corridor de transport régional', 'secteur': 'INF', 'bailleur': 'BAD', 'montant': 90000000, 'statut': 'en_cours', 'avancement': 15, 'zone': 'National'},
            {'code': 'PRJ-015', 'titre': 'Projet de résilience climatique des communautés rurales', 'secteur': 'ENV', 'bailleur': 'PNUD', 'montant': 12000000, 'statut': 'cloture', 'avancement': 100, 'zone': 'Bondoukou'},
            {'code': 'PRJ-016', 'titre': 'Appui à la décentralisation', 'secteur': 'GOV', 'bailleur': 'GIZ', 'montant': 6000000, 'statut': 'en_cours', 'avancement': 60, 'zone': 'Yamoussoukro'},
            {'code': 'PRJ-017', 'titre': 'Programme national d\'irrigation', 'secteur': 'AGR', 'bailleur': 'JICA', 'montant': 25000000, 'statut': 'en_cours', 'avancement': 48, 'zone': 'Ferkessédougou'},
            {'code': 'PRJ-018', 'titre': 'Projet d\'assainissement des grandes villes', 'secteur': 'EAU', 'bailleur': 'AFD', 'montant': 33000000, 'statut': 'en_cours', 'avancement': 22, 'zone': 'Abidjan'},
            {'code': 'PRJ-019', 'titre': 'Appui aux réformes des finances publiques', 'secteur': 'GOV', 'bailleur': 'FMI', 'montant': 10000000, 'statut': 'en_cours', 'avancement': 75, 'zone': 'Yamoussoukro'},
            {'code': 'PRJ-020', 'titre': 'Programme de développement de la chaîne de valeur agricole', 'secteur': 'AGR', 'bailleur': 'FKDEA', 'montant': 20000000, 'statut': 'identification', 'avancement': 0, 'zone': 'Korhogo'},
        ]

        # Map secteurs and bailleurs
        secteurs_map = {s.code: s for s in secteurs}
        bailleurs_map = {b.sigle: b for b in bailleurs}

        # PND sous-objectif mapping by secteur
        so_mapping = {
            'SAN': ['1.2'],
            'EDU': ['1.1'],
            'SOC': ['1.3'],
            'EAU': ['1.4'],
            'AGR': ['2.1'],
            'INF': ['2.2'],
            'ENE': ['2.2', '4.3'],
            'GOV': ['3.1', '3.2'],
            'ENV': ['4.1', '4.2'],
            'URB': ['2.2'],
        }
        so_map = {so.numero: so for so in all_sous_objectifs}

        projets = []
        for p_data in projets_data:
            base_date = date(2022, 1, 1) + timedelta(days=random.randint(0, 365))
            fin_prevue = base_date + timedelta(days=random.randint(365, 1825))

            # Make some projects overdue
            if p_data['code'] in ['PRJ-003', 'PRJ-005', 'PRJ-013', 'PRJ-014']:
                fin_prevue = date(2025, 6, 30)

            projet, created = Projet.objects.get_or_create(
                code=p_data['code'],
                defaults={
                    'titre': p_data['titre'],
                    'secteur': secteurs_map.get(p_data['secteur']),
                    'bailleur_principal': bailleurs_map.get(p_data['bailleur']),
                    'montant_total': Decimal(str(p_data['montant'])),
                    'statut': p_data['statut'],
                    'taux_avancement': Decimal(str(p_data['avancement'])),
                    'date_debut': base_date,
                    'date_fin_prevue': fin_prevue,
                    'date_signature': base_date - timedelta(days=random.randint(30, 180)),
                    'zone_geographique': p_data.get('zone', 'National'),
                    'responsable': f"Direction {p_data['secteur']}",
                }
            )

            if created:
                # Link PND objectives
                sector_code = p_data['secteur']
                if sector_code in so_mapping:
                    for so_num in so_mapping[sector_code]:
                        if so_num in so_map:
                            projet.objectifs_pnd.add(so_map[so_num])

            projets.append(projet)
        self.stdout.write(f"  {len(projets)} projets créés")

        # Financements et décaissements
        type_options = ['don', 'pret_concessionnel', 'pret_non_concessionnel', 'assistance_technique']
        for projet in projets:
            if not Financement.objects.filter(projet=projet).exists():
                montant = float(projet.montant_total)
                fin = Financement.objects.create(
                    projet=projet,
                    bailleur=projet.bailleur_principal,
                    type_financement=random.choice(type_options),
                    montant_engage=Decimal(str(montant)),
                    devise='USD',
                    date_accord=projet.date_signature,
                )

                # Create decaissements based on advancement
                if projet.statut in ['en_cours', 'cloture']:
                    taux = float(projet.taux_avancement) / 100
                    total_to_disburse = montant * taux * random.uniform(0.5, 0.9)
                    nb_decaissements = random.randint(2, 6)
                    for i in range(nb_decaissements):
                        portion = total_to_disburse / nb_decaissements
                        d_date = projet.date_debut + timedelta(days=random.randint(30, 900))
                        Decaissement.objects.create(
                            financement=fin,
                            montant=Decimal(str(round(portion, 2))),
                            date_decaissement=d_date,
                            reference=f"DEC-{projet.code}-{i+1:03d}",
                            description=f"Décaissement tranche {i+1}",
                        )

        self.stdout.write(self.style.SUCCESS("Données de démonstration créées avec succès !"))
