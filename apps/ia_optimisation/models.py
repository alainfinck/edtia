"""
Modèles pour l'intelligence artificielle et l'optimisation
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class ModeleIA(models.Model):
    """
    Modèle pour stocker les modèles d'IA entraînés
    """
    TYPE_MODELE_CHOICES = [
        ('optimisation_emploi_temps', 'Optimisation emploi du temps'),
        ('prediction_absences', 'Prédiction d\'absences'),
        ('matching_remplacants', 'Matching remplaçants'),
        ('optimisation_salles', 'Optimisation salles'),
        ('prediction_charge_travail', 'Prédiction charge de travail'),
    ]

    nom = models.CharField(max_length=200)
    type_modele = models.CharField(max_length=50, choices=TYPE_MODELE_CHOICES)
    version = models.CharField(max_length=20)
    description = models.TextField()
    
    # Fichiers du modèle
    fichier_modele = models.FileField(upload_to='modeles_ia/')
    fichier_config = models.FileField(upload_to='configs_ia/', blank=True, null=True)
    
    # Métriques de performance
    precision = models.FloatField(blank=True, null=True)
    recall = models.FloatField(blank=True, null=True)
    f1_score = models.FloatField(blank=True, null=True)
    accuracy = models.FloatField(blank=True, null=True)
    
    # Configuration d'entraînement
    parametres_entrainement = models.JSONField(default=dict, blank=True)
    donnees_entrainement = models.JSONField(default=dict, blank=True)
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('entrainement', 'En entraînement'),
            ('valide', 'Validé'),
            ('deploye', 'Déployé'),
            ('deprecie', 'Déprécié'),
        ],
        default='entrainement'
    )
    
    # Métadonnées
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='modeles_ia_crees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'modeles_ia'
        verbose_name = 'Modèle IA'
        verbose_name_plural = 'Modèles IA'
        unique_together = ['nom', 'version']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.nom} v{self.version} ({self.get_type_modele_display()})"


class OptimisationEmploiTemps(models.Model):
    """
    Modèle pour les optimisations d'emploi du temps
    """
    emploi_temps = models.ForeignKey('emplois_temps.EmploiTemps', on_delete=models.CASCADE, related_name='optimisations')
    modele_ia = models.ForeignKey(ModeleIA, on_delete=models.CASCADE, related_name='optimisations_emploi_temps')
    
    # Paramètres d'optimisation
    contraintes_appliquees = models.JSONField(default=dict, blank=True)
    objectifs = models.JSONField(default=dict, blank=True)
    poids_contraintes = models.JSONField(default=dict, blank=True)
    
    # Résultats
    score_initial = models.FloatField(default=0.0)
    score_optimise = models.FloatField(default=0.0)
    amelioration_pourcentage = models.FloatField(default=0.0)
    
    # Détails de l'optimisation
    conflits_resolus = models.PositiveIntegerField(default=0)
    contraintes_violees = models.PositiveIntegerField(default=0)
    temps_calcul = models.FloatField(default=0.0)  # en secondes
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('en_cours', 'En cours'),
            ('termine', 'Terminé'),
            ('echec', 'Échec'),
            ('annule', 'Annulé'),
        ],
        default='en_cours'
    )
    
    # Métadonnées
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='optimisations_crees')

    class Meta:
        db_table = 'optimisations_emploi_temps'
        verbose_name = 'Optimisation emploi du temps'
        verbose_name_plural = 'Optimisations emploi du temps'
        ordering = ['-started_at']

    def __str__(self):
        return f"Optimisation {self.emploi_temps.nom} - {self.get_statut_display()}"


class PredictionAbsence(models.Model):
    """
    Modèle pour les prédictions d'absences
    """
    enseignant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='predictions_absence')
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='predictions_absence')
    modele_ia = models.ForeignKey(ModeleIA, on_delete=models.CASCADE, related_name='predictions_absence')
    
    # Prédiction
    date_prediction = models.DateField()
    probabilite_absence = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    type_absence_predite = models.CharField(max_length=50, blank=True)
    duree_predite = models.PositiveIntegerField(blank=True, null=True)  # en jours
    
    # Facteurs de risque
    facteurs_risque = models.JSONField(default=dict, blank=True)
    score_risque = models.FloatField(default=0.0)
    
    # Validation
    absence_reelle = models.ForeignKey(
        'remplacements.Absence',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='prediction_liee'
    )
    prediction_correcte = models.BooleanField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'predictions_absence'
        verbose_name = 'Prédiction d\'absence'
        verbose_name_plural = 'Prédictions d\'absence'
        ordering = ['-probabilite_absence', '-created_at']

    def __str__(self):
        return f"Prédiction {self.enseignant.get_full_name()} - {self.date_prediction} ({self.probabilite_absence:.2%})"


class MatchingRemplacant(models.Model):
    """
    Modèle pour les matchings de remplaçants
    """
    absence = models.ForeignKey('remplacements.Absence', on_delete=models.CASCADE, related_name='matchings_remplacants')
    remplacant = models.ForeignKey('remplacements.Remplacant', on_delete=models.CASCADE, related_name='matchings')
    modele_ia = models.ForeignKey(ModeleIA, on_delete=models.CASCADE, related_name='matchings_remplacants')
    
    # Scores de compatibilité
    score_global = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_competence = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_disponibilite = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_geographique = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_experience = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Détails du matching
    matieres_compatibles = models.JSONField(default=list, blank=True)
    cours_remplacables = models.JSONField(default=list, blank=True)
    contraintes_respectees = models.JSONField(default=list, blank=True)
    contraintes_violees = models.JSONField(default=list, blank=True)
    
    # Résultat
    proposition_acceptee = models.BooleanField(blank=True, null=True)
    remplacement_effectue = models.ForeignKey(
        'remplacements.Remplacement',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matching_origine'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matchings_remplacants'
        verbose_name = 'Matching remplaçant'
        verbose_name_plural = 'Matchings remplaçants'
        ordering = ['-score_global', '-created_at']

    def __str__(self):
        return f"Matching {self.remplacant.enseignant.get_full_name()} - Score: {self.score_global:.2f}"


class LogOptimisation(models.Model):
    """
    Modèle pour les logs d'optimisation
    """
    TYPE_ACTION_CHOICES = [
        ('optimisation_emploi_temps', 'Optimisation emploi du temps'),
        ('prediction_absence', 'Prédiction d\'absence'),
        ('matching_remplacant', 'Matching remplaçant'),
        ('optimisation_salle', 'Optimisation salle'),
        ('analyse_conflit', 'Analyse de conflit'),
    ]

    type_action = models.CharField(max_length=50, choices=TYPE_ACTION_CHOICES)
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='logs_optimisation')
    
    # Détails de l'action
    description = models.TextField()
    parametres_entree = models.JSONField(default=dict, blank=True)
    resultats = models.JSONField(default=dict, blank=True)
    
    # Performance
    temps_execution = models.FloatField(default=0.0)  # en secondes
    memoire_utilisee = models.FloatField(default=0.0)  # en MB
    cpu_utilise = models.FloatField(default=0.0)  # en %
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('succes', 'Succès'),
            ('echec', 'Échec'),
            ('erreur', 'Erreur'),
        ]
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='logs_optimisation')

    class Meta:
        db_table = 'logs_optimisation'
        verbose_name = 'Log d\'optimisation'
        verbose_name_plural = 'Logs d\'optimisation'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_type_action_display()} - {self.get_statut_display()} ({self.created_at})"

