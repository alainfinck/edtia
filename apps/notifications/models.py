"""
Modèles pour le système de notifications
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Notification(models.Model):
    """
    Modèle pour les notifications
    """
    TYPE_CHOICES = [
        ('absence_declaree', 'Absence déclarée'),
        ('propositions_remplacants', 'Propositions de remplaçants'),
        ('remplacement_accepte', 'Remplacement accepté'),
        ('remplacement_refuse', 'Remplacement refusé'),
        ('conflit_emploi_temps', 'Conflit emploi du temps'),
        ('optimisation_terminee', 'Optimisation terminée'),
        ('prediction_absence', 'Prédiction d\'absence'),
        ('rapport_hebdomadaire', 'Rapport hebdomadaire'),
        ('alerte_systeme', 'Alerte système'),
        ('message_general', 'Message général'),
    ]

    PRIORITE_CHOICES = [
        (1, 'Très faible'),
        (2, 'Faible'),
        (3, 'Normale'),
        (4, 'Élevée'),
        (5, 'Critique'),
    ]

    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type_notification = models.CharField(max_length=50, choices=TYPE_CHOICES)
    priorite = models.PositiveIntegerField(choices=PRIORITE_CHOICES, default=3)
    
    # Contenu
    titre = models.CharField(max_length=200)
    message = models.TextField()
    donnees = models.JSONField(default=dict, blank=True)  # Données supplémentaires
    
    # Statut
    lu = models.BooleanField(default=False)
    date_lecture = models.DateTimeField(blank=True, null=True)
    
    # Actions
    action_requise = models.BooleanField(default=False)
    action_effectuee = models.BooleanField(default=False)
    date_action = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.titre} - {self.destinataire.get_full_name()}"

    def marquer_comme_lu(self):
        """Marque la notification comme lue"""
        if not self.lu:
            self.lu = True
            self.date_lecture = timezone.now()
            self.save()

    def marquer_action_effectuee(self):
        """Marque l'action comme effectuée"""
        if not self.action_effectuee:
            self.action_effectuee = True
            self.date_action = timezone.now()
            self.save()


class TemplateNotification(models.Model):
    """
    Modèle pour les templates de notifications
    """
    nom = models.CharField(max_length=100, unique=True)
    type_notification = models.CharField(max_length=50, choices=Notification.TYPE_CHOICES)
    sujet = models.CharField(max_length=200)
    template_email = models.TextField(blank=True)
    template_sms = models.TextField(blank=True)
    template_app = models.TextField(blank=True)
    variables_disponibles = models.JSONField(default=list, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'templates_notifications'
        verbose_name = 'Template de notification'
        verbose_name_plural = 'Templates de notifications'

    def __str__(self):
        return self.nom


# Modèle PreferenceNotification temporairement désactivé
# class PreferenceNotification(models.Model):
#     """
#     Modèle pour les préférences de notifications des utilisateurs
#     """
#     CANAL_CHOICES = [
#         ('email', 'Email'),
#         ('sms', 'SMS'),
#         ('app', 'Application'),
#         ('push', 'Push notification'),
#     ]
#
#     utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences_notifications')
#     
#     # Préférences par type de notification
#     types_notifications = models.JSONField(default=dict, blank=True)
#     
#     # Préférences par canal
#     canaux_preferes = models.JSONField(default=dict, blank=True)
#     
#     # Préférences générales
#     recevoir_email = models.BooleanField(default=True)
#     recevoir_sms = models.BooleanField(default=False)
#     recevoir_push = models.BooleanField(default=True)
#     
#     # Horaires de réception
#     heure_debut = models.TimeField(default='08:00')
#     heure_fin = models.TimeField(default='18:00')
#     jours_semaine = models.JSONField(default=list, blank=True)  # [1,2,3,4,5] pour lundi-vendredi
#     
#     # Fréquence des rapports
#     rapport_quotidien = models.BooleanField(default=False)
#     rapport_hebdomadaire = models.BooleanField(default=True)
#     rapport_mensuel = models.BooleanField(default=True)
#     
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     class Meta:
#         db_table = 'preferences_notifications'
#         verbose_name = 'Préférence de notification'
#         verbose_name_plural = 'Préférences de notifications'
#
#     def __str__(self):
#         return f"Préférences de {self.utilisateur.get_full_name()}"


class LogNotification(models.Model):
    """
    Modèle pour les logs d'envoi de notifications
    """
    CANAL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('app', 'Application'),
        ('push', 'Push notification'),
    ]

    STATUT_CHOICES = [
        ('envoye', 'Envoyé'),
        ('delivre', 'Délivré'),
        ('lu', 'Lu'),
        ('echec', 'Échec'),
        ('bounce', 'Bounce'),
    ]

    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='logs')
    canal = models.CharField(max_length=20, choices=CANAL_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    
    # Détails d'envoi
    destinataire_email = models.EmailField(blank=True, null=True)
    destinataire_telephone = models.CharField(max_length=20, blank=True)
    message_envoye = models.TextField(blank=True)
    
    # Réponse du service
    reponse_service = models.JSONField(default=dict, blank=True)
    erreur_message = models.TextField(blank=True)
    
    # Métadonnées
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_delivrance = models.DateTimeField(blank=True, null=True)
    date_lecture = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'logs_notifications'
        verbose_name = 'Log de notification'
        verbose_name_plural = 'Logs de notifications'
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.notification.titre} - {self.get_canal_display()} - {self.get_statut_display()}"
