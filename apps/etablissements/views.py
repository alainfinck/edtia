"""
Vues pour l'application etablissements
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Etablissement, Classe, Salle, Matiere


@login_required
def liste_etablissements(request):
    """
    Liste des établissements
    """
    if request.user.is_rectorat():
        etablissements = Etablissement.objects.filter(actif=True).order_by('nom')
    else:
        etablissements = Etablissement.objects.none()
    
    context = {
        'etablissements': etablissements,
    }
    return render(request, 'etablissements/liste.html', context)


@login_required
def creer_etablissement(request):
    """
    Création d'un nouvel établissement
    """
    if not request.user.is_rectorat():
        messages.error(request, 'Accès non autorisé')
        return redirect('etablissements:liste')
    
    if request.method == 'POST':
        # Traitement de la création
        nom = request.POST.get('nom')
        type_etablissement = request.POST.get('type_etablissement')
        uai = request.POST.get('uai')
        
        etablissement = Etablissement.objects.create(
            nom=nom,
            type_etablissement=type_etablissement,
            uai=uai,
            # Autres champs...
        )
        
        messages.success(request, 'Établissement créé avec succès')
        return redirect('etablissements:detail', pk=etablissement.pk)
    
    return render(request, 'etablissements/creer.html')


@login_required
def detail_etablissement(request, pk):
    """
    Détail d'un établissement
    """
    etablissement = get_object_or_404(Etablissement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('etablissements:liste')
    
    # Statistiques
    stats = {
        'classes': etablissement.classes.filter(actif=True).count(),
        'salles': etablissement.salles.filter(actif=True).count(),
        'enseignants': etablissement.enseignants.filter(statut='actif').count(),
    }
    
    context = {
        'etablissement': etablissement,
        'stats': stats,
    }
    return render(request, 'etablissements/detail.html', context)


@login_required
def modifier_etablissement(request, pk):
    """
    Modification d'un établissement
    """
    etablissement = get_object_or_404(Etablissement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('etablissements:liste')
    
    if request.method == 'POST':
        # Traitement de la modification
        etablissement.nom = request.POST.get('nom')
        etablissement.save()
        
        messages.success(request, 'Établissement modifié avec succès')
        return redirect('etablissements:detail', pk=etablissement.pk)
    
    return render(request, 'etablissements/modifier.html', {'etablissement': etablissement})


@login_required
def liste_classes(request, etablissement_id):
    """
    Liste des classes d'un établissement
    """
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
    classes = etablissement.classes.filter(actif=True).order_by('niveau', 'nom')
    
    context = {
        'etablissement': etablissement,
        'classes': classes,
    }
    return render(request, 'etablissements/classes.html', context)


@login_required
def creer_classe(request, etablissement_id):
    """
    Création d'une nouvelle classe
    """
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
    
    if request.method == 'POST':
        # Traitement de la création
        nom = request.POST.get('nom')
        niveau = request.POST.get('niveau')
        
        classe = Classe.objects.create(
            nom=nom,
            niveau=niveau,
            etablissement=etablissement
        )
        
        messages.success(request, 'Classe créée avec succès')
        return redirect('etablissements:liste_classes', etablissement_id=etablissement.id)
    
    return render(request, 'etablissements/creer_classe.html', {'etablissement': etablissement})


@login_required
def liste_salles(request, etablissement_id):
    """
    Liste des salles d'un établissement
    """
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
    salles = etablissement.salles.filter(actif=True).order_by('nom')
    
    context = {
        'etablissement': etablissement,
        'salles': salles,
    }
    return render(request, 'etablissements/salles.html', context)


@login_required
def creer_salle(request, etablissement_id):
    """
    Création d'une nouvelle salle
    """
    etablissement = get_object_or_404(Etablissement, pk=etablissement_id)
    
    if request.method == 'POST':
        # Traitement de la création
        nom = request.POST.get('nom')
        type_salle = request.POST.get('type_salle')
        capacite = request.POST.get('capacite')
        
        salle = Salle.objects.create(
            nom=nom,
            type_salle=type_salle,
            capacite=capacite,
            etablissement=etablissement
        )
        
        messages.success(request, 'Salle créée avec succès')
        return redirect('etablissements:liste_salles', etablissement_id=etablissement.id)
    
    return render(request, 'etablissements/creer_salle.html', {'etablissement': etablissement})


# API Views
@login_required
def api_liste_etablissements(request):
    """
    API pour récupérer la liste des établissements
    """
    etablissements = Etablissement.objects.filter(actif=True).order_by('nom')
    
    data = []
    for etablissement in etablissements:
        data.append({
            'id': etablissement.id,
            'nom': etablissement.nom,
            'type': etablissement.get_type_etablissement_display(),
            'uai': etablissement.uai,
            'ville': etablissement.ville,
            'classes_count': etablissement.classes.filter(actif=True).count(),
            'salles_count': etablissement.salles.filter(actif=True).count(),
        })
    
    return JsonResponse({'etablissements': data})


@login_required
def api_detail_etablissement(request, pk):
    """
    API pour récupérer le détail d'un établissement
    """
    etablissement = get_object_or_404(Etablissement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and etablissement != request.user.profil_enseignant.etablissement:
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    data = {
        'id': etablissement.id,
        'nom': etablissement.nom,
        'type': etablissement.get_type_etablissement_display(),
        'uai': etablissement.uai,
        'adresse': etablissement.adresse,
        'ville': etablissement.ville,
        'code_postal': etablissement.code_postal,
        'telephone': etablissement.telephone,
        'email': etablissement.email,
        'classes': [],
        'salles': [],
    }
    
    # Ajouter les classes
    for classe in etablissement.classes.filter(actif=True):
        data['classes'].append({
            'id': classe.id,
            'nom': classe.nom,
            'niveau': classe.niveau,
            'nombre_eleves': classe.nombre_eleves,
        })
    
    # Ajouter les salles
    for salle in etablissement.salles.filter(actif=True):
        data['salles'].append({
            'id': salle.id,
            'nom': salle.nom,
            'type': salle.get_type_salle_display(),
            'capacite': salle.capacite,
        })
    
    return JsonResponse(data)

