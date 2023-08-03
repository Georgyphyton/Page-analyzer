from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import date
from dotenv import load_dotenv
import psycopg2
import requests
import os
from urllib.parse import urlparse
from page_analyzer.validat import valid
from psycopg2.extras import NamedTupleCursor

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY')
database = os.getenv('DATABASE_URL')


def connection():
    return psycopg2.connect(database)


@app.route('/')
def main_page():
    return render_template('head.html')


@app.post('/urls')
def post_urls():
    url = request.form.get('url')
    errors = valid(url)
    if errors:
        for error in errors.values():
            flash(error, 'error')
        return render_template('head.html', url_er=url), 422
    current_date = date.today()
    parsed_url = urlparse(url)
    valid_url = parsed_url.scheme + '://' + parsed_url.netloc
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE name=%s', (valid_url,))
            cur_url = curs.fetchone()
            if cur_url:
                flash('Страницы уже добавлена', 'error')
                return redirect(url_for('to_url', id=cur_url.id), code=302)
            curs.execute('INSERT INTO urls (name, created_at) VALUES (%s, %s)', (valid_url, current_date))
            curs.execute('SELECT * FROM urls WHERE name=%s', (valid_url,))
            cur_url = curs.fetchone()
            return redirect(url_for('to_url', id=cur_url.id))


@app.get('/urls/<id>')
def to_url(id):
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url_inf = curs.fetchone()
            curs.execute('SELECT * FROM url_checks WHERE url_id=%s', (id,))
            url_checks = curs.fetchall()
    if not url_inf:
        return 'net takogo url', 404
    return render_template('page.html', url=url_inf, url_checks=url_checks)


@app.get('/urls')
def to_urls():
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls')
            urls = curs.fetchall()
            curs.execute('SELECT DISTINCT ON (url_id) * FROM url_checks')
            url_checks = curs.fetchall()
    return render_template('pages.html', urls=urls, url_checks=url_checks)


@app.post('/urls/<id>/checks')
def post_check(id):
    current_date = date.today()
    with connection() as conn:
        with conn.cursor(cursor_factory=NamedTupleCursor) as curs:
            curs.execute('SELECT * FROM urls WHERE id=%s', (id,))
            url_inf = curs.fetchone()
            code = requests.get(url_inf.name)
            curs.execute('INSERT INTO url_checks (url_id, status_code, created_at) VALUES (%s, %s, %s)',
                         (id, code.status_code, current_date))
    return redirect(url_for('to_url', id=id))
