"""
Modèles pour la gestion des établissements scolaires
"""
from django.db import models
from django.core.validators import RegexValidator


class Academie(models.Model):
    """
    Modèle pour les académies (rectorats)
    """
    nom = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    region = models.CharField(max_length=100)
    ville_chef_lieu = models.CharField(max_length=100)
    adresse = models.TextField()
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    site_web = models.URLField(blank=True)
    recteur = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'academies'
        verbose_name = 'Académie'
        verbose_name_plural = 'Académies'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Etablissement(models.Model):
    """
    Modèle pour les établissements scolaires
    """
    TYPE_CHOICES = [
        ('maternelle', 'École maternelle'),
        ('primaire', 'École primaire'),
        ('elementaire', 'École élémentaire'),
        ('college', 'Collège'),
        ('lycee_general', 'Lycée général'),
        ('lycee_technique', 'Lycée technique'),
        ('lycee_professionnel', 'Lycée professionnel'),
        ('superieur', 'Établissement supérieur'),
    ]

    STATUT_CHOICES = [
        ('public', 'Public'),
        ('prive', 'Privé sous contrat'),
        ('prive_hors_contrat', 'Privé hors contrat'),
    ]

    nom = models.CharField(max_length=200)
    type_etablissement = models.CharField(max_length=30, choices=TYPE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES)
    uai = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(regex=r'^\d{7}[A-Z]$', message="Format UAI invalide")]
    )
    academie = models.ForeignKey(Academie, on_delete=models.CASCADE, related_name='etablissements')
    
    # Adresse
    adresse = models.TextField()
    code_postal = models.CharField(max_length=10)
    ville = models.CharField(max_length=100)
    departement = models.CharField(max_length=3)
    region = models.CharField(max_length=100)
    
    # Contact
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    site_web = models.URLField(blank=True)
    
    # Informations administratives
    directeur = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='etablissement_dirige'
    )
    date_ouverture = models.DateField(blank=True, null=True)
    capacite_eleves = models.PositiveIntegerField(default=0)
    nombre_classes = models.PositiveIntegerField(default=0)
    
    # Configuration emploi du temps
    heures_debut_journee = models.TimeField(default='08:00')
    heures_fin_journee = models.TimeField(default='17:00')
    duree_creneau = models.PositiveIntegerField(default=55)  # en minutes
    pause_dejeuner = models.PositiveIntegerField(default=60)  # en minutes
    jours_ouverture = models.JSONField(default=list)  # [1,2,3,4,5] pour lundi-vendredi
    
    # Paramètres IA
    contraintes_etablissement = models.JSONField(default=dict, blank=True)
    preferences_optimisation = models.JSONField(default=dict, blank=True)
    
    # Statut
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'etablissements'
        verbose_name = 'Établissement'
        verbose_name_plural = 'Établissements'
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} ({self.get_type_etablissement_display()})"

    def get_nombre_enseignants(self):
        return self.enseignants.filter(statut='actif').count()

    def get_nombre_classes(self):
        return self.classes.filter(actif=True).count()


class Classe(models.Model):
    """
    Modèle pour les classes
    """
    nom = models.CharField(max_length=50)  # Ex: "6ème A", "CM2", "Terminale S"
    niveau = models.CharField(max_length=20)  # Ex: "6ème", "CM2", "Terminale"
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='classes')
    professeur_principal = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes_dirigees'
    )
    nombre_eleves = models.PositiveIntegerField(default=0)
    capacite_max = models.PositiveIntegerField(default=30)
    salle_principale = models.ForeignKey(
        'Salle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classe_principale'
    )
    matieres = models.ManyToManyField('Matiere', through='ClasseMatiere')
    horaires_specifiques = models.JSONField(default=dict, blank=True)
    contraintes_classe = models.JSONField(default=list, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'classes'
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        unique_together = ['nom', 'etablissement']
        ordering = ['niveau', 'nom']

    def __str__(self):
        return f"{self.nom} - {self.etablissement.nom}"


class Matiere(models.Model):
    """
    Modèle pour les matières enseignées
    """
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    couleur = models.CharField(max_length=7, default='#3B82F6')  # Code couleur hex
    description = models.TextField(blank=True)
    niveau_enseignement = models.CharField(
        max_length=20,
        choices=[
            ('maternelle', 'Maternelle'),
            ('primaire', 'Primaire'),
            ('college', 'Collège'),
            ('lycee', 'Lycée'),
            ('superieur', 'Supérieur'),
        ]
    )
    heures_semaine_standard = models.PositiveIntegerField(default=0)
    contraintes_matiere = models.JSONField(default=dict, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'matieres'
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'
        ordering = ['nom']

    def __str__(self):
        return self.nom


class ClasseMatiere(models.Model):
    """
    Modèle de liaison entre classes et matières avec heures spécifiques
    """
    classe = models.ForeignKey(Classe, on_delete=models.CASCADE)
    matiere = models.ForeignKey(Matiere, on_delete=models.CASCADE)
    heures_semaine = models.PositiveIntegerField()
    enseignant_principal = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='matieres_enseignees'
    )
    contraintes_specifiques = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'classe_matieres'
        verbose_name = 'Matière de classe'
        verbose_name_plural = 'Matières de classes'
        unique_together = ['classe', 'matiere']

    def __str__(self):
        return f"{self.classe.nom} - {self.matiere.nom} ({self.heures_semaine}h/sem)"


class Salle(models.Model):
    """
    Modèle pour les salles de classe
    """
    TYPE_CHOICES = [
        ('classe', 'Salle de classe'),
        ('laboratoire', 'Laboratoire'),
        ('informatique', 'Salle informatique'),
        ('sport', 'Salle de sport'),
        ('musique', 'Salle de musique'),
        ('art', 'Salle d\'arts plastiques'),
        ('bibliotheque', 'Bibliothèque'),
        ('cantine', 'Cantine'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100)
    numero = models.CharField(max_length=20, blank=True)
    type_salle = models.CharField(max_length=20, choices=TYPE_CHOICES)
    etablissement = models.ForeignKey(Etablissement, on_delete=models.CASCADE, related_name='salles')
    capacite = models.PositiveIntegerField(default=30)
    equipements = models.JSONField(default=list, blank=True)  # Liste des équipements
    contraintes_salle = models.JSONField(default=dict, blank=True)
    disponibilites = models.JSONField(default=dict, blank=True)
    actif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'salles'
        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'
        unique_together = ['nom', 'etablissement']
        ordering = ['nom']

    def __str__(self):
        return f"{self.nom} - {self.etablissement.nom}"

    def is_disponible(self, jour, heure):
        """Vérifie si la salle est disponible à un moment donné"""
        if not self.actif:
            return False
        
        # Vérifier les disponibilités spécifiques
        if self.disponibilites:
            jour_str = str(jour)
            if jour_str in self.disponibilites:
                heures_dispo = self.disponibilites[jour_str]
                return heure in heures_dispo
        
        return True

