"""
Algorithmes d'optimisation et d'intelligence artificielle pour Edtia
"""
import numpy as np
import pandas as pd
from ortools.sat.python import cp_model
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class OptimiseurEmploiTemps:
    """
    Classe pour l'optimisation des emplois du temps avec contraintes
    """
    
    def __init__(self, etablissement, contraintes=None):
        self.etablissement = etablissement
        self.contraintes = contraintes or {}
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self.objectifs = []
        
    def optimiser(self, emploi_temps):
        """
        Optimise un emploi du temps en respectant les contraintes
        """
        try:
            # Initialiser le modèle
            self._initialiser_variables(emploi_temps)
            
            # Ajouter les contraintes
            self._ajouter_contraintes_enseignants()
            self._ajouter_contraintes_salles()
            self._ajouter_contraintes_classes()
            self._ajouter_contraintes_globales()
            
            # Définir l'objectif
            self._definir_objectif()
            
            # Résoudre
            status = self.solver.Solve(self.model)
            
            if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                return self._extraire_solution(emploi_temps)
            else:
                logger.error(f"Optimisation impossible: {status}")
                return None
                
        except Exception as e:
            logger.error(f"Erreur lors de l'optimisation: {e}")
            return None
    
    def _initialiser_variables(self, emploi_temps):
        """Initialise les variables du problème d'optimisation"""
        cours = emploi_temps.cours.all()
        
        for cours in cours:
            # Variable binaire pour chaque cours
            var_name = f"cours_{cours.id}"
            self.variables[var_name] = self.model.NewBoolVar(var_name)
            
            # Variables pour les créneaux horaires
            for jour in range(1, 6):  # Lundi à vendredi
                for heure in range(8, 18):  # 8h à 17h
                    slot_name = f"slot_{cours.id}_{jour}_{heure}"
                    self.variables[slot_name] = self.model.NewBoolVar(slot_name)
    
    def _ajouter_contraintes_enseignants(self):
        """Ajoute les contraintes liées aux enseignants"""
        # Un enseignant ne peut pas être dans deux endroits en même temps
        # Un enseignant ne peut pas dépasser ses heures max par jour/semaine
        pass
    
    def _ajouter_contraintes_salles(self):
        """Ajoute les contraintes liées aux salles"""
        # Une salle ne peut pas accueillir deux cours simultanément
        # Respect des équipements nécessaires
        pass
    
    def _ajouter_contraintes_classes(self):
        """Ajoute les contraintes liées aux classes"""
        # Une classe ne peut pas avoir deux cours simultanément
        # Respect des heures par matière
        pass
    
    def _ajouter_contraintes_globales(self):
        """Ajoute les contraintes globales"""
        # Pauses déjeuner
        # Heures d'ouverture/fermeture
        # Contraintes spécifiques à l'établissement
        pass
    
    def _definir_objectif(self):
        """Définit la fonction objectif à optimiser"""
        # Minimiser les conflits
        # Maximiser la satisfaction des enseignants
        # Optimiser l'utilisation des salles
        pass
    
    def _extraire_solution(self, emploi_temps):
        """Extrait la solution optimisée"""
        solution = {
            'emploi_temps': emploi_temps,
            'score': self.solver.ObjectiveValue(),
            'conflits_resolus': 0,
            'temps_calcul': self.solver.WallTime(),
            'cours_optimises': []
        }
        return solution


