"""
URLs pour l'application dashboard
"""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Tableaux de bord principaux
    path('', views.dashboard_principal, name='index'),
    path('directeur/', views.dashboard_directeur, name='directeur'),
    path('enseignant/', views.dashboard_enseignant, name='enseignant'),
    path('rectorat/', views.dashboard_rectorat, name='rectorat'),
    
    # Configuration
    path('configuration/', views.configurer_dashboard, name='configuration'),
    path('widgets/', views.gerer_widgets, name='widgets'),
    
    # Rapports
    path('rapports/', views.liste_rapports, name='rapports'),
    path('rapports/creer/', views.creer_rapport, name='creer_rapport'),
    path('rapports/<int:pk>/', views.detail_rapport, name='detail_rapport'),
    path('rapports/<int:pk>/executer/', views.executer_rapport, name='executer_rapport'),
    
    # Alertes
    path('alertes/', views.liste_alertes, name='alertes'),
    path('alertes/<int:pk>/', views.detail_alerte, name='detail_alerte'),
    path('alertes/<int:pk>/resoudre/', views.resoudre_alerte, name='resoudre_alerte'),
    
    # API
    path('api/donnees/', views.api_donnees_dashboard, name='api_donnees'),
    path('api/widgets/', views.api_widgets, name='api_widgets'),
    path('api/alertes/', views.api_alertes, name='api_alertes'),
    path('api/statistiques/', views.api_statistiques, name='api_statistiques'),
]