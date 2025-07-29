import psycopg2
from config import DATABASE_URL, DB_CONFIG
import os

def connect_db():
    """
    Connect to PostgreSQL database using environment variables.
    """
    try:
        # Try using DATABASE_URL first (recommended for production)
        if DATABASE_URL:
            conn = psycopg2.connect(DATABASE_URL)
        else:
            # Fallback to individual components
            conn = psycopg2.connect(**DB_CONFIG)
        
        return conn
    
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def test_connection():
    """
    Test database connection.
    """
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"Connected to: {version[0]}")
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()
