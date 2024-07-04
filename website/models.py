from website import db
from flask_login import UserMixin
from sqlalchemy.sql import func
# user_teams tablosunun tanımlanması
user_teams = db.Table(
    'user_teams',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('team_id', db.Integer, db.ForeignKey('team.id'), primary_key=True)
)
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_favorite = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=func.now())
    reminder_days = db.Column(db.Integer, default=0)
    reminder_date = db.Column(db.DateTime, default=None)
    completed = db.Column(db.Boolean, default=False)  
    info = db.Column(db.String(1000))
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=True)

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user')
    favorites = db.relationship('Favorites', backref='user')
    teams = db.relationship('Team', secondary='user_teams', back_populates='users')

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    users = db.relationship('User', secondary='user_teams', back_populates='teams')

class UserTeam(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), primary_key=True)

"""
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

from . import db
from flask_login import UserMixin

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_favorite = db.Column(db.Boolean, default=False)
    date = db.Column(db.DateTime, default=func.now())
    reminder_days = db.Column(db.Integer, default=0)
    reminder_date = db.Column(db.DateTime, default=None)
    completed = db.Column(db.Boolean, default=False)  
    info = db.Column(db.String(1000))

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note', backref='user')
    favorites = db.relationship('Favorites', backref='user')
"""