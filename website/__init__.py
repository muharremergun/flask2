from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config
from celery import Celery


db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    


    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur

    return app

def make_celery(app):
    # Güncellenmiş Celery ayarları
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    from celery.schedules import crontab
    # Celery yapılandırmasını güncelle
    celery.conf.update(
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        timezone=app.config['CELERY_TIMEZONE'],
        beat_schedule={
            'send-daily-emails': {
                'task': 'website.tasks.send_daily_emails',
                'schedule': crontab(minute='*/1'),  # Her dakika çalışacak şekilde ayarlandı
            },
        },
    )

    # Celery görevleri için Flask uygulama bağlamını sağlama
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)

# Celery beat schedule ve timezone yapılandırmasıasasa
celery.conf.timezone = 'UTC'
DB_NAME = "database.db"
def create_database():
    # Güncellenmiş veritabanı kontrolü
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')

"""
  


from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config
from celery import Celery
import logging

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()
# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# `tasks` modülünü içe aktar


# Celery'nin `send_daily_emails` görevini tanıyabilmesi için `tasks` modülünü içe aktar

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    mail.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    with app.app_context():
        db.create_all()  # Veritabanı tablolarını oluştur

    return app

def make_celery(app):
    # Güncellenmiş Celery ayarları
    celery = Celery(
        app.import_name,
        broker=app.config['CELERY_BROKER_URL'],
        backend=app.config['CELERY_RESULT_BACKEND']
    )
    from celery.schedules import crontab
    # Celery yapılandırmasını güncelle
    celery.conf.update(
        task_serializer=app.config['CELERY_TASK_SERIALIZER'],
        result_serializer=app.config['CELERY_RESULT_SERIALIZER'],
        timezone=app.config['CELERY_TIMEZONE'],
        beat_schedule={
            'send-daily-emails': {
                'task': 'app.tasks.send_daily_emails',
                'schedule': crontab(minute='*/1'),  # Her dakika çalışacak şekilde ayarlandı
            },
        },
    )

    # Celery görevleri için Flask uygulama bağlamını sağlama
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

app = create_app()
celery = make_celery(app)

# Celery beat schedule ve timezone yapılandırması
celery.conf.timezone = 'UTC'
DB_NAME = "database.db"
def create_database():
    # Güncellenmiş veritabanı kontrolü
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
        print('Created Database!')


from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config.from_object('config')  # 'config' dosyasını yükleyin

    db.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        create_database()  # Veritabanını oluşturun

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database():
    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database!')

"""