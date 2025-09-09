"""
Vues pour l'application emplois du temps
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import EmploiTemps, Cours, Contrainte
# from apps.ia_optimisation.algorithms import OptimiseurEmploiTemps, AnalyseurConflits


@login_required
def liste_emplois_temps(request):
    """
    Liste des emplois du temps
    """
    if request.user.is_rectorat():
        emplois_temps = EmploiTemps.objects.all().order_by('-date_creation')
    else:
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        if etablissement:
            emplois_temps = EmploiTemps.objects.filter(etablissement=etablissement).order_by('-date_creation')
        else:
            emplois_temps = EmploiTemps.objects.none()
    
    context = {
        'emplois_temps': emplois_temps,
    }
    return render(request, 'emplois_temps/liste.html', context)


@login_required
def creer_emploi_temps(request):
    """
    Création d'un nouvel emploi du temps
    """
    if request.method == 'POST':
        # Traitement de la création
        nom = request.POST.get('nom')
        periode_id = request.POST.get('periode')
        
        emploi_temps = EmploiTemps.objects.create(
            nom=nom,
            periode_id=periode_id,
            createur=request.user,
            etablissement=request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        )
        
        messages.success(request, 'Emploi du temps créé avec succès')
        return redirect('emplois_temps:detail', pk=emploi_temps.pk)
    
    return render(request, 'emplois_temps/creer.html')


@login_required
def detail_emploi_temps(request, pk):
    """
    Détail d'un emploi du temps
    """
    emploi_temps = get_object_or_404(EmploiTemps, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and emploi_temps.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('emplois_temps:liste')
    
    # Analyser les conflits (simplifié)
    conflits = []  # TODO: Implémenter l'analyse des conflits
    
    context = {
        'emploi_temps': emploi_temps,
        'conflits': conflits,
    }
    return render(request, 'emplois_temps/detail.html', context)


@login_required
def modifier_emploi_temps(request, pk):
    """
    Modification d'un emploi du temps
    """
    emploi_temps = get_object_or_404(EmploiTemps, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and emploi_temps.createur != request.user:
        messages.error(request, 'Accès non autorisé')
        return redirect('emplois_temps:liste')
    
    if request.method == 'POST':
        # Traitement de la modification
        emploi_temps.nom = request.POST.get('nom')
        emploi_temps.save()
        
        messages.success(request, 'Emploi du temps modifié avec succès')
        return redirect('emplois_temps:detail', pk=emploi_temps.pk)
    
    return render(request, 'emplois_temps/modifier.html', {'emploi_temps': emploi_temps})


@login_required
def optimiser_emploi_temps(request, pk):
    """
    Optimisation d'un emploi du temps
    """
    emploi_temps = get_object_or_404(EmploiTemps, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and emploi_temps.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('emplois_temps:liste')
    
    if request.method == 'POST':
        # Lancer l'optimisation (simplifié)
        # TODO: Implémenter l'optimisation IA
        messages.success(request, 'Optimisation terminée avec succès (simulée)')
        
        return redirect('emplois_temps:detail', pk=emploi_temps.pk)
    
    return render(request, 'emplois_temps/optimiser.html', {'emploi_temps': emploi_temps})


# API Views
@login_required
def api_liste_emplois_temps(request):
    """
    API pour récupérer la liste des emplois du temps
    """
    emplois_temps = EmploiTemps.objects.all().order_by('-date_creation')
    
    data = []
    for emploi_temps in emplois_temps:
        data.append({
            'id': emploi_temps.id,
            'nom': emploi_temps.nom,
            'etablissement': emploi_temps.etablissement.nom,
            'statut': emploi_temps.get_statut_display(),
            'date_creation': emploi_temps.date_creation.isoformat(),
            'score_optimisation': emploi_temps.score_optimisation,
        })
    
    return JsonResponse({'emplois_temps': data})


@login_required
def api_detail_emploi_temps(request, pk):
    """
    API pour récupérer le détail d'un emploi du temps
    """
    emploi_temps = get_object_or_404(EmploiTemps, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and emploi_temps.etablissement != request.user.profil_enseignant.etablissement:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    cours = emploi_temps.cours.all().order_by('jour_semaine', 'heure_debut')
    
    data = {
        'id': emploi_temps.id,
        'nom': emploi_temps.nom,
        'etablissement': emploi_temps.etablissement.nom,
        'statut': emploi_temps.get_statut_display(),
        'score_optimisation': emploi_temps.score_optimisation,
        'cours': []
    }
    
    for cours in cours:
        data['cours'].append({
            'id': cours.id,
            'classe': cours.classe.nom,
            'matiere': cours.matiere.nom,
            'enseignant': cours.enseignant.get_full_name(),
            'salle': cours.salle.nom,
            'jour_semaine': cours.get_jour_semaine_display(),
            'heure_debut': cours.heure_debut.isoformat(),
            'heure_fin': cours.heure_fin.isoformat(),
        })
    
    return JsonResponse(data)


@login_required
def api_optimiser_emploi_temps(request, pk):
    """
    API pour optimiser un emploi du temps
    """
    emploi_temps = get_object_or_404(EmploiTemps, pk=pk)
    
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
