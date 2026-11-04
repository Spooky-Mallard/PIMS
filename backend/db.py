"""Database Connection and Helper Utilities for PIMS
Sekarungi Pharmaceuticals Ltd
Connects to Neon PostgreSQL using psycopg2 with Pandas support and robust error handling.
"""

import os
import warnings
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
from dotenv import load_dotenv

# Filter pandas warning regarding raw DBAPI2 connection without SQLAlchemy
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

# Locate and load .env from DBMS-PROJECT/.env
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
env_path = os.path.join(project_root, ".env")
load_dotenv(env_path)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_db_connection():
    """Create and return a raw psycopg2 connection."""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not found in environment variables. Check .env file.")
    return psycopg2.connect(DATABASE_URL)


def test_connection():
    """Verify database connectivity and fetch metadata."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version(), current_database(), current_user;")
        row = cur.fetchone()
        cur.close()
        conn.close()
        return True, {
            "version": row[0].split()[0] + " " + row[0].split()[1],
            "database": row[1],
            "user": row[2]
        }
    except Exception as e:
        return False, {"error": str(e)}


def fetch_dataframe(sql, params=None):
    """Execute a query and return the result as a Pandas DataFrame."""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(sql, conn, params=params)
        return df
    finally:
        conn.close()


def execute_statement(sql, params=None, return_id_column=None):
    """
    Execute an INSERT, UPDATE, or DELETE statement inside a transaction.
    If return_id_column is provided, appends RETURNING <col> and returns the generated ID.
    Returns: (success: bool, message: str, returned_id: any)
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if return_id_column:
            sql_returning = f"{sql.rstrip(';')} RETURNING {return_id_column};"
            cur.execute(sql_returning, params)
            new_id = cur.fetchone()[0]
        else:
            cur.execute(sql, params)
            new_id = None
        conn.commit()
        cur.close()
        return True, "Operation successful", new_id
    except Exception as e:
        conn.rollback()
        return False, str(e), None
    finally:
        conn.close()


if __name__ == "__main__":
    ok, info = test_connection()
    if ok:
        print(f"Connected to Neon DB '{info['database']}' as user '{info['user']}' ({info['version']})")
    else:
        print(f"Connection failed: {info['error']}")
