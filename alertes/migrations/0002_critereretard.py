from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alertes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CritereRetard",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nom", models.CharField(max_length=200, verbose_name="Nom du critère")),
                ("type_critere", models.CharField(
                    choices=[
                        ("date_depassee", "Date de fin prévue dépassée"),
                        ("decaissement_vs_prevu", "Taux de décaissement < Objectif annuel"),
                        ("ecart_physique_financier", "Écart avancement physique / décaissement ≥ seuil"),
                        ("duree_ecoulee_taux_faible", "Taux décaissement faible en fin de projet"),
                    ],
                    max_length=40,
                    verbose_name="Type de critère",
                )),
                ("description", models.TextField(blank=True, verbose_name="Description")),
                ("seuil_ecart_pct", models.DecimalField(
                    decimal_places=2, default=25, max_digits=5,
                    verbose_name="Écart physique/décaissement minimum (%)",
                    help_text="Utilisé pour le type « Écart avancement physique / décaissement »",
                )),
                ("seuil_duree_ecoulee_pct", models.DecimalField(
                    decimal_places=2, default=75, max_digits=5,
                    verbose_name="Durée écoulée minimum (%)",
                    help_text="Utilisé pour le type « Durée critique »",
                )),
                ("seuil_taux_decaissement_pct", models.DecimalField(
                    decimal_places=2, default=50, max_digits=5,
                    verbose_name="Taux de décaissement maximum (%)",
                    help_text="Utilisé pour le type « Durée critique »",
                )),
                ("actif", models.BooleanField(default=True, verbose_name="Actif")),
                ("ordre", models.PositiveIntegerField(default=0, verbose_name="Ordre d'affichage")),
                ("date_creation", models.DateTimeField(auto_now_add=True)),
                ("date_modification", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Critère de retard",
                "verbose_name_plural": "Critères de retard",
                "ordering": ["ordre", "nom"],
            },
        ),
    ]
