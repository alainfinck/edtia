"""
Configuration admin pour l'interface publique d'Edtia
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import DemandeDemo, Newsletter, Temoignage, ArticleBlog, ContactMessage


@admin.register(DemandeDemo)
class DemandeDemoAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'email', 'etablissement_info', 'statut_badge', 'date_demande']
    list_filter = ['statut', 'type_etablissement', 'date_demande', 'source']
    search_fields = ['nom', 'prenom', 'email', 'nom_etablissement', 'ville']
    readonly_fields = ['date_demande']
    list_per_page = 25
    
    fieldsets = (
        ('Informations de contact', {
            'fields': ('nom', 'prenom', 'email', 'telephone')
        }),
        ('Établissement', {
            'fields': ('nom_etablissement', 'type_etablissement', 'nombre_enseignants', 'ville')
        }),
        ('Demande', {
            'fields': ('message', 'statut', 'source')
        }),
        ('Suivi commercial', {
            'fields': ('commercial_assigné', 'notes_commerciales', 'date_contact', 'date_demo'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_demande',),
            'classes': ('collapse',)
        })
    )
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = 'Nom complet'
    
    def etablissement_info(self, obj):
        return f"{obj.nom_etablissement} ({obj.type_etablissement})"
    etablissement_info.short_description = 'Établissement'
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': 'orange',
            'contacte': 'blue',
            'demo_planifiee': 'green',
            'convertis': 'green',
            'abandonne': 'red'
        }
        color = colors.get(obj.statut, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'nom_complet', 'etablissement', 'date_inscription', 'actif_badge']
    list_filter = ['actif', 'date_inscription', 'source']
    search_fields = ['email', 'nom', 'prenom', 'etablissement']
    readonly_fields = ['date_inscription']
    list_per_page = 50
    
    def nom_complet(self, obj):
        if obj.nom and obj.prenom:
            return f"{obj.prenom} {obj.nom}"
        return "-"
    nom_complet.short_description = 'Nom'
    
    def actif_badge(self, obj):
        color = 'green' if obj.actif else 'red'
        text = 'Actif' if obj.actif else 'Inactif'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, text
        )
    actif_badge.short_description = 'Statut'


@admin.register(Temoignage)
class TemoignageAdmin(admin.ModelAdmin):
    list_display = ['nom_complet', 'etablissement', 'note_stars', 'statut_badge', 'date_creation']
    list_filter = ['statut', 'note', 'date_creation']
    search_fields = ['nom', 'prenom', 'etablissement', 'titre']
    readonly_fields = ['date_creation']
    list_per_page = 25
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'fonction', 'etablissement', 'photo')
        }),
        ('Témoignage', {
            'fields': ('titre', 'contenu', 'note')
        }),
        ('Publication', {
            'fields': ('statut', 'date_creation', 'date_publication')
        })
    )
    
    def nom_complet(self, obj):
        return f"{obj.prenom} {obj.nom}"
    nom_complet.short_description = 'Nom'
    
    def note_stars(self, obj):
        stars = '★' * obj.note + '☆' * (5 - obj.note)
        return format_html('<span style="color: gold;">{}</span>', stars)
    note_stars.short_description = 'Note'
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': 'orange',
            'approuve': 'green',
            'rejete': 'red'
        }
        color = colors.get(obj.statut, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'


@admin.register(ArticleBlog)
class ArticleBlogAdmin(admin.ModelAdmin):
    list_display = ['titre', 'auteur', 'categorie', 'statut_badge', 'date_creation', 'vues']
    list_filter = ['statut', 'categorie', 'date_creation', 'auteur']
    search_fields = ['titre', 'resume', 'contenu']
    readonly_fields = ['date_creation', 'date_modification', 'vues', 'likes']
    prepopulated_fields = {'slug': ('titre',)}
    list_per_page = 25
    
    fieldsets = (
        ('Contenu', {
            'fields': ('titre', 'slug', 'resume', 'contenu', 'image_principale')
        }),
        ('Métadonnées', {
            'fields': ('auteur', 'categorie', 'statut')
        }),
        ('SEO', {
            'fields': ('meta_description', 'mots_cles'),
            'classes': ('collapse',)
        }),
        ('Statistiques', {
            'fields': ('vues', 'likes'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_modification', 'date_publication'),
            'classes': ('collapse',)
        })
    )
    
    def statut_badge(self, obj):
        colors = {
            'brouillon': 'gray',
            'publie': 'green',
            'archive': 'red'
        }
        color = colors.get(obj.statut, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['nom', 'email', 'sujet', 'type_message', 'statut_badge', 'date_envoi']
    list_filter = ['statut', 'type_message', 'date_envoi']
    search_fields = ['nom', 'email', 'sujet', 'message']
    readonly_fields = ['date_envoi']
    list_per_page = 25
    
    fieldsets = (
        ('Informations de contact', {
            'fields': ('nom', 'email', 'telephone')
        }),
        ('Message', {
            'fields': ('sujet', 'type_message', 'message')
        }),
        ('Suivi', {
            'fields': ('statut', 'assigne_a', 'reponse', 'date_reponse'),
            'classes': ('collapse',)
        }),
        ('Dates', {
            'fields': ('date_envoi',),
            'classes': ('collapse',)
        })
    )
    
    def statut_badge(self, obj):
        colors = {
            'nouveau': 'blue',
            'lu': 'orange',
            'repondu': 'green',
            'ferme': 'gray'
        }
        color = colors.get(obj.statut, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_statut_display()
        )
    statut_badge.short_description = 'Statut'