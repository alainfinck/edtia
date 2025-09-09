"""
Vues pour l'application core
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from apps.etablissements.models import Etablissement
from apps.accounts.models import User
from apps.emplois_temps.models import EmploiTemps
from apps.remplacements.models import Absence, Remplacement


def home(request):
    """
    Page d'accueil d'Edtia
    """
    return render(request, 'core/home.html')


def health_check(request):
    """
    Endpoint de vérification de santé de l'API
    """
    return JsonResponse({
        'status': 'healthy',
        'timestamp': '2024-01-01T00:00:00Z',
        'version': '1.0.0'
    })


@login_required
def global_stats(request):
    """
    Statistiques globales pour les utilisateurs authentifiés
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    stats = {
        'etablissements': {
            'total': Etablissement.objects.filter(actif=True).count(),
            'par_type': list(Etablissement.objects.filter(actif=True)
                           .values('type_etablissement')
                           .annotate(count=Count('id'))),
        },
        'utilisateurs': {
            'total': User.objects.filter(is_active=True).count(),
            'par_role': list(User.objects.filter(is_active=True)
                           .values('role')
                           .annotate(count=Count('id'))),
        },
        'emplois_temps': {
            'total': EmploiTemps.objects.filter(statut='actif').count(),
            'en_cours': EmploiTemps.objects.filter(statut='brouillon').count(),
        },
        'absences': {
            'total_mois': Absence.objects.filter(
                date_debut__month=1,  # Mois actuel
                date_debut__year=2024
            ).count(),
            'remplacees': Remplacement.objects.filter(
                statut='effectue'
            ).count(),
        }
    }
    
    return JsonResponse(stats)

