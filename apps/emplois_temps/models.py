"""
Modèles pour la gestion des emplois du temps
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Periode(models.Model):
    """
    Modèle pour les périodes scolaires (trimestres, semestres, etc.)
    """
    nom = models.CharField(max_length=100)
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='periodes')
    date_debut = models.DateField()
    date_fin = models.DateField()
    numero_periode = models.PositiveIntegerField()
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'periodes'
        verbose_name = 'Période'
        verbose_name_plural = 'Périodes'
        unique_together = ['etablissement', 'numero_periode']
        ordering = ['numero_periode']

    def __str__(self):
        return f"{self.nom} - {self.etablissement.nom}"


class EmploiTemps(models.Model):
    """
    Modèle principal pour les emplois du temps
    """
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('propose', 'Proposé'),
        ('valide', 'Validé'),
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
    ]

    nom = models.CharField(max_length=200)
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='emplois_temps')
    periode = models.ForeignKey(Periode, on_delete=models.CASCADE, related_name='emplois_temps')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_validation = models.DateTimeField(blank=True, null=True)
    date_activation = models.DateTimeField(blank=True, null=True)
    createur = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='emplois_temps_crees')
    validateur = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='emplois_temps_valides'
    )
    contraintes_appliquees = models.JSONField(default=dict, blank=True)
    score_optimisation = models.FloatField(default=0.0)
    commentaires = models.TextField(blank=True)
    version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'emplois_temps'
        verbose_name = 'Emploi du temps'
        verbose_name_plural = 'Emplois du temps'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} - {self.etablissement.nom} ({self.get_statut_display()})"

    def get_nombre_cours(self):
        return self.cours.count()

    def get_nombre_enseignants(self):
        return self.cours.values('enseignant').distinct().count()


class Cours(models.Model):
    """
    Modèle pour les cours individuels dans un emploi du temps
    """
    JOURS_SEMAINE = [
        (1, 'Lundi'),
        (2, 'Mardi'),
        (3, 'Mercredi'),
        (4, 'Jeudi'),
        (5, 'Vendredi'),
        (6, 'Samedi'),
        (7, 'Dimanche'),
    ]

    emploi_temps = models.ForeignKey(EmploiTemps, on_delete=models.CASCADE, related_name='cours')
    classe = models.ForeignKey('etablissements.Classe', on_delete=models.CASCADE, related_name='cours')
    matiere = models.ForeignKey('etablissements.Matiere', on_delete=models.CASCADE, related_name='cours')
    enseignant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='cours')
    salle = models.ForeignKey('etablissements.Salle', on_delete=models.CASCADE, related_name='cours')
    
    jour_semaine = models.PositiveIntegerField(choices=JOURS_SEMAINE)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    duree = models.PositiveIntegerField()  # en minutes
    
    # Informations supplémentaires
    type_cours = models.CharField(
        max_length=20,
        choices=[
            ('cours', 'Cours'),
            ('td', 'Travaux dirigés'),
            ('tp', 'Travaux pratiques'),
            ('examen', 'Examen'),
            ('reunion', 'Réunion'),
            ('autre', 'Autre'),
        ],
        default='cours'
    )
    description = models.TextField(blank=True)
    contraintes_specifiques = models.JSONField(default=dict, blank=True)
    
    # Statut et validation
    statut = models.CharField(
        max_length=20,
        choices=[
            ('planifie', 'Planifié'),
            ('confirme', 'Confirmé'),
            ('annule', 'Annulé'),
            ('reporte', 'Reporté'),
        ],
        default='planifie'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cours'
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        ordering = ['jour_semaine', 'heure_debut']
        unique_together = ['emploi_temps', 'classe', 'jour_semaine', 'heure_debut']

    def __str__(self):
        return f"{self.matiere.nom} - {self.classe.nom} - {self.get_jour_semaine_display()} {self.heure_debut}"

    def get_duree_heures(self):
        """Retourne la durée en heures décimales"""
        return self.duree / 60.0

    def is_en_conflit(self):
        """Vérifie s'il y a des conflits avec d'autres cours"""
        conflits = Cours.objects.filter(
            emploi_temps=self.emploi_temps,
            jour_semaine=self.jour_semaine,
            enseignant=self.enseignant
        ).exclude(id=self.id).filter(
            models.Q(
                heure_debut__lt=self.heure_fin,
                heure_fin__gt=self.heure_debut
            )
        )
        return conflits.exists()


class Contrainte(models.Model):
    """
    Modèle pour les contraintes d'emploi du temps
    """
    TYPE_CHOICES = [
        ('enseignant', 'Contrainte enseignant'),
        ('salle', 'Contrainte salle'),
        ('classe', 'Contrainte classe'),
        ('matiere', 'Contrainte matière'),
        ('globale', 'Contrainte globale'),
    ]

    PRIORITE_CHOICES = [
        (1, 'Très faible'),
        (2, 'Faible'),
        (3, 'Moyenne'),
        (4, 'Élevée'),
        (5, 'Critique'),
    ]

    nom = models.CharField(max_length=200)
    type_contrainte = models.CharField(max_length=20, choices=TYPE_CHOICES)
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='contraintes')
    priorite = models.PositiveIntegerField(choices=PRIORITE_CHOICES, default=3)
    description = models.TextField()
    regle = models.JSONField()  # Règle de contrainte en format JSON
    actif = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='contraintes_creees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'contraintes'
        verbose_name = 'Contrainte'
        verbose_name_plural = 'Contraintes'
        ordering = ['-priorite', 'nom']

    def __str__(self):
        return f"{self.nom} ({self.get_priorite_display()})"


class HistoriqueEmploiTemps(models.Model):
    """
    Modèle pour l'historique des modifications d'emploi du temps
    """
    emploi_temps = models.ForeignKey(EmploiTemps, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(
        max_length=50,
        choices=[
            ('creation', 'Création'),
            ('modification', 'Modification'),
            ('validation', 'Validation'),
            ('activation', 'Activation'),
            ('archivage', 'Archivage'),
            ('suppression', 'Suppression'),
        ]
    )
    utilisateur = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='actions_emploi_temps')
    description = models.TextField()
    donnees_avant = models.JSONField(blank=True, null=True)
    donnees_apres = models.JSONField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'historique_emplois_temps'
        verbose_name = 'Historique emploi du temps'
        verbose_name_plural = 'Historique emplois du temps'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.emploi_temps.nom} - {self.get_action_display()} par {self.utilisateur.get_full_name()}"

