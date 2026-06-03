"""Принять или отклонить заявку на сервер Spirit — отправляет письмо игроку"""
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2

ADMIN_EMAIL = "qwaisov@gmail.com"
SMTP_USER = "qwaisov@gmail.com"
CARD_NUMBER = "2200 2418 1268 4441"
AMOUNT = "100"

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
    """Решение по заявке: принять или отклонить, отправить письмо игроку"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    body = json.loads(event.get('body') or '{}')
    app_id = body.get('id')
    decision = body.get('decision')  # 'accept' or 'reject'

    if not app_id or decision not in ('accept', 'reject'):
        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Неверные параметры'})
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(
        "UPDATE spirit_applications SET status = %s WHERE id = %s RETURNING nickname, email",
        (decision, app_id)
    )
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if not row:
        return {'statusCode': 404, 'headers': CORS_HEADERS, 'body': json.dumps({'error': 'Заявка не найдена'})}

    nickname, email = row

    if decision == 'accept':
        subject = '✅ Твоя заявка на Spirit принята!'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f0f8ff; padding: 30px; border-radius: 12px;">
            <h2 style="color: #1a5276; border-bottom: 2px solid #f4c430; padding-bottom: 10px;">🎮 Добро пожаловать на Spirit!</h2>
            <p>Привет, <b>{nickname}</b>!</p>
            <p>Твоя заявка на вступление в наш приватный сервер <b>одобрена</b>. Остался последний шаг:</p>
            <div style="margin: 20px 0; padding: 20px; background: white; border-radius: 8px; border: 2px solid #f4c430;">
                <p style="margin: 0 0 10px; font-size: 18px; font-weight: bold; color: #1a5276;">💳 Оплата проходки</p>
                <p style="margin: 0 0 8px;">Переведи <b>{AMOUNT} рублей</b> на карту:</p>
                <p style="margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 2px; color: #c0392b;">{CARD_NUMBER}</p>
            </div>
            <p style="color: #555; font-size: 14px;">После оплаты ты получишь доступ к серверу. Версия: 1.21.1, карта 6000×6000.</p>
            <p style="color: #888; font-size: 12px;">Если возникнут вопросы — пиши в Telegram: @fqylov</p>
        </div>
        """
    else:
        subject = '❌ Заявка на Spirit отклонена'
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; background: #f0f8ff; padding: 30px; border-radius: 12px;">
            <h2 style="color: #1a5276; border-bottom: 2px solid #f4c430; padding-bottom: 10px;">🎮 Сервер Spirit</h2>
            <p>Привет, <b>{nickname}</b>!</p>
            <p>К сожалению, твоя заявка на вступление в сервер <b>не была одобрена</b>.</p>
            <div style="margin: 20px 0; padding: 15px; background: white; border-radius: 8px; border-left: 4px solid #e74c3c;">
                <p style="margin: 0; color: #555;">Не расстраивайся — ты можешь попробовать снова. Следи за обновлениями в наших социальных сетях.</p>
            </div>
            <p style="color: #888; font-size: 12px;">Telegram: @fqylov &nbsp;|&nbsp; Discord: discord.gg/J5fcGEEM</p>
        </div>
        """

    send_email(email, subject, html)

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'ok': True})
    }