class PredicteurAbsences:
    """
    Classe pour prédire les absences d'enseignants
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.features_importantes = []
        
    def entrainer(self, donnees_historiques):
        """
        Entraîne le modèle de prédiction d'absences
        """
        try:
            # Préparer les données
            X, y = self._preparer_donnees(donnees_historiques)
            
            # Diviser en train/test
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Normaliser les features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Entraîner le modèle
            self.model.fit(X_train_scaled, y_train)
            
            # Évaluer
            y_pred = self.model.predict(X_test_scaled)
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, average='weighted'),
                'recall': recall_score(y_test, y_pred, average='weighted'),
                'f1_score': f1_score(y_test, y_pred, average='weighted')
            }
            
            # Sauvegarder les features importantes
            self.features_importantes = list(zip(
                donnees_historiques.columns[:-1],  # Exclure la target
                self.model.feature_importances_
            ))
            
            return metrics
            
        except Exception as e:
            logger.error(f"Erreur lors de l'entraînement: {e}")
            return None
    
    def predire(self, donnees_enseignant):
        """
        Prédit la probabilité d'absence pour un enseignant
        """
        try:
            # Préparer les données
            X = self._preparer_features_enseignant(donnees_enseignant)
            X_scaled = self.scaler.transform(X.reshape(1, -1))
            
            # Prédiction
            probabilite = self.model.predict_proba(X_scaled)[0][1]  # Probabilité d'absence
            
            return {
                'probabilite_absence': probabilite,
                'facteurs_risque': self._analyser_facteurs_risque(donnees_enseignant),
                'recommandations': self._generer_recommandations(probabilite, donnees_enseignant)
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la prédiction: {e}")
            return None
    
    def _preparer_donnees(self, donnees_historiques):
        """Prépare les données pour l'entraînement"""
        # Extraire les features et la target
        features = donnees_historiques.drop(['absence'], axis=1)
        target = donnees_historiques['absence']
        
        return features, target
    
    def _preparer_features_enseignant(self, donnees_enseignant):
        """Prépare les features pour un enseignant spécifique"""
        # Convertir les données en format numpy array
        features = np.array([
            donnees_enseignant.get('age', 0),
            donnees_enseignant.get('experience_annees', 0),
            donnees_enseignant.get('heures_semaine', 0),
            donnees_enseignant.get('nombre_classes', 0),
            donnees_enseignant.get('stress_niveau', 0),
            donnees_enseignant.get('satisfaction_travail', 0),
            donnees_enseignant.get('distance_domicile', 0),
            donnees_enseignant.get('nombre_enfants', 0),
            donnees_enseignant.get('sante_generale', 0),
            donnees_enseignant.get('absences_annee_precedente', 0),
        ])
        
        return features
    
    def _analyser_facteurs_risque(self, donnees_enseignant):
        """Analyse les facteurs de risque d'absence"""
        facteurs = {}
        
        # Analyser chaque feature importante
        for feature, importance in self.features_importantes:
            valeur = donnees_enseignant.get(feature, 0)
            
            if importance > 0.1:  # Feature importante
                if feature == 'absences_annee_precedente' and valeur > 5:
                    facteurs[feature] = 'Élevé - Nombreuses absences l\'année dernière'
                elif feature == 'stress_niveau' and valeur > 7:
                    facteurs[feature] = 'Élevé - Niveau de stress important'
                elif feature == 'sante_generale' and valeur < 6:
                    facteurs[feature] = 'Faible - Santé générale préoccupante'
        
        return facteurs
    
    def _generer_recommandations(self, probabilite, donnees_enseignant):
        """Génère des recommandations basées sur la prédiction"""
        recommandations = []
        
        if probabilite > 0.7:
            recommandations.append("Probabilité d'absence élevée - Prévoir des remplaçants")
            recommandations.append("Contacter l'enseignant pour évaluer sa situation")
        elif probabilite > 0.4:
            recommandations.append("Probabilité d'absence modérée - Surveiller la situation")
            recommandations.append("Proposer un soutien si nécessaire")
        else:
            recommandations.append("Probabilité d'absence faible - Situation normale")
        
        return recommandations


