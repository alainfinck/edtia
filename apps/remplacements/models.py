"""
Modèles pour la gestion des remplacements et absences
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone


class Absence(models.Model):
    """
    Modèle pour les absences d'enseignants
    """
    TYPE_ABSENCE_CHOICES = [
        ('maladie', 'Maladie'),
        ('formation', 'Formation'),
        ('conges', 'Congés'),
        ('maternite', 'Congé maternité'),
        ('paternite', 'Congé paternité'),
        ('deces', 'Décès famille'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('declaree', 'Déclarée'),
        ('validee', 'Validée'),
        ('remplacee', 'Remplacée'),
        ('annulee', 'Annulée'),
    ]

    enseignant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='absences')
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='absences')
    type_absence = models.CharField(max_length=20, choices=TYPE_ABSENCE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='declaree')
    
    # Période d'absence
    date_debut = models.DateField()
    date_fin = models.DateField()
    heure_debut = models.TimeField(blank=True, null=True)
    heure_fin = models.TimeField(blank=True, null=True)
    
    # Informations
    motif = models.TextField()
    justificatif = models.FileField(upload_to='justificatifs/', blank=True, null=True)
    urgence = models.BooleanField(default=False)
    
    # Gestion
    declaree_par = models.ForeignKey(
        'accounts.User',
        on_delete=models.CASCADE,
        related_name='absences_declarees'
    )
    validee_par = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='absences_validees'
    )
    date_validation = models.DateTimeField(blank=True, null=True)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'absences'
        verbose_name = 'Absence'
        verbose_name_plural = 'Absences'
        ordering = ['-date_debut']

    def __str__(self):
        return f"Absence {self.enseignant.get_full_name()} - {self.date_debut} au {self.date_fin}"

    def get_duree_jours(self):
        """Calcule la durée en jours"""
        return (self.date_fin - self.date_debut).days + 1

    def get_cours_concernes(self):
        """Retourne les cours concernés par cette absence"""
        from apps.emplois_temps.models import Cours
        return Cours.objects.filter(
            enseignant=self.enseignant,
            emploi_temps__etablissement=self.etablissement,
            emploi_temps__statut='actif'
        ).filter(
            models.Q(
                jour_semaine__in=self.get_jours_semaine_absence(),
                heure_debut__gte=self.heure_debut or '00:00',
                heure_fin__lte=self.heure_fin or '23:59'
            )
        )

    def get_jours_semaine_absence(self):
        """Retourne les jours de la semaine concernés par l'absence"""
        # Logique pour déterminer les jours de semaine
        # Simplifié ici, à adapter selon les besoins
        return [1, 2, 3, 4, 5]  # Lundi à vendredi


class Remplacant(models.Model):
    """
    Modèle pour les remplaçants disponibles
    """
    STATUT_CHOICES = [
        ('disponible', 'Disponible'),
        ('occupe', 'Occupé'),
        ('indisponible', 'Indisponible'),
    ]

    enseignant = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='remplacements')
    etablissement = models.ForeignKey('etablissements.Etablissement', on_delete=models.CASCADE, related_name='remplacants')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='disponible')
    
    # Disponibilités
    date_debut_disponibilite = models.DateField()
    date_fin_disponibilite = models.DateField(blank=True, null=True)
    heures_disponibles = models.JSONField(default=dict, blank=True)  # {"lundi": [8, 9, 10], ...}
    
    # Compétences
    matieres_enseignees = models.ManyToManyField('etablissements.Matiere', related_name='remplacants')
    niveaux_competents = models.JSONField(default=list, blank=True)
    experience_remplacement = models.PositiveIntegerField(default=0)
    
    # Préférences
    preferences_etablissement = models.JSONField(default=dict, blank=True)
    tarif_horaire = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    distance_max = models.PositiveIntegerField(default=50)  # en km
    
    # Évaluation
    note_moyenne = models.FloatField(default=0.0)
    nombre_evaluations = models.PositiveIntegerField(default=0)
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'remplacants'
        verbose_name = 'Remplaçant'
        verbose_name_plural = 'Remplaçants'
        unique_together = ['enseignant', 'etablissement']

    def __str__(self):
        return f"Remplaçant {self.enseignant.get_full_name()} - {self.etablissement.nom}"

    def is_disponible(self, date, heure=None):
        """Vérifie si le remplaçant est disponible à une date/heure donnée"""
        if self.statut != 'disponible':
            return False
        
        if date < self.date_debut_disponibilite:
            return False
        
        if self.date_fin_disponibilite and date > self.date_fin_disponibilite:
            return False
        
        if heure and self.heures_disponibles:
            jour_semaine = date.weekday() + 1  # 1 = lundi, 7 = dimanche
            if str(jour_semaine) in self.heures_disponibles:
                return heure in self.heures_disponibles[str(jour_semaine)]
        
        return True


