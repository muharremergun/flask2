from flask import Blueprint, render_template, request, flash, jsonify , redirect , url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from sqlalchemy.sql import func
from datetime import datetime, timedelta, date
from .models import User , Team ,UserTeam

views = Blueprint('views', __name__)

from flask import make_response

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    notes = Note.query.filter_by(user_id=current_user.id)  # Öntanımlı olarak tüm notları al

    if request.method == 'POST': 
        note = request.form.get('note')
        reminder_days = int(request.form.get('reminder_days', 0))  # Hatırlatma günlerini al
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            if reminder_days > 0:
                # Not için hatırlatma günlerini ayarla
                new_note.reminder_days = reminder_days
                update_reminder_date(new_note)
                db.session.commit()

    # Notları sıralama seçeneklerine göre al
    sort_option = request.args.get('sort_option', 'alphabetical')
    order = request.args.get('order', 'asc')

    if order == 'desc':
        if sort_option == 'alphabetical':
            notes = notes.order_by(func.lower(Note.data).desc())
        elif sort_option == 'creation_date':
            notes = notes.order_by(Note.id.asc())
        elif sort_option == 'favorites_first':
            notes = notes.order_by(Note.is_favorite.asc())
        elif sort_option == 'completes_first':
            notes = notes.order_by(Note.completed.asc())
        
    else:
        if sort_option == 'alphabetical':
            notes = notes.order_by(func.lower(Note.data))
        elif sort_option == 'creation_date':
            notes = notes.order_by(Note.id.desc())
        elif sort_option == 'favorites_first':
            notes = notes.order_by(Note.is_favorite.desc())
        elif sort_option == 'completes_first':
            notes = notes.order_by(Note.completed.desc())

    notes = notes.all()  # Notları liste olarak al

    now = datetime.now()  # Şu anki zamanı al

    response = make_response(render_template("home.html", user=current_user, notes=notes, now=now, sort_option=sort_option, order=order))
    response.set_cookie('sort_option', sort_option)
    response.set_cookie('order', order)
    
    return response



def update_reminder_date(note):
    if note.reminder_days > 0:
        note.reminder_date = note.date + timedelta(days=note.reminder_days)
    else:
        note.reminder_date = None

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/toggle-favorite', methods=['POST'])
def toggle_favorite():
    note_data = json.loads(request.data)
    note_id = note_data['noteId']
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            note.is_favorite = not note.is_favorite
            db.session.commit()

    return jsonify({})

@views.route('/set-reminder-days', methods=['POST'])
def set_reminder_days():
    note_text = request.form.get('note')
    reminder_days = request.form.get('reminder_days')
    if note_text.strip() and reminder_days is not None and reminder_days.isdigit() and int(reminder_days) > 0:
        existing_note = Note.query.filter_by(data=note_text, user_id=current_user.id).first()
        if existing_note:
            # Var olan notun hatırlatma günlerini güncelle
            existing_note.reminder_days = int(reminder_days)
            update_reminder_date(existing_note)
        else:
            # Yeni bir not oluştur ve hatırlatma günlerini ayarla
            new_note = Note(data=note_text, user_id=current_user.id, reminder_days=int(reminder_days))
            update_reminder_date(new_note)
            db.session.add(new_note)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
@views.route('/toggle-completed', methods=['POST'])
def toggle_complete():
    data = request.json
    note_id = data.get('noteId')
    is_completed = data.get('isCompleted')

    note = Note.query.get(note_id)
    if note:
        note.completed = bool(is_completed)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 404

@views.route('/account', methods=['GET'])
@login_required
def account():
    favorite_notes = Note.query.filter_by(user_id=current_user.id, is_favorite=True).all()
    return render_template('account.html', user=current_user, favorite_notes=favorite_notes)



@views.route('/all-accounts')
@login_required
def all_accounts():
    all_users = User.query.all()
    return render_template('all_accounts.html', user=current_user, all_users=all_users)

@views.route('/update_info', methods=['POST'])
@login_required
def update_info():
    data = request.get_json()
    info_text = data['info']
    note_id = data['noteId']
    
    # Kullanıcıya ait ilgili notu güncellemek için SQL sorgusu
    note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
    if note:
        note.info = info_text
        db.session.commit()
        return jsonify({'success': True, 'info': info_text})
    return jsonify({'success': False, 'message': 'Note not found'}), 404


