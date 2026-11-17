"""One-click database setup.

    py setup_database.py        (Windows)
    python3 setup_database.py   (Mac / Linux)

Uses the settings in .env to:
  1. create the 'patient_records' database if it does not exist
  2. create the tables (database/schema.sql)
  3. optionally load the sample data (database/seed.sql)
"""
import os
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql

HERE = Path(__file__).resolve().parent


def load_env(path=HERE / ".env"):
    if not path.exists():
        print("WARNING: no .env file found - using default settings.")
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())


def settings(dbname):
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": os.getenv("DB_PORT", "5432"),
        "user": os.getenv("DB_USER", "postgres"),
        "password": os.getenv("DB_PASSWORD", ""),
        "dbname": dbname,
    }


def main():
    load_env()
    target = os.getenv("DB_NAME", "patient_records")

    # Step 1: connect to the default 'postgres' database and create ours.
    try:
        conn = psycopg2.connect(**settings("postgres"))
    except psycopg2.OperationalError as exc:
        print("\nCould not log in to PostgreSQL.")
        print("Check DB_PASSWORD in your .env file.\n")
        print("Details:", exc)
        return 1
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("SHOW port")
        port = cur.fetchone()[0]
        cur.execute("SELECT version()")
        version = cur.fetchone()[0].split(",")[0]
        print(f"Connected: {version} on port {port}")
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", [target])
        if cur.fetchone():
            print(f"Database '{target}' already exists.")
        else:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target)))
            print(f"Database '{target}' created.")
    conn.close()

    # Step 2: create the tables.
    conn = psycopg2.connect(**settings(target))
    with conn, conn.cursor() as cur:
        cur.execute((HERE / "database" / "schema.sql").read_text(encoding="utf-8"))
        print("Tables and views created.")

        # Step 3: sample data (only offered when the tables are empty).
        cur.execute("SELECT COUNT(*) FROM patients")
        if cur.fetchone()[0] == 0:
            answer = input("Load sample patients and doctors for a demo? (y/n): ")
            if answer.strip().lower().startswith("y"):
                cur.execute((HERE / "database" / "seed.sql").read_text(encoding="utf-8"))
                print("Sample data loaded.")
        else:
            print("Tables already contain data - sample data not loaded.")
    conn.close()

    print("\nAll done! Now run:  py main.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
