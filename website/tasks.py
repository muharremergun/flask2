from .celery import celery, app
from .celery import celery
from .models import Note, User
from datetime import date
import pandas as pd
import os
from flask import current_app
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail as SendGridMail, Attachment, FileContent, FileName, FileType, Disposition
import logging

# Logging yapılandırması
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_mail(to_list, title, content, file_path):
    sg = SendGridAPIClient(api_key=current_app.config['SENDGRID_API_KEY'])
    from_email = current_app.config['MAIL_DEFAULT_SENDER']
    to_emails = to_list
    subject = title
    content = content

    with open(file_path, 'rb') as f:
        data = f.read()
        encoded_file = base64.b64encode(data).decode()

    message = SendGridMail(
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
        logger.info("E-posta başarıyla gönderildi! Status Code: %s", response.status_code)
        print("E-posta başarıyla gönderildi! Status Code:", response.status_code)
    except Exception as e:
        logger.error("E-posta gönderilirken bir hata oluştu: %s", str(e))
        print("E-posta gönderilirken bir hata oluştu:", str(e))
from website.celery import celery
@celery.task
def send_daily_emails():
    logging.info('send_daily_emails görevi çalıştırıldı.')
    with app.app_context():
        users = User.query.all()
        for user in users:
            notes = Note.query.filter_by(user_id=user.id).all()
            data = []
            for note in notes:
                data.append({
                    "Data": note.data,
                    "Completed": note.completed,
                    "Reminder Days": note.reminder_days,
                    "Reminder Date": note.reminder_date
                })

            if data:
                df = pd.DataFrame(data)
                bugunun_tarihi = date.today().strftime('%Y-%m-%d')
                dosya_adi = f'flask_{bugunun_tarihi}.xlsx'
                file_path = os.path.join(os.getcwd(), dosya_adi)
                df.to_excel(file_path, index=False)

                send_mail(
                    to_list=[user.email],
                    title="Your Notes Excel File",
                    content="Your notes have been successfully exported to an Excel file and downloaded.",
                    file_path=file_path
                )
                logger.info("Kullanıcı %s için e-posta gönderildi.", user.email)
                print(f"Kullanıcı {user.email} için e-posta gönderildi.")
