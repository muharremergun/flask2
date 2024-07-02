from flask import Flask
from config import Config
from celery import Celery

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],  # Güncellenmiş broker URL
        backend=app.config['CELERY_RESULT_BACKEND']  # Güncellenmiş backend URL
    )

    from celery.schedules import crontab
    # Güncellenmiş Celery ayarları
    celery.conf.update(
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        timezone=app.config['CELERY_TIMEZONE'],
        beat_schedule={
            'send-daily-emails': {
                'task': 'website.tasks.send_daily_emails',  # Görevin doğru şekilde tanımlandığından emin ol
                'schedule': crontab(minute='*/1'),  # Her dakika çalışacak şekilde ayarlandı
            },
        },
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)



import website.tasks  # Görevleri import et

"""
from celery import Celery
from config import Config
from . import create_app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)

from celery.schedules import crontab
from .tasks import send_daily_emails

celery.conf.beat_schedule = {
    'send-daily-emails': {
        'task': 'myapp.tasks.send_daily_emails',
        'schedule': crontab(minute='*/1'),  # Her dakika çalıştırmak için,
    },
}
celery.conf.timezone = 'UTC'  

"""