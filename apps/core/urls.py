"""
URLs pour l'application core
"""
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/health/', views.health_check, name='health_check'),
    path('api/stats/', views.global_stats, name='global_stats'),
]

