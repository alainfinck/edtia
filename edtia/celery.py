"""
Configuration Celery pour Edtia
"""
import os
from celery import Celery

# Configuration de l'environnement Django pour Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'edtia.settings')

app = Celery('edtia')

# Configuration Celery depuis les settings Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Découverte automatique des tâches dans toutes les apps Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

