"""
Vues pour l'application IA et optimisation
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from .models import ModeleIA, OptimisationEmploiTemps, PredictionAbsence, LogOptimisation
# from .algorithms import OptimiseurEmploiTemps, PredicteurAbsences, OptimiseurRemplacants
from apps.emplois_temps.models import EmploiTemps
from apps.remplacements.models import Absence


@login_required
def dashboard_ia(request):
    """
    Tableau de bord IA
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    # Statistiques IA
    stats = {
        'modeles_actifs': ModeleIA.objects.filter(statut='deploye').count(),
        'optimisations_mois': OptimisationEmploiTemps.objects.filter(
            started_at__month=timezone.now().month
        ).count(),
        'predictions_mois': PredictionAbsence.objects.filter(
            created_at__month=timezone.now().month
        ).count(),
        'taux_succes': 0.95,  # À calculer
    }
    
    # Dernières optimisations
    optimisations_recentes = OptimisationEmploiTemps.objects.all().order_by('-started_at')[:5]
    
    # Prédictions récentes
    predictions_recentes = PredictionAbsence.objects.all().order_by('-created_at')[:5]
    
    context = {
        'stats': stats,
        'optimisations_recentes': optimisations_recentes,
        'predictions_recentes': predictions_recentes,
    }
    
    return render(request, 'ia_optimisation/dashboard.html', context)


@login_required
def liste_modeles(request):
    """
    Liste des modèles IA
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    modeles = ModeleIA.objects.all().order_by('-created_at')
    
    context = {
        'modeles': modeles,
    }
    
    return render(request, 'ia_optimisation/modeles.html', context)


@login_required
def detail_modele(request, pk):
    """
    Détail d'un modèle IA
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    modele = get_object_or_404(ModeleIA, pk=pk)
    
    context = {
        'modele': modele,
    }
    
    return render(request, 'ia_optimisation/detail_modele.html', context)


@login_required
def liste_optimisations(request):
    """
    Liste des optimisations
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    optimisations = OptimisationEmploiTemps.objects.all().order_by('-started_at')
    
    context = {
        'optimisations': optimisations,
    }
    
    return render(request, 'ia_optimisation/optimisations.html', context)


@login_required
def detail_optimisation(request, pk):
    """
    Détail d'une optimisation
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    optimisation = get_object_or_404(OptimisationEmploiTemps, pk=pk)
    
    context = {
        'optimisation': optimisation,
    }
    
    return render(request, 'ia_optimisation/detail_optimisation.html', context)


@login_required
def liste_predictions(request):
    """
    Liste des prédictions
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    predictions = PredictionAbsence.objects.all().order_by('-created_at')
    
    context = {
        'predictions': predictions,
    }
    
    return render(request, 'ia_optimisation/predictions.html', context)


@login_required
def detail_prediction(request, pk):
    """
    Détail d'une prédiction
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    prediction = get_object_or_404(PredictionAbsence, pk=pk)
    
    context = {
        'prediction': prediction,
    }
    
    return render(request, 'ia_optimisation/detail_prediction.html', context)


# API Views
@login_required
def api_optimiser(request):
    """
    API pour optimiser un emploi du temps
    """
    emploi_temps_id = request.GET.get('emploi_temps_id')
    
    if not emploi_temps_id:
        return JsonResponse({'error': 'emploi_temps_id requis'}, status=400)
    
    try:
        emploi_temps = EmploiTemps.objects.get(id=emploi_temps_id)
        
        # Vérifier les permissions
        if not request.user.is_rectorat() and emploi_temps.etablissement != request.user.profil_enseignant.etablissement:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Lancer l'optimisation (simplifié)
        # TODO: Implémenter l'optimisation IA
        return JsonResponse({
            'success': True,
            'message': 'Optimisation terminée avec succès (simulée)',
            'score': 0.95,
            'conflits_resolus': 5,
            'temps_calcul': 2.5
        })
            
    except EmploiTemps.DoesNotExist:
        return JsonResponse({'error': 'Emploi du temps non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_predire(request):
    """
    API pour prédire les absences
    """
    enseignant_id = request.GET.get('enseignant_id')
    
    if not enseignant_id:
        return JsonResponse({'error': 'enseignant_id requis'}, status=400)
    
    try:
        from apps.accounts.models import User
        enseignant = User.objects.get(id=enseignant_id, role='enseignant')
        
        # Vérifier les permissions
        if not request.user.is_rectorat() and enseignant != request.user:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Faire la prédiction
        predicteur = PredicteurAbsences()
        
        # Préparer les données de l'enseignant
        donnees_enseignant = {
            'age': 35,  # À calculer
            'experience_annees': enseignant.profil_enseignant.experience_annees if hasattr(enseignant, 'profil_enseignant') else 0,
            'heures_semaine': enseignant.profil_enseignant.heures_max_semaine if hasattr(enseignant, 'profil_enseignant') else 35,
            'nombre_classes': 3,  # À calculer
            'stress_niveau': 5,  # À récupérer
            'satisfaction_travail': 7,  # À récupérer
            'distance_domicile': 15,  # À calculer
            'nombre_enfants': 2,  # À récupérer
            'sante_generale': 8,  # À récupérer
            'absences_annee_precedente': Absence.objects.filter(
                enseignant=enseignant,
                date_debut__year=timezone.now().year - 1
            ).count(),
        }
        
        prediction = predicteur.predire(donnees_enseignant)
        
        if prediction:
            return JsonResponse({
                'success': True,
                'probabilite_absence': prediction['probabilite_absence'],
                'facteurs_risque': prediction['facteurs_risque'],
                'recommandations': prediction['recommandations']
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la prédiction'
            }, status=500)
            
    except User.DoesNotExist:
        return JsonResponse({'error': 'Enseignant non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def api_analyser(request):
    """
    API pour analyser les conflits
    """
    emploi_temps_id = request.GET.get('emploi_temps_id')
    
    if not emploi_temps_id:
        return JsonResponse({'error': 'emploi_temps_id requis'}, status=400)
    
    try:
        emploi_temps = EmploiTemps.objects.get(id=emploi_temps_id)
        
        # Vérifier les permissions
        if not request.user.is_rectorat() and emploi_temps.etablissement != request.user.profil_enseignant.etablissement:
            return JsonResponse({'error': 'Accès non autorisé'}, status=403)
        
        # Analyser les conflits
        from .algorithms import AnalyseurConflits
        analyseur = AnalyseurConflits()
        conflits = analyseur.analyser_conflits(emploi_temps)
        
        return JsonResponse({
            'success': True,
            'conflits': conflits,
            'nombre_conflits': len(conflits)
        })
        
    except EmploiTemps.DoesNotExist:
        return JsonResponse({'error': 'Emploi du temps non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
