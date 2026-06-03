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
    <div style="background:#ddeeff;padding:40px 20px;font-family:Arial,sans-serif;">
      <div style="max-width:560px;margin:0 auto;background:#ffffff;border-radius:18px;overflow:hidden;border:1px solid #b8d8f0;box-shadow:0 4px 24px rgba(30,100,180,0.10);">
        <div style="background:linear-gradient(135deg,#c8e8ff 0%,#fff8dc 100%);padding:26px 32px;border-bottom:2px solid #f4c430;">
          <p style="margin:0;font-size:11px;letter-spacing:3px;color:#b07d00;text-transform:uppercase;">Spirit Server</p>
          <h1 style="margin:6px 0 0;font-size:23px;color:#1a4a7a;font-weight:800;">Новая заявка 🎮</h1>
        </div>
        <div style="padding:28px 32px;background:#f5faff;">
          <table style="width:100%;border-collapse:collapse;margin-bottom:24px;background:#ffffff;border-radius:12px;overflow:hidden;">
            <tr>
              <td style="padding:12px 16px;border-bottom:1px solid #ddeeff;color:#6a9cc4;font-size:13px;width:110px;">Никнейм</td>
              <td style="padding:12px 16px;border-bottom:1px solid #ddeeff;color:#1a4a7a;font-weight:700;font-size:16px;">{nickname}</td>
            </tr>
            <tr>
              <td style="padding:12px 16px;border-bottom:1px solid #ddeeff;color:#6a9cc4;font-size:13px;">Email</td>
              <td style="padding:12px 16px;border-bottom:1px solid #ddeeff;color:#2a6aa0;font-size:14px;">{email}</td>
            </tr>
            <tr>
              <td style="padding:12px 16px;color:#6a9cc4;font-size:13px;">ID заявки</td>
              <td style="padding:12px 16px;color:#9abcd4;font-size:13px;">#{app_id}</td>
            </tr>
          </table>
          <p style="color:#5a8aaa;font-size:13px;margin:0 0 20px;text-align:center;">Нажми кнопку — игрок сразу получит письмо с ответом</p>
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="width:50%;padding-right:8px;">
                <a href="{accept_url}" style="display:block;text-align:center;background:#f4c430;color:#1a3a00;text-decoration:none;padding:18px 20px;border-radius:14px;font-size:17px;font-weight:900;letter-spacing:0.5px;box-shadow:0 4px 12px rgba(244,196,48,0.45);border-bottom:4px solid #c9a000;">
                  ✅&nbsp; Принять
                </a>
              </td>
              <td style="width:50%;padding-left:8px;">
                <a href="{reject_url}" style="display:block;text-align:center;background:#e8f4ff;color:#1a4a7a;text-decoration:none;padding:18px 20px;border-radius:14px;font-size:17px;font-weight:800;border:2px solid #b0d0f0;border-bottom:4px solid #8ab8e8;box-shadow:0 4px 12px rgba(30,100,180,0.12);">
                  ❌&nbsp; Отказать
                </a>
              </td>
            </tr>
          </table>
        </div>
        <div style="padding:14px 32px;border-top:1px solid #ddeeff;text-align:center;background:#edf6ff;">
          <p style="margin:0;color:#9abcd4;font-size:11px;">Кнопки работают один раз · Spirit Server 2024</p>
        </div>
      </div>
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