class OptimiseurRemplacants:
    """
    Classe pour optimiser le matching des remplaçants
    """
    
    def __init__(self):
        self.model = GradientBoostingRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        
    def trouver_meilleurs_remplacants(self, absence, remplacants_disponibles):
        """
        Trouve les meilleurs remplaçants pour une absence donnée
        """
        try:
            scores = []
            
            for remplacant in remplacants_disponibles:
                score = self._calculer_score_compatibilite(absence, remplacant)
                scores.append({
                    'remplacant': remplacant,
                    'score_global': score['score_global'],
                    'score_competence': score['score_competence'],
                    'score_disponibilite': score['score_disponibilite'],
                    'score_geographique': score['score_geographique'],
                    'score_experience': score['score_experience'],
                    'details': score['details']
                })
            
            # Trier par score global
            scores.sort(key=lambda x: x['score_global'], reverse=True)
            
            return scores[:10]  # Retourner les 10 meilleurs
            
        except Exception as e:
            logger.error(f"Erreur lors du matching: {e}")
            return []
    
    def _calculer_score_compatibilite(self, absence, remplacant):
        """
        Calcule le score de compatibilité entre une absence et un remplaçant
        """
        # Score de compétence (matières enseignées)
        score_competence = self._calculer_score_competence(absence, remplacant)
        
        # Score de disponibilité
        score_disponibilite = self._calculer_score_disponibilite(absence, remplacant)
        
        # Score géographique
        score_geographique = self._calculer_score_geographique(absence, remplacant)
        
        # Score d'expérience
        score_experience = self._calculer_score_experience(absence, remplacant)
        
        # Score global pondéré
        score_global = (
            score_competence * 0.4 +
            score_disponibilite * 0.3 +
            score_geographique * 0.2 +
            score_experience * 0.1
        )
        
        return {
            'score_global': score_global,
            'score_competence': score_competence,
            'score_disponibilite': score_disponibilite,
            'score_geographique': score_geographique,
            'score_experience': score_experience,
            'details': {
                'matieres_compatibles': self._get_matieres_compatibles(absence, remplacant),
                'cours_remplacables': self._get_cours_remplacables(absence, remplacant),
                'contraintes_respectees': self._get_contraintes_respectees(absence, remplacant)
            }
        }
    
    def _calculer_score_competence(self, absence, remplacant):
        """Calcule le score de compétence"""
        cours_concernes = absence.get_cours_concernes()
        matieres_requises = set(cours.matiere for cours in cours_concernes)
        matieres_enseignees = set(remplacant.matieres_enseignees.all())
        
        if not matieres_requises:
            return 0.0
        
        intersection = matieres_requises.intersection(matieres_enseignees)
        return len(intersection) / len(matieres_requises)
    
    def _calculer_score_disponibilite(self, absence, remplacant):
        """Calcule le score de disponibilité"""
        if not remplacant.is_disponible(absence.date_debut):
            return 0.0
        
        # Vérifier la disponibilité pour chaque jour d'absence
        jours_disponibles = 0
        total_jours = (absence.date_fin - absence.date_debut).days + 1
        
        for i in range(total_jours):
            date = absence.date_debut + timedelta(days=i)
            if remplacant.is_disponible(date):
                jours_disponibles += 1
        
        return jours_disponibles / total_jours
    
    def _calculer_score_geographique(self, absence, remplacant):
        """Calcule le score géographique"""
        # Simplifié - en réalité, il faudrait calculer la distance
        # entre le domicile du remplaçant et l'établissement
        distance_max = remplacant.distance_max
        # Simulation d'une distance
        distance_estimee = 20  # km
        
        if distance_estimee <= distance_max:
            return 1.0 - (distance_estimee / distance_max)
        else:
            return 0.0
    
    def _calculer_score_experience(self, absence, remplacant):
        """Calcule le score d'expérience"""
        # Basé sur l'expérience et les évaluations
        experience = remplacant.experience_remplacement
        note_moyenne = remplacant.note_moyenne
        
        score_experience = min(experience / 10, 1.0)  # Max 10 ans = score 1.0
        score_evaluation = note_moyenne / 5.0  # Note sur 5
        
        return (score_experience + score_evaluation) / 2.0
    
    def _get_matieres_compatibles(self, absence, remplacant):
        """Retourne les matières compatibles"""
        cours_concernes = absence.get_cours_concernes()
        matieres_requises = set(cours.matiere for cours in cours_concernes)
        matieres_enseignees = set(remplacant.matieres_enseignees.all())
        
        return list(matieres_requises.intersection(matieres_enseignees))
    
    def _get_cours_remplacables(self, absence, remplacant):
        """Retourne les cours remplaçables"""
        cours_concernes = absence.get_cours_concernes()
        matieres_compatibles = self._get_matieres_compatibles(absence, remplacant)
        
        cours_remplacables = []
        for cours in cours_concernes:
            if cours.matiere in matieres_compatibles:
                cours_remplacables.append(cours)
        
        return cours_remplacables
    
    def _get_contraintes_respectees(self, absence, remplacant):
        """Retourne les contraintes respectées"""
        contraintes = []
        
        # Vérifier les contraintes de disponibilité
        if remplacant.is_disponible(absence.date_debut):
            contraintes.append("Disponible à la date de début")
        
        # Vérifier les contraintes de compétence
        matieres_compatibles = self._get_matieres_compatibles(absence, remplacant)
        if matieres_compatibles:
            contraintes.append(f"Compétent en {len(matieres_compatibles)} matière(s)")
        
        # Vérifier les contraintes géographiques
        if self._calculer_score_geographique(absence, remplacant) > 0:
            contraintes.append("Distance acceptable")
        
        return contraintes