class Remplacement(models.Model):
    """
    Modèle pour les remplacements effectués
    """
    STATUT_CHOICES = [
        ('propose', 'Proposé'),
        ('accepte', 'Accepté'),
        ('refuse', 'Refusé'),
        ('effectue', 'Effectué'),
        ('annule', 'Annulé'),
    ]

    absence = models.ForeignKey(Absence, on_delete=models.CASCADE, related_name='remplacements')
    remplacant = models.ForeignKey(Remplacant, on_delete=models.CASCADE, related_name='missions_remplacement')
    cours_remplaces = models.ManyToManyField('emplois_temps.Cours', related_name='remplacements')
    
    # Détails du remplacement
    date_remplacement = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    salle = models.ForeignKey('etablissements.Salle', on_delete=models.CASCADE, related_name='remplacements')
    
    # Statut et gestion
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='propose')
    date_proposition = models.DateTimeField(auto_now_add=True)
    date_acceptation = models.DateTimeField(blank=True, null=True)
    date_effectuation = models.DateTimeField(blank=True, null=True)
    
    # Informations
    commentaires = models.TextField(blank=True)
    evaluation_remplacant = models.JSONField(default=dict, blank=True)
    evaluation_etablissement = models.JSONField(default=dict, blank=True)
    
    # Rémunération
    tarif_applique = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    heures_remunerees = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    
    # Métadonnées
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='remplacements_crees')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'remplacements'
        verbose_name = 'Remplacement'
        verbose_name_plural = 'Remplacements'
        ordering = ['-date_remplacement']

    def __str__(self):
        return f"Remplacement {self.remplacant.enseignant.get_full_name()} - {self.date_remplacement}"

    def get_duree_heures(self):
        """Calcule la durée en heures"""
        if self.heure_debut and self.heure_fin:
            debut = self.heure_debut
            fin = self.heure_fin
            return (fin.hour - debut.hour) + (fin.minute - debut.minute) / 60.0
        return 0

    def calculer_remuneration(self):
        """Calcule la rémunération totale"""
        if self.tarif_applique and self.heures_remunerees:
            return self.tarif_applique * self.heures_remunerees
        return 0


class PropositionRemplacement(models.Model):
    """
    Modèle pour les propositions de remplacement générées par l'IA
    """
    absence = models.ForeignKey(Absence, on_delete=models.CASCADE, related_name='propositions_remplacement')
    remplacant = models.ForeignKey(Remplacant, on_delete=models.CASCADE, related_name='propositions')
    cours_concernes = models.ManyToManyField('emplois_temps.Cours', related_name='propositions_remplacement')
    
    # Score de compatibilité
    score_compatibilite = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_competence = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_disponibilite = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    score_geographique = models.FloatField(validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Détails de la proposition
    date_proposition = models.DateField()
    heures_proposees = models.JSONField(default=list, blank=True)
    salles_proposees = models.JSONField(default=list, blank=True)
    
    # Statut
    statut = models.CharField(
        max_length=20,
        choices=[
            ('generee', 'Générée'),
            ('envoyee', 'Envoyée'),
            ('acceptee', 'Acceptée'),
            ('refusee', 'Refusée'),
            ('expiree', 'Expirée'),
        ],
        default='generee'
    )
    
    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'propositions_remplacement'
        verbose_name = 'Proposition de remplacement'
        verbose_name_plural = 'Propositions de remplacement'
        ordering = ['-score_compatibilite', '-created_at']

    def __str__(self):
        return f"Proposition {self.remplacant.enseignant.get_full_name()} - Score: {self.score_compatibilite:.2f}"

    def get_score_total(self):
        """Calcule le score total pondéré"""
        return (
            self.score_compatibilite * 0.4 +
            self.score_competence * 0.3 +
            self.score_disponibilite * 0.2 +
            self.score_geographique * 0.1
        )
