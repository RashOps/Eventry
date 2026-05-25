import psycopg2
from config import settings
from contextlib import contextmanager

@contextmanager
def get_db_sql():
    """
    Context manager pour gérer proprement le cycle de vie 
    de la connexion et du cursor PostgreSQL.
    """
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=settings.sql_database,
            user=settings.sql_user,
            password=settings.sql_password, 
            host=settings.sql_host,
            port=settings.sql_port
        )
        cur = conn.cursor()
        yield cur
        conn.commit()  # Commit automatique si aucune exception n'est levée
    except Exception as e:
        if conn:
            conn.rollback()  # Rollback en cas d'erreur
        print(f"[Error] Database operation failed: {e}")
        raise
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

if __name__ == "__main__": 
    # Utilisation propre du context manager
    with get_db_sql() as cur:
        cur.execute("SELECT * FROM tags;")
        records = cur.fetchall()
        print(f"Données récupérées : {records}")