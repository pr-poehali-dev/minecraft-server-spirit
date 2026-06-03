"""Принять заявку на сервер Spirit — сохраняет заявку и отправляет уведомление администратору"""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2

ADMIN_EMAIL = "qwaisov@gmail.com"
SMTP_USER = "qwaisov@gmail.com"
ACTION_URL = "https://functions.poehali.dev/a8960d99-255e-408a-bd67-406283acc96b"

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

    token = f"{app_id}_spirit2024"
    accept_url = f"{ACTION_URL}?id={app_id}&decision=accept&token={token}"
    reject_url = f"{ACTION_URL}?id={app_id}&decision=reject&token={token}"

    html = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f0f8ff;padding:30px;border-radius:12px;">
        <h2 style="color:#1a5276;border-bottom:2px solid #f4c430;padding-bottom:10px;">🎮 Новая заявка на сервер Spirit</h2>
        <table style="width:100%;border-collapse:collapse;margin-bottom:20px;">
            <tr><td style="padding:8px 0;color:#888;width:100px;">Никнейм</td><td style="padding:8px 0;font-weight:bold;color:#1a5276;">{nickname}</td></tr>
            <tr><td style="padding:8px 0;color:#888;">Email</td><td style="padding:8px 0;color:#1a5276;">{email}</td></tr>
            <tr><td style="padding:8px 0;color:#888;">ID заявки</td><td style="padding:8px 0;color:#888;">#{app_id}</td></tr>
        </table>
        <p style="color:#555;margin-bottom:20px;">Нажми одну из кнопок, чтобы принять решение. Игрок сразу получит письмо.</p>
        <table style="width:100%;border-collapse:collapse;">
            <tr>
                <td style="width:50%;padding-right:8px;">
                    <a href="{accept_url}" style="display:block;text-align:center;background:#27ae60;color:white;text-decoration:none;padding:14px 20px;border-radius:10px;font-size:16px;font-weight:bold;">
                        ✅ Принять
                    </a>
                </td>
                <td style="width:50%;padding-left:8px;">
                    <a href="{reject_url}" style="display:block;text-align:center;background:#e74c3c;color:white;text-decoration:none;padding:14px 20px;border-radius:10px;font-size:16px;font-weight:bold;">
                        ❌ Отказать
                    </a>
                </td>
            </tr>
        </table>
        <p style="color:#aaa;font-size:12px;margin-top:20px;text-align:center;">Кнопки работают один раз — повторное нажатие будет проигнорировано.</p>
    </div>
    """
    try:
        send_email(ADMIN_EMAIL, f'Новая заявка #{app_id} — {nickname}', html)
    except Exception:
        pass

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'ok': True, 'id': app_id})
    }