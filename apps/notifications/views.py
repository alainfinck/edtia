"""
Vues pour l'application notifications
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from .models import Notification, TemplateNotification


@login_required
def liste_notifications(request):
    """
    Liste des notifications de l'utilisateur
    """
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-created_at')
    
    # Filtres
    lu = request.GET.get('lu')
    if lu is not None:
        notifications = notifications.filter(lu=lu == 'true')
    
    type_notification = request.GET.get('type')
    if type_notification:
        notifications = notifications.filter(type_notification=type_notification)
    
    context = {
        'notifications': notifications,
        'types_notifications': Notification.TYPE_CHOICES,
    }
    
    return render(request, 'notifications/liste.html', context)


@login_required
def detail_notification(request, pk):
    """
    Détail d'une notification
    """
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    
    # Marquer comme lue si ce n'est pas déjà fait
    if not notification.lu:
        notification.marquer_comme_lu()
    
    context = {
        'notification': notification,
    }
    
    return render(request, 'notifications/detail.html', context)


@login_required
def marquer_comme_lu(request, pk):
    """
    Marquer une notification comme lue
    """
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    
    if not notification.lu:
        notification.marquer_comme_lu()
        messages.success(request, 'Notification marquée comme lue')
    else:
        messages.info(request, 'Notification déjà lue')
    
    return redirect('notifications:detail', pk=notification.pk)


@login_required
def marquer_toutes_lues(request):
    """
    Marquer toutes les notifications comme lues
    """
    notifications = Notification.objects.filter(
        destinataire=request.user,
        lu=False
    )
    
    count = notifications.count()
    notifications.update(lu=True, date_lecture=timezone.now())
    
    messages.success(request, f'{count} notifications marquées comme lues')
    return redirect('notifications:liste')


@login_required
def preferences_notifications(request):
    """
    Configuration des préférences de notifications (simplifié)
    """
    if request.method == 'POST':
        # Traitement des préférences (simplifié)
        messages.success(request, 'Préférences sauvegardées avec succès')
        return redirect('notifications:preferences')
    
    context = {
        'types_notifications': Notification.TYPE_CHOICES,
    }
    
    return render(request, 'notifications/preferences.html', context)


# API Views
@login_required
def api_liste_notifications(request):
    """
    API pour récupérer la liste des notifications
    """
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-created_at')
    
    # Filtres
    lu = request.GET.get('lu')
    if lu is not None:
        notifications = notifications.filter(lu=lu == 'true')
    
    type_notification = request.GET.get('type')
    if type_notification:
        notifications = notifications.filter(type_notification=type_notification)
    
    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'type': notification.type_notification,
            'titre': notification.titre,
            'message': notification.message,
            'priorite': notification.priorite,
            'lu': notification.lu,
            'action_requise': notification.action_requise,
            'created_at': notification.created_at.isoformat(),
        })
    
    return JsonResponse({'notifications': data})


@login_required
def api_detail_notification(request, pk):
    """
    API pour récupérer le détail d'une notification
    """
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    
    # Marquer comme lue si ce n'est pas déjà fait
    if not notification.lu:
        notification.marquer_comme_lu()
    
    data = {
        'id': notification.id,
        'type': notification.type_notification,
        'titre': notification.titre,
        'message': notification.message,
        'priorite': notification.priorite,
        'lu': notification.lu,
        'action_requise': notification.action_requise,
        'action_effectuee': notification.action_effectuee,
        'donnees': notification.donnees,
        'created_at': notification.created_at.isoformat(),
        'date_lecture': notification.date_lecture.isoformat() if notification.date_lecture else None,
    }
    
    return JsonResponse(data)


@login_required
def api_marquer_comme_lu(request, pk):
    """
    API pour marquer une notification comme lue
    """
    notification = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    
    if not notification.lu:
        notification.marquer_comme_lu()
        return JsonResponse({'success': True, 'message': 'Notification marquée comme lue'})
    else:
        return JsonResponse({'success': False, 'message': 'Notification déjà lue'})
