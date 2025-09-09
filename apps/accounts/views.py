"""
Vues pour l'application accounts
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import User, ProfilEnseignant, ProfilDirecteur, ProfilRectorat


@login_required
def profil_utilisateur(request):
    """
    Profil de l'utilisateur connecté
    """
    user = request.user
    
    # Récupérer le profil spécifique selon le rôle
    profil = None
    if user.is_enseignant() and hasattr(user, 'profil_enseignant'):
        profil = user.profil_enseignant
    elif user.is_directeur() and hasattr(user, 'profil_directeur'):
        profil = user.profil_directeur
    elif user.is_rectorat() and hasattr(user, 'profil_rectorat'):
        profil = user.profil_rectorat
    
    context = {
        'user': user,
        'profil': profil,
    }
    
    return render(request, 'accounts/profil.html', context)


@login_required
def modifier_profil(request):
    """
    Modification du profil utilisateur
    """
    user = request.user
    
    if request.method == 'POST':
        # Traitement de la modification
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.adresse = request.POST.get('adresse', user.adresse)
        user.ville = request.POST.get('ville', user.ville)
        user.code_postal = request.POST.get('code_postal', user.code_postal)
        
        # Gestion de l'avatar
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
        
        user.save()
        
        messages.success(request, 'Profil modifié avec succès')
        return redirect('accounts:profile')
    
    context = {
        'user': user,
    }
    
    return render(request, 'accounts/modifier_profil.html', context)


@login_required
def parametres_utilisateur(request):
    """
    Paramètres de l'utilisateur
    """
    user = request.user
    
    if request.method == 'POST':
        # Traitement des paramètres
        user.preferences_notifications = {
            'email': request.POST.get('notifications_email') == 'on',
            'sms': request.POST.get('notifications_sms') == 'on',
            'push': request.POST.get('notifications_push') == 'on',
        }
        
        user.save()
        
        messages.success(request, 'Paramètres sauvegardés avec succès')
        return redirect('accounts:settings')
    
    context = {
        'user': user,
    }
    
    return render(request, 'accounts/parametres.html', context)


# API Views
@login_required
def api_profil_utilisateur(request):
    """
    API pour récupérer le profil de l'utilisateur
    """
    user = request.user
    
    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'role': user.role,
        'telephone': user.telephone,
        'avatar': user.avatar.url if user.avatar else None,
        'date_embauche': user.date_embauche.isoformat() if user.date_embauche else None,
        'statut': user.statut,
        'derniere_connexion': user.derniere_connexion.isoformat() if user.derniere_connexion else None,
    }
    
    # Ajouter les informations spécifiques au profil
    if user.is_enseignant() and hasattr(user, 'profil_enseignant'):
        profil = user.profil_enseignant
        data['profil_enseignant'] = {
            'numero_enseignant': profil.numero_enseignant,
            'specialite': profil.specialite,
            'niveau_enseignement': profil.niveau_enseignement,
            'heures_max_semaine': profil.heures_max_semaine,
            'experience_annees': profil.experience_annees,
        }
    elif user.is_directeur() and hasattr(user, 'profil_directeur'):
        profil = user.profil_directeur
        data['profil_directeur'] = {
            'numero_directeur': profil.numero_directeur,
            'etablissement': profil.etablissement.nom,
            'date_nomination': profil.date_nomination.isoformat(),
        }
    elif user.is_rectorat() and hasattr(user, 'profil_rectorat'):
        profil = user.profil_rectorat
        data['profil_rectorat'] = {
            'numero_agent': profil.numero_agent,
            'service': profil.service,
            'niveau_acces': profil.niveau_acces,
            'academie': profil.academie,
        }
    
    return JsonResponse(data)


@login_required
def api_liste_utilisateurs(request):
    """
    API pour récupérer la liste des utilisateurs
    """
    if not request.user.is_rectorat() and not request.user.is_admin():
        return JsonResponse({'error': 'Accès non autorisé'}, status=403)
    
    role = request.GET.get('role')
    etablissement_id = request.GET.get('etablissement_id')
    
    users = User.objects.filter(is_active=True)
    
    if role:
        users = users.filter(role=role)
    
    if etablissement_id:
        users = users.filter(profil_enseignant__etablissement_id=etablissement_id)
    
    data = []
    for user in users:
        data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'statut': user.statut,
            'derniere_connexion': user.derniere_connexion.isoformat() if user.derniere_connexion else None,
        })
    
    return JsonResponse({'users': data})

