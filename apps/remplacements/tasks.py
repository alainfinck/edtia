"""
Tâches Celery pour l'application remplacements
"""
from celery import shared_task
from django.utils import timezone
from .models import Absence, Remplacant, PropositionRemplacement
from apps.ia_optimisation.algorithms import OptimiseurRemplacants, PredicteurAbsences
from apps.notifications.models import Notification
import logging

logger = logging.getLogger(__name__)


@shared_task
def rechercher_remplacants_absence(absence_id):
    """
    Tâche pour rechercher automatiquement des remplaçants pour une absence
    """
    try:
        absence = Absence.objects.get(id=absence_id)
        
        # Récupérer les remplaçants disponibles
        remplacants_disponibles = Remplacant.objects.filter(
            statut='disponible',
            etablissement=absence.etablissement
        )
        
        if not remplacants_disponibles.exists():
            logger.warning(f"Aucun remplaçant disponible pour l'absence {absence_id}")
            return
        
        # Utiliser l'algorithme de matching
        optimiseur = OptimiseurRemplacants()
        matchings = optimiseur.trouver_meilleurs_remplacants(absence, remplacants_disponibles)
        
        # Créer les propositions
        propositions_crees = 0
        for matching in matchings[:5]:  # Top 5
            proposition = PropositionRemplacement.objects.create(
                absence=absence,
                remplacant=matching['remplacant'],
                score_compatibilite=matching['score_global'],
                score_competence=matching['score_competence'],
                score_disponibilite=matching['score_disponibilite'],
                score_geographique=matching['score_geographique'],
                score_experience=matching['score_experience'],
                date_proposition=absence.date_debut,
                statut='generee'
            )
            
            # Ajouter les cours concernés
            for cours in matching['details']['cours_remplacables']:
                proposition.cours_concernes.add(cours)
            
            propositions_crees += 1
        
        # Créer une notification
        Notification.objects.create(
            destinataire=absence.declaree_par,
            type_notification='propositions_remplacants',
            titre=f"Propositions de remplaçants générées",
            message=f"{propositions_crees} propositions de remplaçants ont été générées pour l'absence de {absence.enseignant.get_full_name()}.",
            donnees={'absence_id': absence_id, 'propositions_count': propositions_crees}
        )
        
        logger.info(f"Recherche de remplaçants terminée pour l'absence {absence_id}: {propositions_crees} propositions créées")
        
    except Absence.DoesNotExist:
        logger.error(f"Absence {absence_id} non trouvée")
    except Exception as e:
        logger.error(f"Erreur lors de la recherche de remplaçants pour l'absence {absence_id}: {e}")


@shared_task
def predire_absences_enseignants():
    """
    Tâche pour prédire les absences des enseignants
    """
    try:
        predicteur = PredicteurAbsences()
        
        # Récupérer tous les enseignants actifs
        enseignants = User.objects.filter(role='enseignant', is_active=True)
        
        predictions_crees = 0
        for enseignant in enseignants:
            # Préparer les données de l'enseignant
            donnees_enseignant = {
                'age': 35,  # À calculer à partir de la date de naissance
                'experience_annees': enseignant.profil_enseignant.experience_annees if hasattr(enseignant, 'profil_enseignant') else 0,
                'heures_semaine': enseignant.profil_enseignant.heures_max_semaine if hasattr(enseignant, 'profil_enseignant') else 35,
                'nombre_classes': 3,  # À calculer
                'stress_niveau': 5,  # À récupérer des évaluations
                'satisfaction_travail': 7,  # À récupérer des évaluations
                'distance_domicile': 15,  # À calculer
                'nombre_enfants': 2,  # À récupérer du profil
                'sante_generale': 8,  # À récupérer des évaluations
                'absences_annee_precedente': Absence.objects.filter(
                    enseignant=enseignant,
                    date_debut__year=timezone.now().year - 1
                ).count(),
            }
            
            # Faire la prédiction
            prediction = predicteur.predire(donnees_enseignant)
            
            if prediction and prediction['probabilite_absence'] > 0.3:  # Seuil de 30%
                # Créer une prédiction d'absence
                from apps.ia_optimisation.models import PredictionAbsence
                PredictionAbsence.objects.create(
                    enseignant=enseignant,
                    etablissement=enseignant.profil_enseignant.etablissement if hasattr(enseignant, 'profil_enseignant') else None,
                    date_prediction=timezone.now().date() + timezone.timedelta(days=7),
                    probabilite_absence=prediction['probabilite_absence'],
                    facteurs_risque=prediction['facteurs_risque'],
                    score_risque=prediction['probabilite_absence']
                )
                
                predictions_crees += 1
                
                # Créer une notification si probabilité élevée
                if prediction['probabilite_absence'] > 0.7:
                    Notification.objects.create(
                        destinataire=enseignant,
                        type_notification='prediction_absence',
                        titre="Risque d'absence détecté",
                        message=f"L'IA a détecté un risque d'absence élevé ({prediction['probabilite_absence']:.1%}) pour la semaine prochaine.",
                        donnees={'probabilite': prediction['probabilite_absence'], 'facteurs': prediction['facteurs_risque']}
                    )
        
        logger.info(f"Prédiction d'absences terminée: {predictions_crees} prédictions créées")
        
    except Exception as e:
        logger.error(f"Erreur lors de la prédiction d'absences: {e}")


