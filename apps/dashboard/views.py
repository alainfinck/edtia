"""
Vues pour l'application dashboard
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q, Sum, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from .models import WidgetDashboard, ConfigurationDashboard, RapportDashboard, AlerteDashboard, ActivationAlerte
from apps.etablissements.models import Etablissement, Classe, Salle
from apps.accounts.models import User
from apps.emplois_temps.models import EmploiTemps, Cours
from apps.remplacements.models import Absence, Remplacement, Remplacant
from apps.notifications.models import Notification


@login_required
def dashboard_principal(request):
    """
    Tableau de bord principal selon le rôle de l'utilisateur
    """
    if request.user.is_directeur():
        return dashboard_directeur(request)
    elif request.user.is_enseignant():
        return dashboard_enseignant(request)
    elif request.user.is_rectorat():
        return dashboard_rectorat(request)
    else:
        return dashboard_enseignant(request)  # Par défaut


@login_required
def dashboard_directeur(request):
    """
    Tableau de bord pour les directeurs d'établissement
    """
    etablissement = request.user.profil_directeur.etablissement
    
    # Statistiques générales
    stats = {
        'enseignants_total': User.objects.filter(role='enseignant', profil_enseignant__etablissement=etablissement).count(),
        'classes_total': Classe.objects.filter(etablissement=etablissement, actif=True).count(),
        'salles_total': Salle.objects.filter(etablissement=etablissement, actif=True).count(),
        'emplois_temps_actifs': EmploiTemps.objects.filter(etablissement=etablissement, statut='actif').count(),
    }
    
    # Absences de la semaine
    debut_semaine = timezone.now().date() - timedelta(days=7)
    absences_semaine = Absence.objects.filter(
        etablissement=etablissement,
        date_debut__gte=debut_semaine
    ).count()
    
    # Remplacements effectués
    remplacements_effectues = Remplacement.objects.filter(
        absence__etablissement=etablissement,
        statut='effectue',
        date_effectuation__gte=debut_semaine
    ).count()
    
    # Taux de remplacement
    taux_remplacement = (remplacements_effectues / absences_semaine * 100) if absences_semaine > 0 else 0
    
    # Absences en cours
    absences_en_cours = Absence.objects.filter(
        etablissement=etablissement,
        statut='declaree'
    ).order_by('-date_debut')[:5]
    
    # Conflits d'emploi du temps
    conflits = Cours.objects.filter(
        emploi_temps__etablissement=etablissement,
        emploi_temps__statut='actif'
    ).extra(
        where=["EXISTS (SELECT 1 FROM emplois_temps_cours c2 WHERE c2.enseignant_id = emplois_temps_cours.enseignant_id AND c2.jour_semaine = emplois_temps_cours.jour_semaine AND c2.heure_debut < emplois_temps_cours.heure_fin AND c2.heure_fin > emplois_temps_cours.heure_debut AND c2.id != emplois_temps_cours.id)"]
    ).count()
    
    # Notifications récentes
    notifications = Notification.objects.filter(
        destinataire=request.user,
        lu=False
    ).order_by('-created_at')[:5]
    
    # Alertes actives
    alertes = AlerteDashboard.objects.filter(
        active=True,
        destinataires__contains=[request.user.role]
    ).order_by('-severite')[:3]
    
    context = {
        'stats': stats,
        'absences_semaine': absences_semaine,
        'remplacements_effectues': remplacements_effectues,
        'taux_remplacement': taux_remplacement,
        'absences_en_cours': absences_en_cours,
        'conflits': conflits,
        'notifications': notifications,
        'alertes': alertes,
        'etablissement': etablissement,
    }
    
    return render(request, 'dashboard/directeur.html', context)


@login_required
def dashboard_enseignant(request):
    """
    Tableau de bord pour les enseignants
    """
    # Emploi du temps de la semaine
    debut_semaine = timezone.now().date() - timedelta(days=timezone.now().weekday())
    fin_semaine = debut_semaine + timedelta(days=6)
    
    cours_semaine = Cours.objects.filter(
        enseignant=request.user,
        emploi_temps__statut='actif'
    ).order_by('jour_semaine', 'heure_debut')
    
    # Absences déclarées
    absences_declarees = Absence.objects.filter(
        enseignant=request.user
    ).order_by('-date_debut')[:5]
    
    # Remplacements effectués
    remplacements_effectues = Remplacement.objects.filter(
        remplacant__enseignant=request.user
    ).order_by('-date_remplacement')[:5]
    
    # Notifications
    notifications = Notification.objects.filter(
        destinataire=request.user,
        lu=False
    ).order_by('-created_at')[:5]
    
    # Statistiques personnelles
    stats = {
        'heures_semaine': cours_semaine.aggregate(total=Sum('duree'))['total'] or 0,
        'classes_enseignees': cours_semaine.values('classe').distinct().count(),
        'matieres_enseignees': cours_semaine.values('matiere').distinct().count(),
    }
    
    context = {
        'cours_semaine': cours_semaine,
        'absences_declarees': absences_declarees,
        'remplacements_effectues': remplacements_effectues,
        'notifications': notifications,
        'stats': stats,
        'debut_semaine': debut_semaine,
        'fin_semaine': fin_semaine,
    }
    
    return render(request, 'dashboard/enseignant.html', context)


@login_required
def dashboard_rectorat(request):
    """
    Tableau de bord pour le personnel rectorat
    """
    # Établissements suivis
    etablissements_suivis = request.user.profil_rectorat.etablissements_suivis.all()
    
    # Statistiques globales
    stats = {
        'etablissements_total': etablissements_suivis.count(),
        'enseignants_total': User.objects.filter(
            role='enseignant',
            profil_enseignant__etablissement__in=etablissements_suivis
        ).count(),
        'absences_mois': Absence.objects.filter(
            etablissement__in=etablissements_suivis,
            date_debut__month=timezone.now().month
        ).count(),
        'remplacements_effectues': Remplacement.objects.filter(
            absence__etablissement__in=etablissements_suivis,
            statut='effectue'
        ).count(),
    }
    
    # Établissements avec problèmes
    etablissements_problemes = []
    for etablissement in etablissements_suivis:
        absences_non_remplacees = Absence.objects.filter(
            etablissement=etablissement,
            statut='declaree',
            date_debut__lte=timezone.now().date()
        ).count()
        
        if absences_non_remplacees > 0:
            etablissements_problemes.append({
                'etablissement': etablissement,
                'absences_non_remplacees': absences_non_remplacees
            })
    
    # Tendances
    debut_mois = timezone.now().date().replace(day=1)
    absences_mois = Absence.objects.filter(
        etablissement__in=etablissements_suivis,
        date_debut__gte=debut_mois
    ).count()
    
    debut_mois_precedent = (debut_mois - timedelta(days=1)).replace(day=1)
    fin_mois_precedent = debut_mois - timedelta(days=1)
    absences_mois_precedent = Absence.objects.filter(
        etablissement__in=etablissements_suivis,
        date_debut__gte=debut_mois_precedent,
        date_debut__lte=fin_mois_precedent
    ).count()
    
    evolution_absences = ((absences_mois - absences_mois_precedent) / absences_mois_precedent * 100) if absences_mois_precedent > 0 else 0
    
    # Alertes critiques
    alertes_critiques = AlerteDashboard.objects.filter(
        active=True,
        severite__gte=4,
        destinataires__contains=['rectorat']
    ).order_by('-severite')[:5]
    
    context = {
        'stats': stats,
        'etablissements_suivis': etablissements_suivis,
        'etablissements_problemes': etablissements_problemes,
        'evolution_absences': evolution_absences,
        'alertes_critiques': alertes_critiques,
    }
    
    return render(request, 'dashboard/rectorat.html', context)


@login_required
def configurer_dashboard(request):
    """
    Configuration du tableau de bord
    """
    configuration, created = ConfigurationDashboard.objects.get_or_create(
        utilisateur=request.user
    )
    
    if request.method == 'POST':
        # Traitement de la configuration
        widgets_actifs = request.POST.getlist('widgets_actifs')
        configuration.widgets_actifs.set(widgets_actifs)
        
        configuration.theme = request.POST.get('theme', 'light')
        configuration.auto_refresh = request.POST.get('auto_refresh') == 'on'
        configuration.intervalle_refresh = int(request.POST.get('intervalle_refresh', 300))
        configuration.save()
        
        messages.success(request, 'Configuration sauvegardée avec succès')
        return redirect('dashboard:configuration')
    
    # Widgets disponibles selon le rôle
    widgets_disponibles = WidgetDashboard.objects.filter(
        actif=True,
        roles_autorises__contains=[request.user.role]
    ).order_by('ordre')
    
    context = {
        'configuration': configuration,
        'widgets_disponibles': widgets_disponibles,
    }
    
    return render(request, 'dashboard/configuration.html', context)


@login_required
def gerer_widgets(request):
    """
    Gestion des widgets de tableau de bord
    """
    widgets = WidgetDashboard.objects.all().order_by('ordre')
    
    context = {
        'widgets': widgets,
    }
    
    return render(request, 'dashboard/widgets.html', context)


@login_required
def liste_rapports(request):
    """
    Liste des rapports disponibles
    """
    rapports = RapportDashboard.objects.filter(actif=True).order_by('nom')
    
    context = {
        'rapports': rapports,
    }
    
    return render(request, 'dashboard/rapports.html', context)


@login_required
def creer_rapport(request):
    """
    Création d'un nouveau rapport
    """
    if request.method == 'POST':
        # Traitement de la création du rapport
        nom = request.POST.get('nom')
        type_rapport = request.POST.get('type_rapport')
        description = request.POST.get('description')
        requete_donnees = request.POST.get('requete_donnees')
        
        rapport = RapportDashboard.objects.create(
            nom=nom,
            type_rapport=type_rapport,
            description=description,
            requete_donnees=requete_donnees,
            created_by=request.user
        )
        
        messages.success(request, 'Rapport créé avec succès')
        return redirect('dashboard:detail_rapport', pk=rapport.pk)
    
    return render(request, 'dashboard/creer_rapport.html')


@login_required
def detail_rapport(request, pk):
    """
    Détail d'un rapport
    """
    rapport = get_object_or_404(RapportDashboard, pk=pk)
    executions = rapport.executions.all().order_by('-date_debut')[:10]
    
    context = {
        'rapport': rapport,
        'executions': executions,
    }
    
    return render(request, 'dashboard/detail_rapport.html', context)


@login_required
def executer_rapport(request, pk):
    """
    Exécution d'un rapport
    """
    rapport = get_object_or_404(RapportDashboard, pk=pk)
    
    # Créer une nouvelle exécution
    execution = rapport.executions.create(statut='en_cours')
    
    # Exécuter le rapport en arrière-plan
    from .tasks import executer_rapport_task
    executer_rapport_task.delay(execution.id)
    
    messages.success(request, 'Rapport en cours d\'exécution')
    return redirect('dashboard:detail_rapport', pk=rapport.pk)


@login_required
def liste_alertes(request):
    """
    Liste des alertes
    """
    alertes = AlerteDashboard.objects.filter(active=True).order_by('-severite')
    
    context = {
        'alertes': alertes,
    }
    
    return render(request, 'dashboard/alertes.html', context)


@login_required
def detail_alerte(request, pk):
    """
    Détail d'une alerte
    """
    alerte = get_object_or_404(AlerteDashboard, pk=pk)
    activations = alerte.activations.all().order_by('-date_activation')[:10]
    
    context = {
        'alerte': alerte,
        'activations': activations,
    }
    
    return render(request, 'dashboard/detail_alerte.html', context)


@login_required
def resoudre_alerte(request, pk):
    """
    Résolution d'une alerte
    """
    alerte = get_object_or_404(AlerteDashboard, pk=pk)
    
    if request.method == 'POST':
        alerte.active = False
        alerte.save()
        
        messages.success(request, 'Alerte résolue avec succès')
        return redirect('dashboard:detail_alerte', pk=alerte.pk)
    
    return render(request, 'dashboard/resoudre_alerte.html', {'alerte': alerte})


# API Views
@login_required
def api_donnees_dashboard(request):
    """
    API pour récupérer les données du tableau de bord
    """
    widget_id = request.GET.get('widget_id')
    
    if not widget_id:
        return JsonResponse({'error': 'widget_id requis'}, status=400)
    
    try:
        widget = WidgetDashboard.objects.get(id=widget_id)
        
        # Exécuter la requête de données
        # Ici, on pourrait exécuter la requête SQL ou appeler une API
        donnees = {
            'widget_id': widget.id,
            'type': widget.type_widget,
            'donnees': [],  # Données réelles à implémenter
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(donnees)
        
    except WidgetDashboard.DoesNotExist:
        return JsonResponse({'error': 'Widget non trouvé'}, status=404)


@login_required
def api_widgets(request):
    """
    API pour récupérer les widgets disponibles
    """
    widgets = WidgetDashboard.objects.filter(
        actif=True,
        roles_autorises__contains=[request.user.role]
    ).order_by('ordre')
    
    data = []
    for widget in widgets:
        data.append({
            'id': widget.id,
            'nom': widget.nom,
            'type': widget.type_widget,
            'description': widget.description,
            'largeur': widget.largeur,
            'hauteur': widget.hauteur,
            'ordre': widget.ordre,
        })
    
    return JsonResponse({'widgets': data})


@login_required
def api_alertes(request):
    """
    API pour récupérer les alertes
    """
    alertes = AlerteDashboard.objects.filter(
        active=True,
        destinataires__contains=[request.user.role]
    ).order_by('-severite')
    
    data = []
    for alerte in alertes:
        data.append({
            'id': alerte.id,
            'nom': alerte.nom,
            'type': alerte.type_alerte,
            'severite': alerte.severite,
            'message': alerte.message,
            'date_derniere_activation': alerte.date_derniere_activation.isoformat() if alerte.date_derniere_activation else None,
        })
    
    return JsonResponse({'alertes': data})


@login_required
def api_statistiques(request):
    """
    API pour récupérer les statistiques
    """
    if request.user.is_rectorat():
        # Statistiques rectorat
        etablissements_suivis = request.user.profil_rectorat.etablissements_suivis.all()
        
        stats = {
            'etablissements': etablissements_suivis.count(),
            'enseignants': User.objects.filter(
                role='enseignant',
                profil_enseignant__etablissement__in=etablissements_suivis
            ).count(),
            'absences_mois': Absence.objects.filter(
                etablissement__in=etablissements_suivis,
                date_debut__month=timezone.now().month
            ).count(),
            'remplacements_effectues': Remplacement.objects.filter(
                absence__etablissement__in=etablissements_suivis,
                statut='effectue'
            ).count(),
        }
    else:
        # Statistiques établissement
        etablissement = request.user.profil_enseignant.etablissement if hasattr(request.user, 'profil_enseignant') else None
        
        if etablissement:
            stats = {
                'enseignants': User.objects.filter(role='enseignant', profil_enseignant__etablissement=etablissement).count(),
                'classes': Classe.objects.filter(etablissement=etablissement, actif=True).count(),
                'salles': Salle.objects.filter(etablissement=etablissement, actif=True).count(),
                'absences_semaine': Absence.objects.filter(
                    etablissement=etablissement,
                    date_debut__gte=timezone.now().date() - timedelta(days=7)
                ).count(),
            }
        else:
            stats = {}
    
    return JsonResponse({'statistiques': stats})

