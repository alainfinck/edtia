"""
Tâches Celery pour l'application dashboard
"""
from celery import shared_task
from django.utils import timezone
from .models import ExecutionRapport, AlerteDashboard, ActivationAlerte
from apps.remplacements.models import Absence, Remplacement
from apps.emplois_temps.models import Cours
import logging

logger = logging.getLogger(__name__)


@shared_task
def executer_rapport_task(execution_id):
    """
    Tâche pour exécuter un rapport
    """
    try:
        execution = ExecutionRapport.objects.get(id=execution_id)
        rapport = execution.rapport
        
        # Simuler l'exécution du rapport
        # En réalité, ici on exécuterait la requête SQL ou l'API
        import time
        time.sleep(2)  # Simulation du temps d'exécution
        
        # Générer les données
        donnees = {
            'rapport_id': rapport.id,
            'nom': rapport.nom,
            'type': rapport.type_rapport,
            'date_generation': timezone.now().isoformat(),
            'donnees': []  # Données réelles à implémenter
        }
        
        # Mettre à jour l'exécution
        execution.statut = 'termine'
        execution.date_fin = timezone.now()
        execution.duree_execution = (execution.date_fin - execution.date_debut).total_seconds()
        execution.donnees_generes = donnees
        execution.save()
        
        logger.info(f"Rapport {rapport.nom} exécuté avec succès")
        
    except ExecutionRapport.DoesNotExist:
        logger.error(f"Exécution de rapport {execution_id} non trouvée")
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution du rapport {execution_id}: {e}")
        
        # Marquer l'exécution comme échec
        try:
            execution.statut = 'echec'
            execution.erreur_message = str(e)
            execution.date_fin = timezone.now()
            execution.save()
        except:
            pass


@shared_task
def verifier_alertes():
    """
    Tâche pour vérifier les alertes
    """
    try:
        alertes = AlerteDashboard.objects.filter(active=True)
        
        for alerte in alertes:
            # Vérifier les conditions de l'alerte
            if verifier_conditions_alerte(alerte):
                # Activer l'alerte
                activation = ActivationAlerte.objects.create(
                    alerte=alerte,
                    contexte={'verification_automatique': True}
                )
                
                # Mettre à jour l'alerte
                alerte.date_derniere_activation = timezone.now()
                alerte.nombre_activations += 1
                alerte.save()
                
                logger.info(f"Alerte {alerte.nom} activée")
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des alertes: {e}")


def verifier_conditions_alerte(alerte):
    """
    Vérifie les conditions d'une alerte
    """
    try:
        if alerte.type_alerte == 'absence_non_remplacee':
            # Vérifier les absences non remplacées
            absences_non_remplacees = Absence.objects.filter(
                statut='declaree',
                date_debut__lte=timezone.now().date()
            ).count()
            
            return absences_non_remplacees > 0
        
        elif alerte.type_alerte == 'conflit_emploi_temps':
            # Vérifier les conflits d'emploi du temps
            conflits = Cours.objects.extra(
                where=["EXISTS (SELECT 1 FROM emplois_temps_cours c2 WHERE c2.enseignant_id = emplois_temps_cours.enseignant_id AND c2.jour_semaine = emplois_temps_cours.jour_semaine AND c2.heure_debut < emplois_temps_cours.heure_fin AND c2.heure_fin > emplois_temps_cours.heure_debut AND c2.id != emplois_temps_cours.id)"]
            ).count()
            
            return conflits > 0
        
        elif alerte.type_alerte == 'salle_surchargee':
            # Vérifier les salles surchargées
            # Logique à implémenter selon les besoins
            return False
        
        elif alerte.type_alerte == 'enseignant_surcharge':
            # Vérifier les enseignants surchargés
            # Logique à implémenter selon les besoins
            return False
        
        return False
        
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des conditions de l'alerte {alerte.id}: {e}")
        return False


@shared_task
def generer_rapport_hebdomadaire():
    """
    Tâche pour générer le rapport hebdomadaire
    """
    try:
        from apps.accounts.models import User
        
        # Récupérer tous les directeurs
        directeurs = User.objects.filter(role='directeur')
        
        for directeur in directeurs:
            etablissement = directeur.profil_directeur.etablissement
            
            # Calculer les statistiques de la semaine
            debut_semaine = timezone.now().date() - timezone.timedelta(days=7)
            
            absences_semaine = Absence.objects.filter(
                etablissement=etablissement,
                date_debut__gte=debut_semaine
            ).count()
            
            remplacements_effectues = Remplacement.objects.filter(
                absence__etablissement=etablissement,
                statut='effectue',
                date_effectuation__gte=debut_semaine
            ).count()
            
            # Créer le rapport
            rapport_data = {
                'etablissement': etablissement.nom,
                'periode': f"{debut_semaine} à {timezone.now().date()}",
                'absences_semaine': absences_semaine,
                'remplacements_effectues': remplacements_effectues,
                'taux_remplacement': (remplacements_effectues / absences_semaine * 100) if absences_semaine > 0 else 0,
                'conflits_emploi_temps': 0,  # À calculer
                'alertes_actives': 0,  # À calculer
            }
            
            # Créer une notification avec le rapport
            from apps.notifications.models import Notification
            Notification.objects.create(
                destinataire=directeur,
                type_notification='rapport_hebdomadaire',
                titre="Rapport hebdomadaire",
                message=f"Rapport de la semaine: {absences_semaine} absences déclarées, {remplacements_effectues} remplacements effectués.",
                donnees=rapport_data
            )
        
        logger.info(f"Rapport hebdomadaire généré pour {directeurs.count()} directeurs")
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du rapport hebdomadaire: {e}")


@shared_task
def nettoyer_donnees_dashboard():
    """
    Tâche pour nettoyer les données anciennes du dashboard
    """
    try:
        # Nettoyer les exécutions de rapports anciennes (plus de 30 jours)
        date_limite = timezone.now() - timezone.timedelta(days=30)
        
        executions_supprimees = ExecutionRapport.objects.filter(
            date_debut__lt=date_limite
        ).delete()
        
        # Nettoyer les activations d'alertes résolues (plus de 7 jours)
        activations_supprimees = ActivationAlerte.objects.filter(
            resolue=True,
            date_resolution__lt=date_limite
        ).delete()
        
        logger.info(f"Nettoyage dashboard: {executions_supprimees[0]} exécutions et {activations_supprimees[0]} activations supprimées")
        
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des données dashboard: {e}")

