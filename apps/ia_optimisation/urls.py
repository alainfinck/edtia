"""
URLs pour l'application IA et optimisation
"""
from django.urls import path
from . import views

app_name = 'ia_optimisation'

urlpatterns = [
    # Vues principales
    path('', views.dashboard_ia, name='dashboard'),
    path('modeles/', views.liste_modeles, name='modeles'),
    path('modeles/<int:pk>/', views.detail_modele, name='detail_modele'),
    
    # Optimisation
    path('optimisation/', views.liste_optimisations, name='optimisations'),
    path('optimisation/<int:pk>/', views.detail_optimisation, name='detail_optimisation'),
    
    # Prédictions
    path('predictions/', views.liste_predictions, name='predictions'),
    path('predictions/<int:pk>/', views.detail_prediction, name='detail_prediction'),
    
    # API
    path('api/optimiser/', views.api_optimiser, name='api_optimiser'),
    path('api/predire/', views.api_predire, name='api_predire'),
    path('api/analyser/', views.api_analyser, name='api_analyser'),
]