# create_data.py

from website import create_app, db
from website.models import User, Team
app = create_app
with app.app_context():
    db.create_all()

    # Takım ekleme
    team1 = Team(name='Team A')
    team2 = Team(name='Team B')

    db.session.add(team1)
    db.session.add(team2)
    db.session.commit()

    # Kullanıcı ekleme ve takımlara atama
    user1 = User(email='m_ergun_61@hotmail.com', password='pbkdf2:sha256:600000$hh6mwb42fWtvqE0G$f44b4bab150636ac07c1e020edd2c66bb851c2fe023f4e5f9887503c1db3c449', first_name='muharrem')
    user2 = User(email='muharrem.ergunn@gmail.com', password='pbkdf2:sha256:600000$d8h8XLOHmVqi3FOw$3ca738de2d78c9e10e359d1ee0fa3fa4bd937bd5983c6bed6b7f6ce6fb481823', first_name='muharremanahesap')
    user3 = User(email='aaa@gmail.com', password='pbkdf2:sha256:600000$twV30t9bj7F5qsT0$d197c3d22616b87beeecf4f467f9eba7b59b139311914877b81cabc446d48cc8', first_name='aaa')
    user4 = User(email='qqq@gmail.com', password='pbkdf2:sha256:600000$YTvGJkdAkbo7MXAD$a16e73612db9cb89afee953858d9817891f5dae8adda278a9fc246ee07f77648', first_name='qqq')

    user1.teams.append(team1)
    user2.teams.append(team1)
    user3.teams.append(team2)
    user4.teams.append(team2)

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(user3)
    db.session.add(user4)
    db.session.commit()
