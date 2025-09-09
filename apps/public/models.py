"""
Modèles pour l'interface publique d'Edtia
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class DemandeDemo(models.Model):
    """
    Modèle pour les demandes de démonstration
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('contacte', 'Contacté'),
        ('demo_planifiee', 'Démo planifiée'),
        ('convertis', 'Converti'),
        ('abandonne', 'Abandonné'),
    ]

    TYPE_ETABLISSEMENT_CHOICES = [
        ('ecole_primaire', 'École primaire'),
        ('college', 'Collège'),
        ('lycee', 'Lycée'),
        ('universite', 'Université'),
        ('centre_formation', 'Centre de formation'),
        ('autre', 'Autre'),
    ]

    # Informations de contact
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    
    # Informations sur l'établissement
    nom_etablissement = models.CharField(max_length=200)
    type_etablissement = models.CharField(max_length=50, choices=TYPE_ETABLISSEMENT_CHOICES)
    nombre_enseignants = models.PositiveIntegerField()
    ville = models.CharField(max_length=100)
    
    # Détails de la demande
    message = models.TextField(blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    
    # Suivi commercial
    commercial_assigné = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes_commerciales = models.TextField(blank=True)
    
    # Dates
    date_demande = models.DateTimeField(auto_now_add=True)
    date_contact = models.DateTimeField(null=True, blank=True)
    date_demo = models.DateTimeField(null=True, blank=True)
    
    # Source de la demande
    source = models.CharField(max_length=100, default='site_web')
    
    class Meta:
        db_table = 'demandes_demo'
        verbose_name = 'Demande de démonstration'
        verbose_name_plural = 'Demandes de démonstration'
        ordering = ['-date_demande']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.nom_etablissement}"


class Newsletter(models.Model):
    """
    Modèle pour l'inscription à la newsletter
    """
    email = models.EmailField(unique=True)
    nom = models.CharField(max_length=100, blank=True)
    prenom = models.CharField(max_length=100, blank=True)
    etablissement = models.CharField(max_length=200, blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    source = models.CharField(max_length=100, default='site_web')
    
    class Meta:
        db_table = 'newsletter'
        verbose_name = 'Inscription newsletter'
        verbose_name_plural = 'Inscriptions newsletter'
        ordering = ['-date_inscription']

    def __str__(self):
        return f"{self.email} - {self.date_inscription.strftime('%d/%m/%Y')}"


class Temoignage(models.Model):
    """
    Modèle pour les témoignages clients
    """
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('rejete', 'Rejeté'),
    ]

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    fonction = models.CharField(max_length=100)
    etablissement = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='temoignages/', blank=True, null=True)
    
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    note = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'temoignages'
        verbose_name = 'Témoignage'
        verbose_name_plural = 'Témoignages'
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.etablissement}"


class ArticleBlog(models.Model):
    """
    Modèle pour les articles de blog
    """
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]

    CATEGORIE_CHOICES = [
        ('actualites', 'Actualités'),
        ('tutoriels', 'Tutoriels'),
        ('cas_usage', 'Cas d\'usage'),
        ('technique', 'Technique'),
        ('partenaires', 'Partenaires'),
    ]

    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    resume = models.TextField(max_length=500)
    contenu = models.TextField()
    
    auteur = models.ForeignKey(User, on_delete=models.CASCADE)
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES)
    image_principale = models.ImageField(upload_to='blog/', blank=True, null=True)
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True)
    mots_cles = models.CharField(max_length=200, blank=True)
    
    # Statistiques
    vues = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'articles_blog'
        verbose_name = 'Article de blog'
        verbose_name_plural = 'Articles de blog'
        ordering = ['-date_publication']

    def __str__(self):
        return self.titre


class ContactMessage(models.Model):
    """
    Modèle pour les messages de contact
    """
    STATUT_CHOICES = [
        ('nouveau', 'Nouveau'),
        ('lu', 'Lu'),
        ('repondu', 'Répondu'),
        ('ferme', 'Fermé'),
    ]

    TYPE_MESSAGE_CHOICES = [
        ('question_generale', 'Question générale'),
        ('support_technique', 'Support technique'),
        ('demande_commerciale', 'Demande commerciale'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20, blank=True)
    sujet = models.CharField(max_length=200)
    type_message = models.CharField(max_length=50, choices=TYPE_MESSAGE_CHOICES, default='question_generale')
    message = models.TextField()
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='nouveau')
    date_envoi = models.DateTimeField(auto_now_add=True)
    date_reponse = models.DateTimeField(null=True, blank=True)
    
    # Suivi
    assigne_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    reponse = models.TextField(blank=True)
    
    class Meta:
        db_table = 'messages_contact'
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'
        ordering = ['-date_envoi']

    def __str__(self):
        return f"{self.nom} - {self.sujet}"