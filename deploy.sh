#!/bin/bash

# Script de déploiement en production pour Edtia
# Usage: ./deploy.sh

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Edtia"
VENV_DIR=".venv"

echo -e "${BLUE}🚀 Déploiement en production de $PROJECT_NAME${NC}"
echo -e "${BLUE}===========================================${NC}"

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 n'est pas installé${NC}"
    exit 1
fi

# Vérifier si le fichier manage.py existe
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Fichier manage.py non trouvé. Êtes-vous dans le bon répertoire ?${NC}"
    exit 1
fi

# Sauvegarder la base de données
echo -e "${YELLOW}💾 Sauvegarde de la base de données...${NC}"
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Activer l'environnement virtuel
echo -e "${YELLOW}🐍 Activation de l'environnement virtuel...${NC}"
source $VENV_DIR/bin/activate

# Installer/mettre à jour les dépendances
echo -e "${YELLOW}📦 Installation des dépendances...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Créer le dossier logs s'il n'existe pas
if [ ! -d "logs" ]; then
    echo -e "${YELLOW}📁 Création du dossier logs...${NC}"
    mkdir -p logs
fi

# Appliquer les migrations
echo -e "${YELLOW}🔄 Application des migrations...${NC}"
python manage.py makemigrations
python manage.py migrate

# Collecter les fichiers statiques
echo -e "${YELLOW}📁 Collecte des fichiers statiques...${NC}"
python manage.py collectstatic --noinput

# Vérifier la configuration
echo -e "${YELLOW}🔍 Vérification de la configuration...${NC}"
python manage.py check --deploy

# Redémarrer les services (selon votre configuration)
echo -e "${YELLOW}🔄 Redémarrage des services...${NC}"
echo -e "${YELLOW}💡 Si vous utilisez systemd, exécutez: sudo systemctl restart edtia${NC}"
echo -e "${YELLOW}💡 Si vous utilisez Apache, exécutez: sudo systemctl restart apache2${NC}"

echo -e "${GREEN}✅ Déploiement terminé avec succès !${NC}"
echo -e "${GREEN}🌐 Votre site est maintenant en ligne${NC}"
