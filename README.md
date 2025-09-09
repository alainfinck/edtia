# Edtia - Solution SaaS d'optimisation des emplois du temps éducatifs

## Description

Edtia est une solution SaaS révolutionnaire d'optimisation des emplois du temps éducatifs alimentée par l'intelligence artificielle. Elle permet de gérer intelligemment les remplaçants, optimiser les ressources pédagogiques et améliorer l'efficacité des établissements scolaires.

## Fonctionnalités principales

### 1. Optimisation des emplois du temps
- **Algorithmes d'IA avancés** : Utilisation de l'optimisation par contraintes (CSP) et de l'apprentissage automatique
- **Résolution automatique des conflits** : Détection et résolution des conflits d'horaires
- **Respect des contraintes légales** : Conformité aux réglementations éducatives
- **Optimisation des ressources** : Utilisation optimale des salles et équipements

### 2. Gestion intelligente des remplaçants
- **Matching automatique** : Proposition de remplaçants qualifiés en temps réel
- **Évaluation des compétences** : Scoring basé sur l'expérience et les matières enseignées
- **Géolocalisation** : Prise en compte de la distance et des préférences géographiques
- **Notifications en temps réel** : Alertes automatiques pour tous les acteurs

### 3. Prédiction d'absences
- **Machine Learning** : Modèles prédictifs basés sur l'historique et les facteurs de risque
- **Analyse des tendances** : Identification des patterns d'absences
- **Recommandations proactives** : Suggestions d'actions préventives
- **Facteurs de risque** : Analyse de la charge de travail, stress, santé, etc.

### 4. Tableaux de bord adaptés
- **Vue directeur** : Statistiques d'établissement, gestion des conflits, monitoring
- **Vue enseignant** : Emploi du temps personnel, absences, remplacements
- **Vue rectorat** : Vue d'ensemble multi-établissements, rapports, alertes

### 5. Notifications intelligentes
- **Multi-canal** : Email, SMS, notifications push, application
- **Personnalisées** : Adaptation selon les préférences et le rôle
- **Temps réel** : Alertes instantanées pour les situations critiques
- **Gestion des priorités** : Classification automatique par urgence

## Architecture technique

### Backend
- **Django 4.2** : Framework web Python robuste et sécurisé
- **PostgreSQL** : Base de données relationnelle performante
- **Celery + Redis** : Traitement asynchrone des tâches lourdes
- **Django REST Framework** : API REST complète

### Frontend
- **TailwindCSS** : Framework CSS utilitaire pour un design moderne
- **Lucide Icons** : Bibliothèque d'icônes cohérente
- **JavaScript vanilla** : Interactivité sans dépendances lourdes
- **Responsive design** : Compatible mobile et desktop

### Intelligence Artificielle
- **OR-Tools** : Optimisation par contraintes pour les emplois du temps
- **Scikit-learn** : Machine learning pour la prédiction d'absences
- **NumPy/SciPy** : Calculs scientifiques et statistiques
- **Pandas** : Manipulation et analyse de données

## Installation

### Prérequis
- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- Node.js 16+ (pour les assets)

### Installation
```bash
# Cloner le repository
git clone https://github.com/edtia/edtia.git
cd edtia

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configuration de la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur de développement
python manage.py runserver
```

### Configuration
1. Copier `.env.example` vers `.env`
2. Configurer les variables d'environnement
3. Configurer PostgreSQL et Redis
4. Lancer Celery : `celery -A edtia worker -l info`

## Utilisation

### Cas d'usage 1 : Absence de dernière minute
1. **8h00** : Un professeur annonce son absence pour 8h30
2. **8h05** : L'IA identifie automatiquement les cours concernés
3. **8h10** : Proposition de 3 remplaçants qualifiés avec scores
4. **8h15** : Notification automatique aux élèves et ajustement des salles

### Cas d'usage 2 : Optimisation trimestrielle
1. **Analyse** : L'IA analyse les emplois du temps actuels
2. **Optimisation** : Résolution automatique des conflits en 2 minutes
3. **Validation** : Proposition soumise au directeur avec rapport
4. **Déploiement** : Activation automatique et notifications

## Modèle économique

### Plan Starter (29€/mois)
- Jusqu'à 20 enseignants
- Optimisation emploi du temps
- Gestion des remplaçants
- Notifications de base
- Support email

### Plan Professional (79€/mois)
- Jusqu'à 100 enseignants
- Prédiction d'absences IA
- Analytics avancées
- API complète
- Support prioritaire

### Plan Enterprise (Sur mesure)
- Illimité
- Tableau de bord rectorat
- Multi-établissements
- Déploiement sur site
- Support dédié 24/7

## API

### Endpoints principaux
- `GET /api/emplois-temps/` : Liste des emplois du temps
- `POST /api/emplois-temps/{id}/optimiser/` : Optimiser un emploi du temps
- `GET /api/remplacements/` : Liste des remplacements
- `POST /api/remplacements/propositions/generer/` : Générer des propositions
- `GET /api/ia/predire/` : Prédire les absences
- `GET /api/dashboard/statistiques/` : Statistiques du tableau de bord

### Authentification
- Token d'authentification requis
- Permissions basées sur les rôles
- Rate limiting pour la sécurité

## Sécurité

- **Chiffrement** : Données sensibles chiffrées
- **Authentification** : Système d'authentification robuste
- **Autorisation** : Contrôle d'accès granulaire
- **Audit** : Logs détaillés des actions
- **RGPD** : Conformité aux réglementations

## Performance

- **Cache Redis** : Mise en cache des requêtes fréquentes
- **Optimisation base de données** : Index et requêtes optimisées
- **Traitement asynchrone** : Tâches lourdes en arrière-plan
- **CDN** : Distribution des assets statiques

## Monitoring

- **Logs structurés** : Traçabilité complète des actions
- **Métriques** : Surveillance des performances
- **Alertes** : Notifications automatiques en cas de problème
- **Rapports** : Tableaux de bord de monitoring

## Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## Support

- **Documentation** : [docs.edtia.fr](https://docs.edtia.fr)
- **Support technique** : support@edtia.fr
- **Communauté** : [forum.edtia.fr](https://forum.edtia.fr)
- **Statut** : [status.edtia.fr](https://status.edtia.fr)

## Roadmap

### Q1 2024
- [ ] Intégration calendrier externe
- [ ] Application mobile native
- [ ] API webhooks

### Q2 2024
- [ ] Intelligence artificielle avancée
- [ ] Intégration systèmes existants
- [ ] Analytics prédictives

### Q3 2024
- [ ] Marketplace de remplaçants
- [ ] Formation en ligne
- [ ] Certification qualité

---

**Edtia** - Révolutionnez la gestion de vos emplois du temps éducatifs avec l'intelligence artificielle.

