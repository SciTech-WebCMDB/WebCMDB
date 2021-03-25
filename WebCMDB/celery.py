# https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

from __future__ import absolute_import
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebCMDB.settings')

from django.conf import settings
from celery import Celery

app = Celery('WebCMDB')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(settings.INSTALLED_APPS)

@app.task(bind=True)
def debug_task(self):
	print(f'Request: {self.request!r}')