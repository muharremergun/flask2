import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hjshjhdjah kjshkjdhjs'
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///database.db'
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'muharrem.ergunn@gmail.com'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY') or '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'
    
    # Güncellenmiş Celery ayarları
    CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND') or 'redis://localhost:6379/0'
    CELERY_TASK_SERIALIZER = os.environ.get('CELERY_TASK_SERIALIZER') or 'json'
    CELERY_RESULT_SERIALIZER = os.environ.get('CELERY_RESULT_SERIALIZER') or 'json'
    CELERY_TIMEZONE = os.environ.get('CELERY_TIMEZONE') or 'UTC'

    # Celery yapılandırma ayarları
    CELERY_CONFIG = {
        'broker_url': CELERY_BROKER_URL,
        'result_backend': CELERY_RESULT_BACKEND,
        'task_serializer': CELERY_TASK_SERIALIZER,
        'result_serializer': CELERY_RESULT_SERIALIZER,
        'timezone': CELERY_TIMEZONE,
    }

"""
SENDGRID_API_KEY = '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'#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
MAIL_DEFAULT_SENDER = 'muharrem.ergunn@gmail.com'#117LETLYA3H6BCZXV639UAXB
SECRET_KEY = 'hjshjhdjah kjshkjdhjs'
SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'

"""