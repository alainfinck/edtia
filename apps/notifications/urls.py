"""
URLs pour l'application notifications
"""
from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Vues principales
    path('', views.liste_notifications, name='liste'),
    path('<int:pk>/', views.detail_notification, name='detail'),
    path('<int:pk>/marquer-lu/', views.marquer_comme_lu, name='marquer_lu'),
    path('marquer-toutes-lues/', views.marquer_toutes_lues, name='marquer_toutes_lues'),
    
    # Configuration
    path('preferences/', views.preferences_notifications, name='preferences'),
    
    # API
    path('api/', views.api_liste_notifications, name='api_liste'),
    path('api/<int:pk>/', views.api_detail_notification, name='api_detail'),
    path('api/<int:pk>/marquer-lu/', views.api_marquer_comme_lu, name='api_marquer_lu'),
]