"""
Modèles pour la gestion des comptes utilisateurs
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Modèle utilisateur personnalisé pour Edtia
    """
    ROLE_CHOICES = [
        ('directeur', 'Directeur d\'établissement'),
        ('enseignant', 'Enseignant'),
        ('rectorat', 'Personnel rectorat'),
        ('admin', 'Administrateur système'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='enseignant')
    telephone = models.CharField(
        max_length=15,
        validators=[RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Format de téléphone invalide")],
        blank=True
    )
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    date_naissance = models.DateField(blank=True, null=True)
    adresse = models.TextField(blank=True)
    ville = models.CharField(max_length=100, blank=True)
    code_postal = models.CharField(max_length=10, blank=True)
    pays = models.CharField(max_length=100, default='France')
    date_embauche = models.DateField(blank=True, null=True)
    statut = models.CharField(
        max_length=20,
        choices=[
            ('actif', 'Actif'),
            ('inactif', 'Inactif'),
            ('suspendu', 'Suspendu'),
        ],
        default='actif'
    )
    preferences_notifications = models.JSONField(default=dict, blank=True, null=True)
    derniere_connexion = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"

    def get_full_name(self):
        """Retourne le nom complet de l'utilisateur"""
        return f"{self.first_name} {self.last_name}".strip() or self.username

    def is_directeur(self):
        return self.role == 'directeur'

    def is_enseignant(self):
        return self.role == 'enseignant'

    def is_rectorat(self):
        return self.role == 'rectorat'

    def is_admin(self):
        return self.role == 'admin'


class ProfilEnseignant(models.Model):
    """
    Profil spécifique pour les enseignants
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_enseignant')
    numero_enseignant = models.CharField(max_length=20, unique=True)
    specialite = models.CharField(max_length=100)
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
    heures_max_semaine = models.PositiveIntegerField(default=35)
    heures_max_jour = models.PositiveIntegerField(default=8)
    disponibilites = models.JSONField(default=dict, blank=True)  # Format: {"lundi": [8, 9, 10], ...}
    contraintes = models.JSONField(default=list, blank=True)  # Liste des contraintes
    competences = models.JSONField(default=list, blank=True)  # Matières enseignées
    experience_annees = models.PositiveIntegerField(default=0)
    formation_continue = models.JSONField(default=list, blank=True)
    notes_evaluation = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profils_enseignants'
        verbose_name = 'Profil Enseignant'
        verbose_name_plural = 'Profils Enseignants'

    def __str__(self):
        return f"Profil de {self.user.get_full_name()}"


class ProfilDirecteur(models.Model):
    """
    Profil spécifique pour les directeurs d'établissement
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_directeur')
    numero_directeur = models.CharField(max_length=20, unique=True)
    etablissement = models.ForeignKey(
        'etablissements.Etablissement',
        on_delete=models.CASCADE,
        related_name='directeurs'
    )
    date_nomination = models.DateField()
    autorites_hierarchiques = models.JSONField(default=list, blank=True)
    permissions = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profils_directeurs'
        verbose_name = 'Profil Directeur'
        verbose_name_plural = 'Profils Directeurs'

    def __str__(self):
        return f"Directeur {self.user.get_full_name()} - {self.etablissement.nom}"


class ProfilRectorat(models.Model):
    """
    Profil spécifique pour le personnel rectorat
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil_rectorat')
    numero_agent = models.CharField(max_length=20, unique=True)
    service = models.CharField(max_length=100)
    niveau_acces = models.CharField(
        max_length=20,
        choices=[
            ('agent', 'Agent'),
            ('chef_service', 'Chef de service'),
            ('inspecteur', 'Inspecteur'),
            ('recteur', 'Recteur'),
        ]
    )
    academie = models.CharField(max_length=100)
    etablissements_suivis = models.ManyToManyField(
        'etablissements.Etablissement',
        blank=True,
        related_name='personnel_rectorat'
    )
    permissions_systeme = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'profils_rectorat'
        verbose_name = 'Profil Rectorat'
        verbose_name_plural = 'Profils Rectorat'

    def __str__(self):
        return f"{self.get_niveau_acces_display()} {self.user.get_full_name()} - {self.service}"
