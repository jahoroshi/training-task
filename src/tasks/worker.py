import os

import smtplib
from celery_app import celery_app
from logger import logger
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv('SMTP_SERVER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_LOGIN = os.getenv('EMAIL_LOGIN')

@celery_app.task
def send_email_task(email, text):
    msg = EmailMessage()
    msg['Subject'] = 'Напоминание о задаче из Вашего To Do List.'
    msg['From'] = EMAIL_LOGIN
    msg['To'] = email
    msg.set_content(f'Напоминаем, что у вас запланирована задача {text}.')

    with smtplib.SMTP(SMTP_SERVER, 587) as server:
        server.starttls()
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        server.send_message(msg)


if __name__ == "__main__":
    send_email_task('jahoroshi4y@gmail.com', 'Test eman', 'fdfdsfsdfsdsd')