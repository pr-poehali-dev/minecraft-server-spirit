"""Получить список заявок на сервер Spirit для админ-панели"""
import json
import os
import psycopg2

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, X-User-Id, X-Auth-Token, X-Session-Id',
    'Access-Control-Max-Age': '86400',
}


def handler(event: dict, context) -> dict:
    """Список всех заявок для администратора"""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nickname, email, status, created_at FROM spirit_applications ORDER BY created_at DESC"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    apps = [
        {'id': r[0], 'nickname': r[1], 'email': r[2], 'status': r[3], 'created_at': str(r[4])}
        for r in rows
    ]

    return {
        'statusCode': 200,
        'headers': CORS_HEADERS,
        'body': json.dumps({'applications': apps})
    }
