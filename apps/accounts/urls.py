"""
URLs pour l'application accounts
"""
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Profil utilisateur
    path('profile/', views.profil_utilisateur, name='profile'),
    path('profile/modifier/', views.modifier_profil, name='modifier_profil'),
    path('settings/', views.parametres_utilisateur, name='settings'),
    
    # API
    path('api/profile/', views.api_profil_utilisateur, name='api_profile'),
    path('api/users/', views.api_liste_utilisateurs, name='api_users'),
]