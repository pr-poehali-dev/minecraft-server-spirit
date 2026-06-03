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
        <div style="background:#0d1b2e;padding:40px 20px;font-family:Arial,sans-serif;">
          <div style="max-width:560px;margin:0 auto;background:#112240;border-radius:16px;overflow:hidden;border:1px solid #1e3a5f;">
            <div style="background:#0d1b2e;padding:24px 32px;border-bottom:2px solid #f4c430;">
              <p style="margin:0;font-size:11px;letter-spacing:3px;color:#f4c430;text-transform:uppercase;">Spirit Server</p>
              <h1 style="margin:6px 0 0;font-size:22px;color:#ffffff;font-weight:700;">Заявка одобрена!</h1>
            </div>
            <div style="padding:28px 32px;">
              <p style="color:#a8c4e0;font-size:15px;margin:0 0 8px;">Привет, <span style="color:#ffffff;font-weight:700;">{nickname}</span>!</p>
              <p style="color:#7a9cc4;font-size:14px;margin:0 0 24px;">Твоя заявка принята. Остался один шаг — оплата проходки.</p>
              <div style="background:#0d1b2e;border:1px solid #f4c430;border-radius:12px;padding:20px 24px;margin-bottom:24px;">
                <p style="margin:0 0 6px;font-size:12px;letter-spacing:2px;color:#f4c430;text-transform:uppercase;">Перевод</p>
                <p style="margin:0 0 12px;color:#7a9cc4;font-size:14px;">Переведи <span style="color:#ffffff;font-weight:700;">{AMOUNT} рублей</span> на карту:</p>
                <p style="margin:0;font-size:26px;font-weight:800;letter-spacing:4px;color:#f4c430;">{CARD_NUMBER}</p>
              </div>
              <p style="color:#4a6d8c;font-size:13px;margin:0;">После оплаты ты получишь доступ к серверу. Версия 1.21.1 · Карта 6000×6000</p>
            </div>
            <div style="padding:16px 32px;border-top:1px solid #1e3a5f;text-align:center;">
              <p style="margin:0;color:#2e5080;font-size:11px;">Вопросы: @mXRlBLhQh · Discord: discord.gg/J5fcGEEM</p>
            </div>
          </div>
        </div>"""
        result_page = page(
            'Принято!', '✅', '#27ae60',
            f'Заявка #{app_id} принята',
            f'Игрок <b>{nickname}</b> получит письмо с реквизитами для оплаты на {email}.'
        )
    else:
        subject = '❌ Заявка на Spirit отклонена'
        player_html = f"""
        <div style="background:#0d1b2e;padding:40px 20px;font-family:Arial,sans-serif;">
          <div style="max-width:560px;margin:0 auto;background:#112240;border-radius:16px;overflow:hidden;border:1px solid #1e3a5f;">
            <div style="background:#0d1b2e;padding:24px 32px;border-bottom:2px solid #1e3a5f;">
              <p style="margin:0;font-size:11px;letter-spacing:3px;color:#f4c430;text-transform:uppercase;">Spirit Server</p>
              <h1 style="margin:6px 0 0;font-size:22px;color:#ffffff;font-weight:700;">Заявка отклонена</h1>
            </div>
            <div style="padding:28px 32px;">
              <p style="color:#a8c4e0;font-size:15px;margin:0 0 8px;">Привет, <span style="color:#ffffff;font-weight:700;">{nickname}</span>!</p>
              <p style="color:#7a9cc4;font-size:14px;margin:0 0 20px;">К сожалению, на этот раз твоя заявка не была одобрена.</p>
              <div style="background:#0d1b2e;border-left:3px solid #2e5080;border-radius:0 10px 10px 0;padding:16px 20px;">
                <p style="margin:0;color:#4a6d8c;font-size:14px;">Не расстраивайся — ты можешь попробовать снова в следующий раз. Следи за обновлениями в наших соц. сетях.</p>
              </div>
            </div>
            <div style="padding:16px 32px;border-top:1px solid #1e3a5f;text-align:center;">
              <p style="margin:0;color:#2e5080;font-size:11px;">Telegram: @mXRlBLhQh · Discord: discord.gg/J5fcGEEM</p>
            </div>
          </div>
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