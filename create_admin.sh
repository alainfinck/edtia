#!/bin/bash

# Script pour créer un superutilisateur Django
# Usage: ./create_admin.sh

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}👤 Création d'un superutilisateur pour Edtia${NC}"
echo -e "${BLUE}===========================================${NC}"

# Vérifier si le fichier manage.py existe
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Fichier manage.py non trouvé. Êtes-vous dans le bon répertoire ?${NC}"
    exit 1
fi

# Activer l'environnement virtuel s'il existe
if [ -d "venv" ]; then
    echo -e "${YELLOW}🐍 Activation de l'environnement virtuel...${NC}"
    source venv/bin/activate
fi

# Créer le superutilisateur
echo -e "${YELLOW}👤 Création du superutilisateur...${NC}"
echo -e "${YELLOW}💡 Suivez les instructions pour créer votre compte administrateur${NC}"
echo ""

python manage.py createsuperuser

echo -e "${GREEN}✅ Superutilisateur créé avec succès !${NC}"
echo -e "${GREEN}🔧 Vous pouvez maintenant accéder à l'admin Django${NC}"
echo -e "${GREEN}🌐 URL: http://localhost:8000/admin/${NC}"
