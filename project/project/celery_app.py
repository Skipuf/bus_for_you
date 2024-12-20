import os

from celery.schedules import crontab

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


CELERY_BEAT_SCHEDULE = {
    'send_notification': {
        'task': 'notification.tasks.send_notification',
        'schedule': crontab(hour='10', minute='0'),
    },
    'send_booking_notifications': {
        'task': 'notification.tasks.send_booking_notifications',
        'schedule': crontab(minute='*/30'), # Каждые 30 минут
    },
}
