"""
Vues pour l'application remplacements
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Absence, Remplacant, Remplacement, PropositionRemplacement
from .forms import AbsenceForm, RemplacantForm, RemplacementForm
# from apps.ia_optimisation.algorithms import OptimiseurRemplacants, PredicteurAbsences
from apps.etablissements.models import Etablissement
from apps.accounts.models import User


@login_required
def liste_absences(request):
    """
    Liste des absences pour l'établissement de l'utilisateur
    """
    if request.user.is_rectorat():
        absences = Absence.objects.all().order_by('-date_debut')
    else:
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        if etablissement:
            absences = Absence.objects.filter(etablissement=etablissement).order_by('-date_debut')
        else:
            absences = Absence.objects.none()
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        absences = absences.filter(statut=statut)
    
    type_absence = request.GET.get('type_absence')
    if type_absence:
        absences = absences.filter(type_absence=type_absence)
    
    context = {
        'absences': absences,
        'statuts': Absence.STATUT_CHOICES,
        'types_absence': Absence.TYPE_ABSENCE_CHOICES,
    }
    return render(request, 'remplacements/liste_absences.html', context)


@login_required
def creer_absence(request):
    """
    Création d'une nouvelle absence
    """
    if request.method == 'POST':
        form = AbsenceForm(request.POST, request.FILES)
        if form.is_valid():
            absence = form.save(commit=False)
            absence.declaree_par = request.user
            absence.etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
            absence.save()
            
            # Déclencher la recherche de remplaçants (simplifié)
            # TODO: Implémenter la recherche automatique de remplaçants
            
            messages.success(request, 'Absence déclarée avec succès. Recherche de remplaçants en cours...')
            return redirect('remplacements:detail_absence', pk=absence.pk)
    else:
        form = AbsenceForm()
    
    return render(request, 'remplacements/creer_absence.html', {'form': form})


@login_required
def detail_absence(request, pk):
    """
    Détail d'une absence avec propositions de remplaçants
    """
    absence = get_object_or_404(Absence, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste')
    
    # Récupérer les propositions de remplaçants
    propositions = PropositionRemplacement.objects.filter(absence=absence).order_by('-score_compatibilite')
    
    # Récupérer les remplacements effectués
    remplacements = Remplacement.objects.filter(absence=absence).order_by('-date_remplacement')
    
    context = {
        'absence': absence,
        'propositions': propositions,
        'remplacements': remplacements,
    }
    return render(request, 'remplacements/detail_absence.html', context)


@login_required
def modifier_absence(request, pk):
    """
    Modification d'une absence
    """
    absence = get_object_or_404(Absence, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and absence.declaree_par != request.user:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste')
    
    if request.method == 'POST':
        form = AbsenceForm(request.POST, request.FILES, instance=absence)
        if form.is_valid():
            form.save()
            messages.success(request, 'Absence modifiée avec succès')
            return redirect('remplacements:detail_absence', pk=absence.pk)
    else:
        form = AbsenceForm(instance=absence)
    
    return render(request, 'remplacements/modifier_absence.html', {'form': form, 'absence': absence})


@login_required
def liste_remplacants(request):
    """
    Liste des remplaçants disponibles
    """
    if request.user.is_rectorat():
        remplacants = Remplacant.objects.all().order_by('-note_moyenne')
    else:
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        if etablissement:
            remplacants = Remplacant.objects.filter(etablissement=etablissement).order_by('-note_moyenne')
        else:
            remplacants = Remplacant.objects.none()
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        remplacants = remplacants.filter(statut=statut)
    
    matiere = request.GET.get('matiere')
    if matiere:
        remplacants = remplacants.filter(matieres_enseignees__id=matiere)
    
    context = {
        'remplacants': remplacants,
        'statuts': Remplacant.STATUT_CHOICES,
    }
    return render(request, 'remplacements/liste_remplacants.html', context)


@login_required
def creer_remplacant(request):
    """
    Création d'un nouveau remplaçant
    """
    if request.method == 'POST':
        form = RemplacantForm(request.POST)
        if form.is_valid():
            remplacant = form.save(commit=False)
            remplacant.etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
            remplacant.save()
            form.save_m2m()  # Sauvegarder les relations many-to-many
            
            messages.success(request, 'Remplaçant créé avec succès')
            return redirect('remplacements:detail_remplacant', pk=remplacant.pk)
    else:
        form = RemplacantForm()
    
    return render(request, 'remplacements/creer_remplacant.html', {'form': form})


@login_required
def detail_remplacant(request, pk):
    """
    Détail d'un remplaçant
    """
    remplacant = get_object_or_404(Remplacant, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and remplacant.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_remplacants')
    
    # Récupérer les remplacements effectués
    remplacements = Remplacement.objects.filter(remplacant=remplacant).order_by('-date_remplacement')
    
    context = {
        'remplacant': remplacant,
        'remplacements': remplacements,
    }
    return render(request, 'remplacements/detail_remplacant.html', context)


@login_required
def modifier_remplacant(request, pk):
    """
    Modification d'un remplaçant
    """
    remplacant = get_object_or_404(Remplacant, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and remplacant.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_remplacants')
    
    if request.method == 'POST':
        form = RemplacantForm(request.POST, instance=remplacant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Remplaçant modifié avec succès')
            return redirect('remplacements:detail_remplacant', pk=remplacant.pk)
    else:
        form = RemplacantForm(instance=remplacant)
    
    return render(request, 'remplacements/modifier_remplacant.html', {'form': form, 'remplacant': remplacant})


@login_required
def liste_remplacements(request):
    """
    Liste des remplacements
    """
    if request.user.is_rectorat():
        remplacements = Remplacement.objects.all().order_by('-date_remplacement')
    else:
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        if etablissement:
            remplacements = Remplacement.objects.filter(absence__etablissement=etablissement).order_by('-date_remplacement')
        else:
            remplacements = Remplacement.objects.none()
    
    # Filtres
    statut = request.GET.get('statut')
    if statut:
        remplacements = remplacements.filter(statut=statut)
    
    context = {
        'remplacements': remplacements,
        'statuts': Remplacement.STATUT_CHOICES,
    }
    return render(request, 'remplacements/liste_remplacements.html', context)


@login_required
def detail_remplacement(request, pk):
    """
    Détail d'un remplacement
    """
    remplacement = get_object_or_404(Remplacement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and remplacement.absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_remplacements')
    
    return render(request, 'remplacements/detail_remplacement.html', {'remplacement': remplacement})


@login_required
def accepter_remplacement(request, pk):
    """
    Accepter un remplacement
    """
    remplacement = get_object_or_404(Remplacement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and remplacement.absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_remplacements')
    
    if request.method == 'POST':
        remplacement.statut = 'accepte'
        remplacement.date_acceptation = timezone.now()
        remplacement.save()
        
        # Mettre à jour l'absence
        remplacement.absence.statut = 'remplacee'
        remplacement.absence.save()
        
        messages.success(request, 'Remplacement accepté avec succès')
        return redirect('remplacements:detail_remplacement', pk=remplacement.pk)
    
    return render(request, 'remplacements/accepter_remplacement.html', {'remplacement': remplacement})


@login_required
def refuser_remplacement(request, pk):
    """
    Refuser un remplacement
    """
    remplacement = get_object_or_404(Remplacement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and remplacement.absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_remplacements')
    
    if request.method == 'POST':
        remplacement.statut = 'refuse'
        remplacement.save()
        
        messages.success(request, 'Remplacement refusé')
        return redirect('remplacements:detail_remplacement', pk=remplacement.pk)
    
    return render(request, 'remplacements/refuser_remplacement.html', {'remplacement': remplacement})


@login_required
def liste_propositions(request):
    """
    Liste des propositions de remplaçants générées par l'IA
    """
    if request.user.is_rectorat():
        propositions = PropositionRemplacement.objects.all().order_by('-score_compatibilite')
    else:
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        if etablissement:
            propositions = PropositionRemplacement.objects.filter(absence__etablissement=etablissement).order_by('-score_compatibilite')
        else:
            propositions = PropositionRemplacement.objects.none()
    
    context = {
        'propositions': propositions,
    }
    return render(request, 'remplacements/liste_propositions.html', context)


@login_required
def detail_proposition(request, pk):
    """
    Détail d'une proposition de remplaçant
    """
    proposition = get_object_or_404(PropositionRemplacement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and proposition.absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_propositions')
    
    return render(request, 'remplacements/detail_proposition.html', {'proposition': proposition})


@login_required
def accepter_proposition(request, pk):
    """
    Accepter une proposition de remplaçant
    """
    proposition = get_object_or_404(PropositionRemplacement, pk=pk)
    
    # Vérifier les permissions
    if not request.user.is_rectorat() and proposition.absence.etablissement != request.user.profil_enseignant.etablissement:
        messages.error(request, 'Accès non autorisé')
        return redirect('remplacements:liste_propositions')
    
    if request.method == 'POST':
        # Créer le remplacement
        remplacement = Remplacement.objects.create(
            absence=proposition.absence,
            remplacant=proposition.remplacant,
            date_remplacement=proposition.date_proposition,
            heure_debut=proposition.absence.heure_debut or timezone.now().time(),
            heure_fin=proposition.absence.heure_fin or timezone.now().time(),
            salle=proposition.absence.etablissement.salles.first(),  # Simplifié
            statut='propose',
            created_by=request.user
        )
        
        # Ajouter les cours concernés
        for cours in proposition.cours_concernes.all():
            remplacement.cours_remplaces.add(cours)
        
        # Mettre à jour la proposition
        proposition.statut = 'acceptee'
        proposition.save()
        
        messages.success(request, 'Proposition acceptée. Remplacement créé.')
        return redirect('remplacements:detail_remplacement', pk=remplacement.pk)
    
    return render(request, 'remplacements/accepter_proposition.html', {'proposition': proposition})


# API Views
@login_required
def api_liste_absences(request):
    """
    API pour récupérer la liste des absences
    """
    absences = Absence.objects.all().order_by('-date_debut')
    
    data = []
    for absence in absences:
        data.append({
            'id': absence.id,
            'enseignant': absence.enseignant.get_full_name(),
            'type_absence': absence.get_type_absence_display(),
            'date_debut': absence.date_debut.isoformat(),
            'date_fin': absence.date_fin.isoformat(),
            'statut': absence.get_statut_display(),
            'urgence': absence.urgence,
        })
    
    return JsonResponse({'absences': data})


@login_required
def api_remplacants_disponibles(request):
    """
    API pour récupérer les remplaçants disponibles
    """
    date = request.GET.get('date')
    matiere = request.GET.get('matiere')
    
    remplacants = Remplacant.objects.filter(statut='disponible')
    
    if date:
        remplacants = remplacants.filter(
            date_debut_disponibilite__lte=date,
            date_fin_disponibilite__gte=date
        )
    
    if matiere:
        remplacants = remplacants.filter(matieres_enseignees__id=matiere)
    
    data = []
    for remplacant in remplacants:
        data.append({
            'id': remplacant.id,
            'enseignant': remplacant.enseignant.get_full_name(),
            'matieres': [m.nom for m in remplacant.matieres_enseignees.all()],
            'note_moyenne': remplacant.note_moyenne,
            'experience': remplacant.experience_remplacement,
        })
    
    return JsonResponse({'remplacants': data})


@login_required
def api_matching_remplacants(request, absence_id):
    """
    API pour le matching de remplaçants pour une absence
    """
    absence = get_object_or_404(Absence, pk=absence_id)
    
    # Récupérer les remplaçants disponibles
    remplacants_disponibles = Remplacant.objects.filter(
        statut='disponible',
        etablissement=absence.etablissement
    )
    
    # Utiliser l'algorithme de matching (simplifié)
    # TODO: Implémenter le matching intelligent
    matchings = []  # Simulation
    
    return JsonResponse({'matchings': matchings})


@login_required
def api_generer_propositions(request, absence_id):
    """
    API pour générer des propositions de remplaçants
    """
    absence = get_object_or_404(Absence, pk=absence_id)
    
    # Utiliser l'algorithme de matching (simplifié)
    # TODO: Implémenter le matching intelligent
    matchings = []  # Simulation
    
    # Créer les propositions
    propositions_crees = []
    for matching in matchings[:5]:  # Top 5
        proposition = PropositionRemplacement.objects.create(
            absence=absence,
            remplacant=matching['remplacant'],
            score_compatibilite=matching['score_global'],
            score_competence=matching['score_competence'],
            score_disponibilite=matching['score_disponibilite'],
            score_geographique=matching['score_geographique'],
            score_experience=matching['score_experience'],
            date_proposition=absence.date_debut,
            statut='generee'
        )
        
        # Ajouter les cours concernés
        for cours in matching['details']['cours_remplacables']:
            proposition.cours_concernes.add(cours)
        
        propositions_crees.append(proposition.id)
    
    return JsonResponse({
        'message': f'{len(propositions_crees)} propositions générées',
        'propositions': propositions_crees
    })