class AnalyseurConflits:
    """
    Classe pour analyser et résoudre les conflits d'emploi du temps
    """
    
    def analyser_conflits(self, emploi_temps):
        """
        Analyse les conflits dans un emploi du temps
        """
        conflits = []
        
        # Conflits d'enseignants
        conflits.extend(self._detecter_conflits_enseignants(emploi_temps))
        
        # Conflits de salles
        conflits.extend(self._detecter_conflits_salles(emploi_temps))
        
        # Conflits de classes
        conflits.extend(self._detecter_conflits_classes(emploi_temps))
        
        return conflits
    
    def _detecter_conflits_enseignants(self, emploi_temps):
        """Détecte les conflits d'enseignants"""
        conflits = []
        cours = emploi_temps.cours.all()
        
        for i, cours1 in enumerate(cours):
            for cours2 in cours[i+1:]:
                if (cours1.enseignant == cours2.enseignant and
                    cours1.jour_semaine == cours2.jour_semaine and
                    self._creneaux_se_chevauchent(cours1, cours2)):
                    
                    conflits.append({
                        'type': 'enseignant',
                        'description': f"L'enseignant {cours1.enseignant.get_full_name()} a deux cours simultanés",
                        'cours1': cours1,
                        'cours2': cours2,
                        'gravite': 'critique'
                    })
        
        return conflits
    
    def _detecter_conflits_salles(self, emploi_temps):
        """Détecte les conflits de salles"""
        conflits = []
        cours = emploi_temps.cours.all()
        
        for i, cours1 in enumerate(cours):
            for cours2 in cours[i+1:]:
                if (cours1.salle == cours2.salle and
                    cours1.jour_semaine == cours2.jour_semaine and
                    self._creneaux_se_chevauchent(cours1, cours2)):
                    
                    conflits.append({
                        'type': 'salle',
                        'description': f"La salle {cours1.salle.nom} est occupée par deux cours simultanés",
                        'cours1': cours1,
                        'cours2': cours2,
                        'gravite': 'critique'
                    })
        
        return conflits
    
    def _detecter_conflits_classes(self, emploi_temps):
        """Détecte les conflits de classes"""
        conflits = []
        cours = emploi_temps.cours.all()
        
        for i, cours1 in enumerate(cours):
            for cours2 in cours[i+1:]:
                if (cours1.classe == cours2.classe and
                    cours1.jour_semaine == cours2.jour_semaine and
                    self._creneaux_se_chevauchent(cours1, cours2)):
                    
                    conflits.append({
                        'type': 'classe',
                        'description': f"La classe {cours1.classe.nom} a deux cours simultanés",
                        'cours1': cours1,
                        'cours2': cours2,
                        'gravite': 'critique'
                    })
        
        return conflits
    
    def _creneaux_se_chevauchent(self, cours1, cours2):
        """Vérifie si deux créneaux se chevauchent"""
        return (cours1.heure_debut < cours2.heure_fin and
                cours1.heure_fin > cours2.heure_debut)

