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
    <div style="background:#0d1b2e;padding:40px 20px;font-family:Arial,sans-serif;">
      <div style="max-width:560px;margin:0 auto;background:#112240;border-radius:16px;overflow:hidden;border:1px solid #1e3a5f;">
        <div style="background:#0d1b2e;padding:24px 32px;border-bottom:2px solid #f4c430;">
          <p style="margin:0;font-size:11px;letter-spacing:3px;color:#f4c430;text-transform:uppercase;">Spirit Server</p>
          <h1 style="margin:6px 0 0;font-size:22px;color:#ffffff;font-weight:700;">Новая заявка</h1>
        </div>
        <div style="padding:28px 32px;">
          <table style="width:100%;border-collapse:collapse;margin-bottom:24px;">
            <tr>
              <td style="padding:10px 0;border-bottom:1px solid #1e3a5f;color:#7a9cc4;font-size:13px;width:110px;">Никнейм</td>
              <td style="padding:10px 0;border-bottom:1px solid #1e3a5f;color:#ffffff;font-weight:700;font-size:15px;">{nickname}</td>
            </tr>
            <tr>
              <td style="padding:10px 0;border-bottom:1px solid #1e3a5f;color:#7a9cc4;font-size:13px;">Email</td>
              <td style="padding:10px 0;border-bottom:1px solid #1e3a5f;color:#a8c4e0;font-size:14px;">{email}</td>
            </tr>
            <tr>
              <td style="padding:10px 0;color:#7a9cc4;font-size:13px;">ID заявки</td>
              <td style="padding:10px 0;color:#4a6d8c;font-size:13px;">#{app_id}</td>
            </tr>
          </table>
          <p style="color:#7a9cc4;font-size:13px;margin:0 0 20px;">Нажми кнопку — игрок сразу получит письмо с ответом.</p>
          <table style="width:100%;border-collapse:collapse;">
            <tr>
              <td style="width:50%;padding-right:6px;">
                <a href="{accept_url}" style="display:block;text-align:center;background:#f4c430;color:#0d1b2e;text-decoration:none;padding:14px;border-radius:10px;font-size:15px;font-weight:800;letter-spacing:0.5px;">
                  ✅ Принять
                </a>
              </td>
              <td style="width:50%;padding-left:6px;">
                <a href="{reject_url}" style="display:block;text-align:center;background:#1e3a5f;color:#a8c4e0;text-decoration:none;padding:14px;border-radius:10px;font-size:15px;font-weight:700;border:1px solid #2e5080;">
                  ❌ Отказать
                </a>
              </td>
            </tr>
          </table>
        </div>
        <div style="padding:16px 32px;border-top:1px solid #1e3a5f;text-align:center;">
          <p style="margin:0;color:#2e5080;font-size:11px;">Кнопки работают один раз · Spirit Server 2024</p>
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