import pandas as pd
from flask import send_file
import os
from flask_mail import Mail
from flask_mail import Message
from . import mail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import sendgrid
from sendgrid.helpers.mail import Mail

from flask import current_app

import sendgrid
from sendgrid.helpers.mail import Mail
from flask import current_app
import base64
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
def send_mail(to_list, title, content, file_path):
    sg = sendgrid.SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
    from_email = current_app.config['MAIL_DEFAULT_SENDER']
    to_emails = to_list
    subject = title
    content = content

    with open(file_path, 'rb') as f:
        data = f.read()
        encoded_file = base64.b64encode(data).decode()

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        plain_text_content=content
    )

    attached_file = Attachment(
        FileContent(encoded_file),
        FileName('notes.xlsx'),
        FileType('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
        Disposition('attachment')
    )
    message.attachment = attached_file

    try:
        response = sg.send(message)
        print("Status Code:", response.status_code)
        print("Body:", response.body)
        print("Headers:", response.headers)
    except Exception as e:
        print("An error occurred while sending email:", str(e))



@views.route('/download-notes', methods=['GET'])
@login_required
def download_notes():
    # Sıralama seçeneklerini ve sıralama düzenini cookie'den al
    sort_option = request.cookies.get('sort_option', 'alphabetical')
    order = request.cookies.get('order', 'asc')

    # Notları filtrele ve sıralama seçeneklerine göre sırala
    notes_query = Note.query.filter_by(user_id=current_user.id)
    
    if order == 'desc':
        if sort_option == 'alphabetical':
            notes_query = notes_query.order_by(func.lower(Note.data).desc())
        elif sort_option == 'creation_date':
            notes_query = notes_query.order_by(Note.id.asc())
        elif sort_option == 'favorites_first':
            notes_query = notes_query.order_by(Note.is_favorite.asc())
        elif sort_option == 'completes_first':
            notes_query = notes_query.order_by(Note.completed.asc())
    else:
        if sort_option == 'alphabetical':
            notes_query = notes_query.order_by(func.lower(Note.data))
        elif sort_option == 'creation_date':
            notes_query = notes_query.order_by(Note.id.desc())
        elif sort_option == 'favorites_first':
            notes_query = notes_query.order_by(Note.is_favorite.desc())
        elif sort_option == 'completes_first':
            notes_query = notes_query.order_by(Note.completed.desc())

    notes = notes_query.all()  # Notları liste olarak al

    # Verileri Excel dosyasına yazdır
    data = []
    for note in notes:
        data.append({
            "Data": note.data,
            "Completed": note.completed,
            "Reminder Days": note.reminder_days,
            "Reminder Date": note.reminder_date
        })

    df = pd.DataFrame(data)
    bugunun_tarihi = date.today().strftime('%Y-%m-%d')
    dosya_adi = f'flask_{bugunun_tarihi}.xlsx'
    file_path = os.path.join(os.getcwd(), dosya_adi)
    df.to_excel(file_path, index=False)

    send_mail(
        to_list=[current_user.email],
        title="Your Notes Excel File",
        content="Your notes have been successfully exported to an Excel file and downloaded.",
        file_path=file_path
    )

    return send_file(file_path, as_attachment=True)

# routes.py veya app.py
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Team



from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import Team


from website import db
from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from .models import User, Team, UserTeam

from website import db  # Burada SQLAlchemy'den gerekli nesneleri import edin
 # Kullanacağımız veritabanı modellerini import edin

@views.route('/teams', methods=['GET', 'POST'])
@login_required
def teams():
    team = None
    users_team1 = []
    users_team2 = []

    if request.method == 'POST':
        team_id = request.form.get('team_id')
        if team_id:
            team = Team.query.get_or_404(team_id)
    else:
        # Mevcut olan takımları ve kullanıcıları al
        team1 = Team.query.get(1)
        team2 = Team.query.get(2)

        users_team1 = team1.users if team1 else []
        users_team2 = team2.users if team2 else []

    return render_template('teams.html', teams=current_user.teams, team=team, users_team1=users_team1, users_team2=users_team2)

"""

# Flask uygulamanızın views.py dosyası

from flask import Blueprint, render_template, request, flash, jsonify , redirect , url_for
from flask_login import login_required, current_user
from .models import Note
from . import db
import json
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from .models import User

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    notes = Note.query.filter_by(user_id=current_user.id)  # Öntanımlı olarak tüm notları al

    if request.method == 'POST': 
        note = request.form.get('note')
        reminder_days = int(request.form.get('reminder_days', 0))  # Hatırlatma günlerini al
        if len(note) < 1:
            flash('Note is too short!', category='error') 
        else:
            new_note = Note(data=note, user_id=current_user.id)
            db.session.add(new_note)
            db.session.commit()
            flash('Note added!', category='success')
            if reminder_days > 0:
                # Not için hatırlatma günlerini ayarla
                new_note.reminder_days = reminder_days
                update_reminder_date(new_note)
                db.session.commit()

    # Notları sıralama seçeneklerine göre al
    sort_option = request.args.get('sort_option', 'alphabetical')
    order = request.args.get('order', 'asc')

    if order == 'desc':
        if sort_option == 'alphabetical':
            notes = notes.order_by(func.lower(Note.data).desc())
        elif sort_option == 'creation_date':
            notes = notes.order_by(Note.id.asc())
        elif sort_option == 'favorites_first':
            notes = notes.order_by(Note.is_favorite.asc())
        elif sort_option == 'completes_first':
            notes = notes.order_by(Note.completed.asc())
        
    else:
        if sort_option == 'alphabetical':
            notes = notes.order_by(func.lower(Note.data))
        elif sort_option == 'creation_date':
            notes = notes.order_by(Note.id.desc())
        elif sort_option == 'favorites_first':
            notes = notes.order_by(Note.is_favorite.desc())
        elif sort_option == 'completes_first':
            notes = notes.order_by(Note.completed.desc())

    notes = notes.all()  # Notları liste olarak al

    now = datetime.now()  # Şu anki zamanı al
    return render_template("home.html", user=current_user, notes=notes, now=now, sort_option=sort_option, order=order)

def update_reminder_date(note):
    if note.reminder_days > 0:
        note.reminder_date = note.date + timedelta(days=note.reminder_days)
    else:
        note.reminder_date = None

@views.route('/delete-note', methods=['POST'])
def delete_note():  
    note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    noteId = note['noteId']
    note = Note.query.get(noteId)
    if note:
        if note.user_id == current_user.id:
            db.session.delete(note)
            db.session.commit()

    return jsonify({})

@views.route('/toggle-favorite', methods=['POST'])
def toggle_favorite():
    note_data = json.loads(request.data)
    note_id = note_data['noteId']
    note = Note.query.get(note_id)
    if note:
        if note.user_id == current_user.id:
            note.is_favorite = not note.is_favorite
            db.session.commit()

    return jsonify({})

@views.route('/set-reminder-days', methods=['POST'])
def set_reminder_days():
    note_text = request.form.get('note')
    reminder_days = request.form.get('reminder_days')
    if note_text.strip() and reminder_days is not None and reminder_days.isdigit() and int(reminder_days) > 0:
        existing_note = Note.query.filter_by(data=note_text, user_id=current_user.id).first()
        if existing_note:
            # Var olan notun hatırlatma günlerini güncelle
            existing_note.reminder_days = int(reminder_days)
            update_reminder_date(existing_note)
        else:
            # Yeni bir not oluştur ve hatırlatma günlerini ayarla
            new_note = Note(data=note_text, user_id=current_user.id, reminder_days=int(reminder_days))
            update_reminder_date(new_note)
            db.session.add(new_note)
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})
    
@views.route('/toggle-completed', methods=['POST'])
def toggle_complete():
    data = request.json
    note_id = data.get('noteId')
    is_completed = data.get('isCompleted')

    note = Note.query.get(note_id)
    if note:
        note.completed = bool(is_completed)
        db.session.commit()
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False}), 404

@views.route('/account', methods=['GET'])
@login_required
def account():
    favorite_notes = Note.query.filter_by(user_id=current_user.id, is_favorite=True).all()
    return render_template('account.html', user=current_user, favorite_notes=favorite_notes)

# views.py

@views.route('/all-accounts')
@login_required
def all_accounts():
    all_users = User.query.all()
    return render_template('all_accounts.html', user=current_user, all_users=all_users)


"""