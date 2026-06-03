from django.urls import path
from . import views

app_name = 'projets'

urlpatterns = [
    path('', views.liste, name='liste'),
    path('synthese/', views.synthese, name='synthese'),
    path('nouveau/', views.creer, name='creer'),
    path('supprimer-lot/', views.supprimer_lot, name='supprimer_lot'),
    path('exporter/', views.exporter_excel, name='exporter'),
    path('rapport-retards/', views.exporter_rapport_retards, name='exporter_retards'),

    # Programmes
    path('programmes/', views.programme_liste, name='programme_liste'),
    path('programmes/nouveau/', views.programme_creer, name='programme_creer'),
    path('programmes/<int:pk>/', views.programme_detail, name='programme_detail'),
    path('programmes/<int:pk>/modifier/', views.programme_modifier, name='programme_modifier'),
    path('programmes/<int:pk>/supprimer/', views.programme_supprimer, name='programme_supprimer'),

    # Projets
    path('<int:pk>/', views.detail, name='detail'),
    path('<int:pk>/modifier/', views.modifier, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer, name='supprimer'),

    # Pièces jointes
    path('<int:projet_pk>/pieces-jointes/ajouter/', views.piece_jointe_ajouter, name='piece_ajouter'),
    path('pieces-jointes/<int:pk>/supprimer/', views.piece_jointe_supprimer, name='piece_supprimer'),

    # Responsables locaux
    path('<int:projet_pk>/responsables/ajouter/', views.responsable_ajouter, name='responsable_ajouter'),
    path('responsables/<int:pk>/supprimer/', views.responsable_supprimer, name='responsable_supprimer'),

    # Commentaires / Justifications
    path('<int:pk>/commentaires/ajouter/', views.ajouter_commentaire, name='commentaire_ajouter'),
    path('<int:pk>/commentaires/<int:commentaire_pk>/supprimer/', views.supprimer_commentaire, name='commentaire_supprimer'),
]
