"""
Modèles pour les tableaux de bord
"""
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class WidgetDashboard(models.Model):
    """
    Modèle pour les widgets de tableau de bord
    """
    TYPE_CHOICES = [
        ('statistique', 'Statistique'),
        ('graphique', 'Graphique'),
        ('liste', 'Liste'),
        ('alerte', 'Alerte'),
        ('calendrier', 'Calendrier'),
        ('carte', 'Carte'),
    ]

    nom = models.CharField(max_length=100)
    type_widget = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Configuration
    configuration = models.JSONField(default=dict, blank=True)
    requete_donnees = models.TextField(blank=True)  # Requête SQL ou API
    
    # Affichage
    largeur = models.PositiveIntegerField(default=4)  # Sur 12 colonnes
    hauteur = models.PositiveIntegerField(default=3)  # En unités
    ordre = models.PositiveIntegerField(default=0)
    
    # Permissions
    roles_autorises = models.JSONField(default=list, blank=True)  # ['directeur', 'enseignant']
    
    # Statut
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'widgets_dashboard'
        verbose_name = 'Widget de tableau de bord'
        verbose_name_plural = 'Widgets de tableau de bord'
        ordering = ['ordre', 'nom']

    def __str__(self):
        return self.nom


class ConfigurationDashboard(models.Model):
    """
    Modèle pour les configurations de tableau de bord par utilisateur
    """
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='configuration_dashboard')
    
    # Layout
    widgets_actifs = models.ManyToManyField(WidgetDashboard, blank=True)
    layout_configuration = models.JSONField(default=dict, blank=True)
    
    # Préférences d'affichage
    theme = models.CharField(max_length=20, default='light')
    densite_affichage = models.CharField(max_length=20, default='normal')
    
    # Actualisation
    auto_refresh = models.BooleanField(default=True)
    intervalle_refresh = models.PositiveIntegerField(default=300)  # en secondes
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configurations_dashboard'
        verbose_name = 'Configuration de tableau de bord'
        verbose_name_plural = 'Configurations de tableau de bord'

    def __str__(self):
        return f"Configuration dashboard de {self.utilisateur.get_full_name()}"


class RapportDashboard(models.Model):
    """
    Modèle pour les rapports de tableau de bord
    """
    TYPE_RAPPORT_CHOICES = [
        ('quotidien', 'Quotidien'),
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel', 'Mensuel'),
        ('trimestriel', 'Trimestriel'),
        ('annuel', 'Annuel'),
    ]

    nom = models.CharField(max_length=200)
    type_rapport = models.CharField(max_length=20, choices=TYPE_RAPPORT_CHOICES)
    description = models.TextField(blank=True)
    
    # Configuration
    requete_donnees = models.TextField()
    parametres = models.JSONField(default=dict, blank=True)
    
    # Destinataires
    destinataires_automatiques = models.JSONField(default=list, blank=True)
    
    # Planification
    planifie = models.BooleanField(default=False)
    frequence = models.CharField(max_length=20, blank=True)
    jour_semaine = models.PositiveIntegerField(blank=True, null=True)  # 1-7
    jour_mois = models.PositiveIntegerField(blank=True, null=True)  # 1-31
    heure_envoi = models.TimeField(default='08:00')
    
    # Statut
    actif = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rapports_crees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rapports_dashboard'
        verbose_name = 'Rapport de tableau de bord'
        verbose_name_plural = 'Rapports de tableau de bord'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class ExecutionRapport(models.Model):
    """
    Modèle pour les exécutions de rapports
    """
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('echec', 'Échec'),
        ('annule', 'Annulé'),
    ]

    rapport = models.ForeignKey(RapportDashboard, on_delete=models.CASCADE, related_name='executions')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    
    # Résultats
    donnees_generes = models.JSONField(default=dict, blank=True)
    fichier_rapport = models.FileField(upload_to='rapports/', blank=True, null=True)
    
    # Métadonnées
    date_debut = models.DateTimeField(auto_now_add=True)
    date_fin = models.DateTimeField(blank=True, null=True)
    duree_execution = models.FloatField(blank=True, null=True)  # en secondes
    erreur_message = models.TextField(blank=True)
    
    # Destinataires
    destinataires_notifies = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'executions_rapports'
        verbose_name = 'Exécution de rapport'
        verbose_name_plural = 'Exécutions de rapports'
        ordering = ['-date_debut']

    def __str__(self):
        return f"Exécution {self.rapport.nom} - {self.get_statut_display()}"


class AlerteDashboard(models.Model):
    """
    Modèle pour les alertes de tableau de bord
    """
    TYPE_ALERTE_CHOICES = [
        ('conflit_emploi_temps', 'Conflit emploi du temps'),
        ('absence_non_remplacee', 'Absence non remplacée'),
        ('salle_surchargee', 'Salle surchargée'),
        ('enseignant_surcharge', 'Enseignant surchargé'),
        ('budget_depasse', 'Budget dépassé'),
        ('performance_faible', 'Performance faible'),
    ]

    SEVERITE_CHOICES = [
        (1, 'Info'),
        (2, 'Attention'),
        (3, 'Avertissement'),
        (4, 'Erreur'),
        (5, 'Critique'),
    ]

    nom = models.CharField(max_length=200)
    type_alerte = models.CharField(max_length=50, choices=TYPE_ALERTE_CHOICES)
    severite = models.PositiveIntegerField(choices=SEVERITE_CHOICES, default=3)
    
    # Contenu
    message = models.TextField()
    description = models.TextField(blank=True)
    
    # Conditions
    conditions = models.JSONField(default=dict, blank=True)
    seuil_alerte = models.FloatField(blank=True, null=True)
    
    # Destinataires
    destinataires = models.JSONField(default=list, blank=True)
    
    # Statut
    active = models.BooleanField(default=True)
    date_derniere_activation = models.DateTimeField(blank=True, null=True)
    nombre_activations = models.PositiveIntegerField(default=0)
    
    # Métadonnées
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertes_crees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'alertes_dashboard'
        verbose_name = 'Alerte de tableau de bord'
        verbose_name_plural = 'Alertes de tableau de bord'
        ordering = ['-severite', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_severite_display()})"


class ActivationAlerte(models.Model):
    """
    Modèle pour les activations d'alertes
    """
    alerte = models.ForeignKey(AlerteDashboard, on_delete=models.CASCADE, related_name='activations')
    
    # Contexte d'activation
    contexte = models.JSONField(default=dict, blank=True)
    valeur_detectee = models.FloatField(blank=True, null=True)
    
    # Statut
    resolue = models.BooleanField(default=False)
    date_resolution = models.DateTimeField(blank=True, null=True)
    resolution_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='alertes_resolues')
    
    # Métadonnées
    date_activation = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'activations_alertes'
        verbose_name = 'Activation d\'alerte'
        verbose_name_plural = 'Activations d\'alertes'
        ordering = ['-date_activation']

    def __str__(self):
        return f"Activation {self.alerte.nom} - {self.date_activation}"

