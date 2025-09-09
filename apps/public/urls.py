"""
URLs pour l'interface publique d'Edtia
"""
from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    # Pages principales
    path('', views.accueil, name='accueil'),
    path('presentation/', views.presentation, name='presentation'),
    path('fonctionnalites/', views.fonctionnalites, name='fonctionnalites'),
    path('tarifs/', views.tarifs, name='tarifs'),
    path('temoignages/', views.temoignages, name='temoignages'),
    path('contact/', views.contact, name='contact'),
    path('demo/', views.demo, name='demo'),
    path('demo-interactive/', views.demo_interactive, name='demo_interactive'),
    path('test-service/', views.test_service, name='test_service'),
    
    # Blog
    path('blog/', views.blog, name='blog'),
    path('blog/<slug:slug>/', views.article_detail, name='article_detail'),
    
    # API endpoints
    path('api/demo/', views.demande_demo, name='api_demo'),
    path('api/newsletter/', views.inscription_newsletter, name='api_newsletter'),
    path('api/contact/', views.message_contact, name='api_contact'),
    
    # Pages légales
    path('mentions-legales/', views.mentions_legales, name='mentions_legales'),
    path('politique-confidentialite/', views.politique_confidentialite, name='politique_confidentialite'),
    path('cgu/', views.cgu, name='cgu'),
]
