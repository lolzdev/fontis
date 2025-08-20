import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fontis.settings')

app = Celery('fontis')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
