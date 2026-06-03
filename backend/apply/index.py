"""Принять заявку на сервер Spirit — сохраняет заявку и отправляет уведомление администратору"""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2

ADMIN_EMAIL = "qwaisov@gmail.com"
SMTP_USER = "qwaisov@gmail.com"

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, X-Auth-Token, X-Session-Id',
    'Access-Control-Max-Age': '86400',
}


def send_email(to: str, subject: str, html: str):
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SMTP_USER
    msg['To'] = to
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(SMTP_USER, smtp_password)
        server.sendmail(SMTP_USER, to, msg.as_string())


def handler(event: dict, context) -> dict:
    """Принять заявку: сохранить в БД и уведомить администратора"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    body = json.loads(event.get('body') or '{}')
    nickname = body.get('nickname', '').strip()
    email = body.get('email', '').strip()

    if not nickname or not email:
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Заполните все поля'})
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO spirit_applications (nickname, email, status) VALUES (%s, %s, 'pending') RETURNING id",
        (nickname, email)
    )
    app_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f0f8ff; padding: 30px; border-radius: 12px;">
        <h2 style="color: #1a5276; border-bottom: 2px solid #f4c430; padding-bottom: 10px;">🎮 Новая заявка на сервер Spirit</h2>
        <p><b>Никнейм:</b> {nickname}</p>
        <p><b>Email:</b> {email}</p>
        <p><b>ID заявки:</b> #{app_id}</p>
        <div style="margin-top: 20px; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #1a5276;">
            <p style="margin: 0; color: #555;">Перейди в админ-панель сайта, чтобы принять или отклонить заявку.</p>
        </div>
    </div>
    """
    send_email(ADMIN_EMAIL, f'Новая заявка #{app_id} — {nickname}', html)

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'ok': True, 'id': app_id})
    }
