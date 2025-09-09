"""
URLs pour l'application emplois du temps
"""
from django.urls import path
from . import views

app_name = 'emplois_temps'

urlpatterns = [
    # Vues principales
    path('', views.liste_emplois_temps, name='liste'),
    path('creer/', views.creer_emploi_temps, name='creer'),
    path('<int:pk>/', views.detail_emploi_temps, name='detail'),
    path('<int:pk>/modifier/', views.modifier_emploi_temps, name='modifier'),
    path('<int:pk>/optimiser/', views.optimiser_emploi_temps, name='optimiser'),
    
    # API
    path('api/', views.api_liste_emplois_temps, name='api_liste'),
    path('api/<int:pk>/', views.api_detail_emploi_temps, name='api_detail'),
    path('api/<int:pk>/optimiser/', views.api_optimiser_emploi_temps, name='api_optimiser'),
]