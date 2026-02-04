import os

from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aforro_backend.settings')
app = Celery('aforro_backend')#logical app identifier
app.config_from_object('django.conf:settings', namespace='CELERY')#read all the CLERY related settings
app.autodiscover_tasks()# auto disover the task.py file in the installed apps.
