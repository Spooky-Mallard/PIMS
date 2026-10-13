import os

import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def get_db_connection():
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        print("Successfully connected to Neon PostgreSQL!")
        conn.close()
