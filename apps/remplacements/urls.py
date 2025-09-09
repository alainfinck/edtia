"""
URLs pour l'application remplacements
"""
from django.urls import path
from . import views

app_name = 'remplacements'

urlpatterns = [
    # Vues principales
    path('', views.liste_absences, name='liste'),
    path('absences/', views.liste_absences, name='liste_absences'),
    path('absences/creer/', views.creer_absence, name='creer_absence'),
    path('absences/<int:pk>/', views.detail_absence, name='detail_absence'),
    path('absences/<int:pk>/modifier/', views.modifier_absence, name='modifier_absence'),
    
    # Gestion des remplaçants
    path('remplacants/', views.liste_remplacants, name='liste_remplacants'),
    path('remplacants/creer/', views.creer_remplacant, name='creer_remplacant'),
    path('remplacants/<int:pk>/', views.detail_remplacant, name='detail_remplacant'),
    path('remplacants/<int:pk>/modifier/', views.modifier_remplacant, name='modifier_remplacant'),
    
    # Remplacements
    path('remplacements/', views.liste_remplacements, name='liste_remplacements'),
    path('remplacements/<int:pk>/', views.detail_remplacement, name='detail_remplacement'),
    path('remplacements/<int:pk>/accepter/', views.accepter_remplacement, name='accepter_remplacement'),
    path('remplacements/<int:pk>/refuser/', views.refuser_remplacement, name='refuser_remplacement'),
    
    # Propositions IA
    path('propositions/', views.liste_propositions, name='liste_propositions'),
    path('propositions/<int:pk>/', views.detail_proposition, name='detail_proposition'),
    path('propositions/<int:pk>/accepter/', views.accepter_proposition, name='accepter_proposition'),
    
    # API
    path('api/absences/', views.api_liste_absences, name='api_liste_absences'),
    path('api/remplacants/disponibles/', views.api_remplacants_disponibles, name='api_remplacants_disponibles'),
    path('api/matching/<int:absence_id>/', views.api_matching_remplacants, name='api_matching_remplacants'),
    path('api/propositions/generer/<int:absence_id>/', views.api_generer_propositions, name='api_generer_propositions'),
]