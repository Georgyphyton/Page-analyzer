from dotenv import load_dotenv
import psycopg2
import os


load_dotenv()
database = os.getenv('DATABASE_URL')
conn = psycopg2.connect(database)
valid_url = 'jyj'
with conn.cursor() as curs:
    curs.execute('SELECT * FROM urls WHERE name=%s', (valid_url,))
    all_users = curs.fetchone()
    print(all_users)