@shared_task
def nettoyer_propositions_expirees():
    """
    Tâche pour nettoyer les propositions de remplaçants expirées
    """
    try:
        # Marquer comme expirées les propositions de plus de 24h
        date_limite = timezone.now() - timezone.timedelta(hours=24)
        
        propositions_expirees = PropositionRemplacement.objects.filter(
            statut='generee',
            created_at__lt=date_limite
        )
        
        count = propositions_expirees.update(statut='expiree')
        
        logger.info(f"Nettoyage des propositions expirées: {count} propositions marquées comme expirées")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des propositions expirées: {e}")


@shared_task
def evaluer_remplacements_effectues():
    """
    Tâche pour évaluer les remplacements effectués et mettre à jour les scores
    """
    try:
        from .models import Remplacement
        
        # Récupérer les remplacements effectués récemment
        remplacements = Remplacement.objects.filter(
            statut='effectue',
            date_effectuation__isnull=False
        )
        
        for remplacement in remplacements:
            # Mettre à jour le score du remplaçant
            if remplacement.evaluation_remplacant:
                note = remplacement.evaluation_remplacant.get('note', 0)
                if note > 0:
                    # Recalculer la note moyenne
                    remplacant = remplacement.remplacant
                    remplacant.nombre_evaluations += 1
                    remplacant.note_moyenne = (
                        (remplacant.note_moyenne * (remplacant.nombre_evaluations - 1) + note) 
                        / remplacant.nombre_evaluations
                    )
                    remplacant.save()
        
        logger.info(f"Évaluation des remplacements terminée: {remplacements.count()} remplacements traités")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'évaluation des remplacements: {e}")


@shared_task
def envoyer_rapport_hebdomadaire():
    """
    Tâche pour envoyer un rapport hebdomadaire aux directeurs
    """
    try:
        from apps.accounts.models import User
        
        # Récupérer tous les directeurs
        directeurs = User.objects.filter(role='directeur')
        
        for directeur in directeurs:
            # Calculer les statistiques de la semaine
            debut_semaine = timezone.now().date() - timezone.timedelta(days=7)
            
            absences_semaine = Absence.objects.filter(
                etablissement=directeur.profil_directeur.etablissement,
                date_debut__gte=debut_semaine
            ).count()
            
            remplacements_effectues = Remplacement.objects.filter(
                absence__etablissement=directeur.profil_directeur.etablissement,
                statut='effectue',
                date_effectuation__gte=debut_semaine
            ).count()
            
            # Créer une notification avec le rapport
            Notification.objects.create(
                destinataire=directeur,
                type_notification='rapport_hebdomadaire',
                titre="Rapport hebdomadaire",
                message=f"Rapport de la semaine: {absences_semaine} absences déclarées, {remplacements_effectues} remplacements effectués.",
                donnees={
                    'absences_semaine': absences_semaine,
                    'remplacements_effectues': remplacements_effectues,
                    'periode': f"{debut_semaine} à {timezone.now().date()}"
                }
            )
        
        logger.info(f"Rapport hebdomadaire envoyé à {directeurs.count()} directeurs")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi du rapport hebdomadaire: {e}")

