"""Обработка решения по заявке по ссылке из письма — возвращает HTML-страницу"""
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import psycopg2

ADMIN_EMAIL = "qwaisov@gmail.com"
SMTP_USER = "qwaisov@gmail.com"
CARD_NUMBER = "2200 2418 1268 4441"
AMOUNT = "100"

HTML_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Content-Type': 'text/html; charset=utf-8',
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


def page(title: str, emoji: str, color: str, heading: str, message: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>{title}</title>
<style>
  body {{ margin:0; font-family: Arial, sans-serif; background: #eaf4fb; display: flex; align-items: center; justify-content: center; min-height: 100vh; }}
  .card {{ background: white; border-radius: 16px; padding: 48px 40px; max-width: 460px; width: 90%; text-align: center; box-shadow: 0 4px 32px rgba(26,82,118,0.10); }}
  .emoji {{ font-size: 56px; margin-bottom: 16px; }}
  h1 {{ color: {color}; font-size: 26px; margin: 0 0 12px; }}
  p {{ color: #555; font-size: 15px; line-height: 1.6; margin: 0; }}
  .back {{ display: inline-block; margin-top: 28px; padding: 12px 28px; background: #1a5276; color: white; border-radius: 10px; text-decoration: none; font-weight: bold; font-size: 14px; }}
</style>
</head>
<body>
<div class="card">
  <div class="emoji">{emoji}</div>
  <h1>{heading}</h1>
  <p>{message}</p>
  <a class="back" href="javascript:window.close()">Закрыть</a>
</div>
</body>
</html>"""


def handler(event: dict, context) -> dict:
    """Принять или отклонить заявку по GET-ссылке из письма администратора"""
    params = event.get('queryStringParameters') or {}
    app_id = params.get('id')
    decision = params.get('decision')
    token = params.get('token', '')

    # Простая защита — токен = id + секретный суффикс
    expected_token = f"{app_id}_spirit2024"
    if not app_id or decision not in ('accept', 'reject') or token != expected_token:
        return {
            'statusCode': 400,
            'headers': HTML_HEADERS,
            'body': page('Ошибка', '⚠️', '#e74c3c', 'Неверная ссылка', 'Ссылка недействительна или устарела.')
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(
        "SELECT status FROM spirit_applications WHERE id = %s",
        (app_id,)
    )
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        return {
            'statusCode': 404,
            'headers': HTML_HEADERS,
            'body': page('Ошибка', '🔍', '#e74c3c', 'Заявка не найдена', f'Заявка #{app_id} не существует.')
        }

    if row[0] != 'pending':
        cur.close()
        conn.close()
        status_label = 'принята' if row[0] == 'accept' else 'отклонена'
        return {
            'statusCode': 200,
            'headers': HTML_HEADERS,
            'body': page('Уже обработано', 'ℹ️', '#1a5276', 'Уже обработано', f'Эта заявка уже была {status_label} ранее.')
        }

    cur.execute(
        "UPDATE spirit_applications SET status = %s WHERE id = %s RETURNING nickname, email",
        (decision, app_id)
    )
    nickname, email = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if decision == 'accept':
        subject = '✅ Твоя заявка на Spirit принята!'
        player_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f0f8ff;padding:30px;border-radius:12px;">
            <h2 style="color:#1a5276;border-bottom:2px solid #f4c430;padding-bottom:10px;">🎮 Добро пожаловать на Spirit!</h2>
            <p>Привет, <b>{nickname}</b>!</p>
            <p>Твоя заявка на вступление в наш приватный сервер <b>одобрена</b>. Остался последний шаг:</p>
            <div style="margin:20px 0;padding:20px;background:white;border-radius:8px;border:2px solid #f4c430;">
                <p style="margin:0 0 10px;font-size:18px;font-weight:bold;color:#1a5276;">💳 Оплата проходки</p>
                <p style="margin:0 0 8px;">Переведи <b>{AMOUNT} рублей</b> на карту:</p>
                <p style="margin:0;font-size:24px;font-weight:bold;letter-spacing:3px;color:#c0392b;">{CARD_NUMBER}</p>
            </div>
            <p style="color:#555;font-size:14px;">После оплаты ты получишь доступ к серверу. Версия: 1.21.1, карта 6000×6000.</p>
            <p style="color:#888;font-size:12px;">Если возникнут вопросы — пиши в Telegram: @fqylov</p>
        </div>"""
        result_page = page(
            'Принято!', '✅', '#27ae60',
            f'Заявка #{app_id} принята',
            f'Игрок <b>{nickname}</b> получит письмо с реквизитами для оплаты на {email}.'
        )
    else:
        subject = '❌ Заявка на Spirit отклонена'
        player_html = f"""
        <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;background:#f0f8ff;padding:30px;border-radius:12px;">
            <h2 style="color:#1a5276;border-bottom:2px solid #f4c430;padding-bottom:10px;">🎮 Сервер Spirit</h2>
            <p>Привет, <b>{nickname}</b>!</p>
            <p>К сожалению, твоя заявка на вступление в сервер <b>не была одобрена</b>.</p>
            <div style="margin:20px 0;padding:15px;background:white;border-radius:8px;border-left:4px solid #e74c3c;">
                <p style="margin:0;color:#555;">Не расстраивайся — ты можешь попробовать снова в следующий раз. Следи за обновлениями в наших социальных сетях.</p>
            </div>
            <p style="color:#888;font-size:12px;">Telegram: @fqylov &nbsp;|&nbsp; Discord: discord.gg/J5fcGEEM</p>
        </div>"""
        result_page = page(
            'Отклонено', '❌', '#e74c3c',
            f'Заявка #{app_id} отклонена',
            f'Игрок <b>{nickname}</b> получит письмо об отказе на {email}.'
        )

    try:
        send_email(email, subject, player_html)
    except Exception:
        pass

    return {
        'statusCode': 200,
        'headers': HTML_HEADERS,
        'body': result_page
    }
