import psycopg2
from config import DB_CONFIG

def connect_db():
    return psycopg2.connect(**DB_CONFIG)
