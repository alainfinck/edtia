# Interface Publique Edtia

## 🎯 Vue d'ensemble

L'interface publique d'Edtia est une application Django séparée qui présente la solution SaaS d'optimisation des emplois du temps éducatifs. Elle offre une expérience utilisateur moderne et professionnelle pour attirer et convertir les prospects.

## 🚀 Fonctionnalités

### Pages principales
- **Page d'accueil** (`/`) : Présentation complète d'Edtia avec fonctionnalités, cas d'usage et témoignages
- **Présentation** (`/presentation/`) : Détails sur la solution et ses avantages
- **Fonctionnalités** (`/fonctionnalites/`) : Description détaillée des fonctionnalités
- **Tarifs** (`/tarifs/`) : Plans tarifaires avec comparaison détaillée
- **Témoignages** (`/temoignages/`) : Témoignages clients approuvés
- **Blog** (`/blog/`) : Articles de blog et actualités
- **Contact** (`/contact/`) : Formulaire de contact et informations
- **Démonstration** (`/demo/`) : Formulaire de demande de démonstration

### API Endpoints
- `POST /api/demo/` : Traitement des demandes de démonstration
- `POST /api/newsletter/` : Inscription à la newsletter
- `POST /api/contact/` : Envoi de messages de contact

## 📊 Modèles de données

### DemandeDemo
Gestion des demandes de démonstration avec suivi commercial complet.

### Newsletter
Inscriptions à la newsletter avec segmentation.

### Temoignage
Témoignages clients avec système d'approbation.

### ArticleBlog
Articles de blog avec SEO et statistiques.

### ContactMessage
Messages de contact avec suivi et assignation.

## 🎨 Design et UX

### Technologies utilisées
- **TailwindCSS** : Framework CSS moderne et responsive
- **Lucide Icons** : Icônes vectorielles élégantes
- **JavaScript vanilla** : Interactions dynamiques
- **Django Templates** : Système de templates puissant

### Caractéristiques design
- Design moderne et professionnel
- Responsive design (mobile-first)
- Animations et transitions fluides
- Optimisation SEO complète
- Accessibilité respectée

## 🔧 Configuration

### Installation
L'app est déjà configurée dans `INSTALLED_APPS` :
```python
LOCAL_APPS = [
    'apps.public',
    # ... autres apps
]
```

### URLs
Les URLs sont incluses dans le fichier principal :
```python
urlpatterns = [
    path('', include('apps.public.urls')),
    # ... autres URLs
]
```

### Migrations
```bash
python manage.py makemigrations public
python manage.py migrate public
```

## 📝 Administration

L'interface d'administration Django permet de gérer :
- Demandes de démonstration avec suivi commercial
- Inscriptions newsletter
- Témoignages avec système d'approbation
- Articles de blog avec SEO
- Messages de contact avec assignation

## 🚀 Déploiement

### Variables d'environnement
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@example.com
EMAIL_HOST_PASSWORD=your_password
DEFAULT_FROM_EMAIL=your_email@example.com
```

### Fichiers statiques
```bash
python manage.py collectstatic
```

## 📈 Analytics et tracking

### Métriques disponibles
- Vues d'articles de blog
- Likes sur les articles
- Demandes de démonstration
- Inscriptions newsletter
- Messages de contact

### Intégrations possibles
- Google Analytics
- Facebook Pixel
- LinkedIn Insight Tag
- Hotjar pour l'analyse comportementale

## 🔒 Sécurité

### Mesures implémentées
- Protection CSRF sur tous les formulaires
- Validation des données côté serveur
- Sanitisation des entrées utilisateur
- Conformité RGPD

### Bonnes pratiques
- Limitation du taux de requêtes
- Validation des emails
- Gestion des erreurs sécurisée

## 🧪 Tests

### Tests recommandés
- Tests unitaires des modèles
- Tests d'intégration des formulaires
- Tests de performance
- Tests de sécurité

## 📞 Support

Pour toute question concernant l'interface publique :
- Documentation technique : `/docs/`
- Support technique : support@edtia.fr
- Contact commercial : contact@edtia.fr

