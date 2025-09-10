#!/bin/bash

# Script de lancement pour Edtia
# Usage: ./run.sh [port]

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="Edtia"
VENV_DIR="venv"
PORT=${1:-8000}

echo -e "${BLUE}🚀 Lancement de $PROJECT_NAME${NC}"
echo -e "${BLUE}================================${NC}"

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

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Création de l'environnement virtuel...${NC}"
    python3 -m venv $VENV_DIR
fi

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

# Créer un superutilisateur si nécessaire
echo -e "${YELLOW}👤 Vérification du superutilisateur...${NC}"
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('Aucun superutilisateur trouvé.')
    print('Pour créer un superutilisateur, exécutez: python manage.py createsuperuser')
else:
    print('Superutilisateur existant trouvé.')
"

# Vérifier si le port est disponible
if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Le port $PORT est déjà utilisé. Arrêt des processus...${NC}"
    pkill -f "python.*manage.py.*runserver.*$PORT" || true
    sleep 2
fi

# Lancer le serveur
echo -e "${GREEN}🌟 Lancement du serveur Django...${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}🌐 Site accessible sur: http://localhost:$PORT${NC}"
echo -e "${GREEN}🌐 Site accessible sur: http://127.0.0.1:$PORT${NC}"
echo -e "${GREEN}🔧 Admin Django: http://localhost:$PORT/admin/${NC}"
echo -e "${GREEN}📱 Démo Interactive: http://localhost:$PORT/demo-interactive/${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${YELLOW}💡 Appuyez sur Ctrl+C pour arrêter le serveur${NC}"
echo ""

# Lancer le serveur Django
python manage.py runserver $PORT
