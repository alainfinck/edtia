"""
Vues pour l'interface publique d'Edtia
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import json

from .models import DemandeDemo, Newsletter, Temoignage, ArticleBlog, ContactMessage


def accueil(request):
    """
    Page d'accueil publique avec présentation complète d'Edtia
    """
    # Récupérer les témoignages approuvés
    temoignages = Temoignage.objects.filter(statut='approuve')[:3]
    
    # Récupérer les derniers articles de blog
    articles = ArticleBlog.objects.filter(statut='publie')[:3]
    
    context = {
        'temoignages': temoignages,
        'articles': articles,
    }
    
    return render(request, 'public/accueil.html', context)


def presentation(request):
    """
    Page de présentation détaillée d'Edtia
    """
    return render(request, 'public/presentation.html')


def fonctionnalites(request):
    """
    Page détaillée des fonctionnalités
    """
    return render(request, 'public/fonctionnalites.html')


def tarifs(request):
    """
    Page des tarifs et plans
    """
    return render(request, 'public/tarifs.html')


def temoignages(request):
    """
    Page des témoignages clients
    """
    temoignages = Temoignage.objects.filter(statut='approuve')
    
    context = {
        'temoignages': temoignages,
    }
    
    return render(request, 'public/temoignages.html', context)


def blog(request):
    """
    Page du blog avec liste des articles
    """
    articles = ArticleBlog.objects.filter(statut='publie')
    
    context = {
        'articles': articles,
    }
    
    return render(request, 'public/blog.html', context)


def article_detail(request, slug):
    """
    Détail d'un article de blog
    """
    article = get_object_or_404(ArticleBlog, slug=slug, statut='publie')
    
    # Incrémenter le compteur de vues
    article.vues += 1
    article.save(update_fields=['vues'])
    
    # Articles similaires
    articles_similaires = ArticleBlog.objects.filter(
        statut='publie',
        categorie=article.categorie
    ).exclude(id=article.id)[:3]
    
    context = {
        'article': article,
        'articles_similaires': articles_similaires,
    }
    
    return render(request, 'public/article_detail.html', context)


def contact(request):
    """
    Page de contact
    """
    return render(request, 'public/contact.html')


def demo(request):
    """
    Page de demande de démonstration
    """
    return render(request, 'public/demo.html')


def demo_interactive(request):
    """
    Page de démonstration interactive avec génération d'emplois du temps
    """
    return render(request, 'public/demo_interactive.html')


def test_service(request):
    """
    Page de test du service avec simulateur interactif
    """
    return render(request, 'public/test_service.html')


@require_http_methods(["POST"])
@csrf_exempt
def demande_demo(request):
    """
    Traitement de la demande de démonstration
    """
    try:
        data = json.loads(request.body)
        
        # Créer la demande de démo
        demande = DemandeDemo.objects.create(
            nom=data.get('nom'),
            prenom=data.get('prenom'),
            email=data.get('email'),
            telephone=data.get('telephone', ''),
            nom_etablissement=data.get('nom_etablissement'),
            type_etablissement=data.get('type_etablissement'),
            nombre_enseignants=data.get('nombre_enseignants'),
            ville=data.get('ville'),
            message=data.get('message', ''),
            source=data.get('source', 'site_web')
        )
        
        # Envoyer un email de confirmation
        send_mail(
            subject='Confirmation de votre demande de démonstration Edtia',
            message=f"""
            Bonjour {demande.prenom} {demande.nom},
            
            Nous avons bien reçu votre demande de démonstration pour {demande.nom_etablissement}.
            
            Notre équipe commerciale vous contactera dans les plus brefs délais pour planifier votre démonstration personnalisée.
            
            Cordialement,
            L'équipe Edtia
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[demande.email],
            fail_silently=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Votre demande a été envoyée avec succès. Nous vous contacterons bientôt !'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def inscription_newsletter(request):
    """
    Inscription à la newsletter
    """
    try:
        data = json.loads(request.body)
        
        email = data.get('email')
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'L\'email est requis.'
            }, status=400)
        
        # Vérifier si l'email existe déjà
        if Newsletter.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Cet email est déjà inscrit à notre newsletter.'
            }, status=400)
        
        # Créer l'inscription
        Newsletter.objects.create(
            email=email,
            nom=data.get('nom', ''),
            prenom=data.get('prenom', ''),
            etablissement=data.get('etablissement', ''),
            source=data.get('source', 'site_web')
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Vous êtes maintenant inscrit à notre newsletter !'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=500)


@require_http_methods(["POST"])
@csrf_exempt
def message_contact(request):
    """
    Envoi d'un message de contact
    """
    try:
        data = json.loads(request.body)
        
        # Créer le message
        message = ContactMessage.objects.create(
            nom=data.get('nom'),
            email=data.get('email'),
            telephone=data.get('telephone', ''),
            sujet=data.get('sujet'),
            type_message=data.get('type_message', 'question_generale'),
            message=data.get('message')
        )
        
        # Envoyer un email de confirmation
        send_mail(
            subject='Confirmation de votre message - Edtia',
            message=f"""
            Bonjour {message.nom},
            
            Nous avons bien reçu votre message concernant : {message.sujet}
            
            Notre équipe vous répondra dans les plus brefs délais.
            
            Cordialement,
            L'équipe Edtia
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[message.email],
            fail_silently=True
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Votre message a été envoyé avec succès. Nous vous répondrons bientôt !'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Une erreur est survenue. Veuillez réessayer.'
        }, status=500)


def mentions_legales(request):
    """
    Page des mentions légales
    """
    return render(request, 'public/mentions_legales.html')


def politique_confidentialite(request):
    """
    Page de la politique de confidentialité
    """
    return render(request, 'public/politique_confidentialite.html')


def cgu(request):
    """
    Page des conditions générales d'utilisation
    """
    return render(request, 'public/cgu.html')