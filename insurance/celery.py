import os
from celery import Celery
from celery.schedules import crontab
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'insurance.settings')
celery_app = Celery('insurance')
celery_app.config_from_object('django.conf:settings', namespace='CELERY')
celery_app.autodiscover_tasks()

@celery_app.task
def show(arg):
    print(arg)

celery_app.conf.beat_schedule = {
    'task-name': {
        'task': 'insurance_app.tasks.adding_task',
        'schedule': 600.0,
    },
}
celery_app.conf.timezone = 'UTC'