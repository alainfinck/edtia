"""
Configuration WSGI pour Edtia.

Il expose l'appelable WSGI comme une variable de niveau module nommée ``application``.

Pour plus d'informations sur ce fichier, voir
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtia.settings')

application = get_wsgi_application()

