"""
URLs pour l'application etablissements
"""
from django.urls import path
from . import views

app_name = 'etablissements'

urlpatterns = [
    # Vues principales
    path('', views.liste_etablissements, name='liste'),
    path('creer/', views.creer_etablissement, name='creer'),
    path('<int:pk>/', views.detail_etablissement, name='detail'),
    path('<int:pk>/modifier/', views.modifier_etablissement, name='modifier'),
    
    # Classes
    path('<int:etablissement_id>/classes/', views.liste_classes, name='liste_classes'),
    path('<int:etablissement_id>/classes/creer/', views.creer_classe, name='creer_classe'),
    
    # Salles
    path('<int:etablissement_id>/salles/', views.liste_salles, name='liste_salles'),
    path('<int:etablissement_id>/salles/creer/', views.creer_salle, name='creer_salle'),
    
    # API
    path('api/', views.api_liste_etablissements, name='api_liste'),
    path('api/<int:pk>/', views.api_detail_etablissement, name='api_detail'),
]