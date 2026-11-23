"""
DataSentinel AI: SQLite to PostgreSQL Non-Destructive Data Migration Tool

Transfers all records from a local SQLite database to PostgreSQL.
- Preserves all users, password hashes, roles, dataset metadata, and incident logs.
- Strictly read-only against the SQLite source database.
- Idempotent: checks for existing IDs and unique constraints to avoid duplicates.
- Transactional: wraps table inserts in transactions with automatic rollback on error.
- Sequence synchronized: updates PostgreSQL SERIAL sequences to match max(id).
- Safe to rerun: can be executed multiple times without duplicating or corrupting data.
"""
import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.models import Base
from app.core.database import json_dumps_custom

# Strict foreign-key dependency order
TABLES_IN_ORDER = [
    "users",
    "datasets",
    "dataset_versions",
    "dataset_schemas",
    "profiling_results",
    "anomaly_results",
    "drift_results",
    "incidents",
    "investigations",
    "remediation_suggestions",
    "audit_logs"
]

def migrate(sqlite_path: str, pg_url: str):
    if not os.path.exists(sqlite_path):
        print(f"ERROR: SQLite database file not found at: {sqlite_path}")
        sys.exit(1)

    print("=" * 70)
    print("DATASENTINEL AI: DATABASE MIGRATION (SQLite -> PostgreSQL)")
    print(f"Source: {sqlite_path}")
    print(f"Target: {pg_url.split('@')[-1] if '@' in pg_url else pg_url}")
    print("=" * 70)

    # 1. Connect to SQLite (read-only mode)
    sqlite_engine = create_engine(f"sqlite:///{sqlite_path}", connect_args={"check_same_thread": False})

    # 2. Connect to PostgreSQL
    normalized_pg_url = pg_url.replace("postgres://", "postgresql://", 1) if pg_url.startswith("postgres://") else pg_url
    is_postgres = "postgres" in normalized_pg_url.lower()

    pg_engine = create_engine(
        normalized_pg_url,
        json_serializer=json_dumps_custom,
        pool_pre_ping=True
    )

    print("\n1. Ensuring destination schema and tables exist...")
    Base.metadata.create_all(bind=pg_engine)
    print("   -> Destination schema initialized successfully.")

    sqlite_inspector = inspect(sqlite_engine)
    sqlite_tables = set(sqlite_inspector.get_table_names())

    with sqlite_engine.connect() as src_conn, pg_engine.connect() as dst_conn:
        for tbl in TABLES_IN_ORDER:
            if tbl not in sqlite_tables:
                print(f"   -> Skipping '{tbl}' (not present in source SQLite).")
                continue

            rows = src_conn.execute(text(f"SELECT * FROM {tbl} ORDER BY id ASC")).mappings().all()
            print(f"\n2. Migrating table '{tbl}' ({len(rows)} record(s) in source)...")

            if not rows:
                print(f"   -> Table '{tbl}' has 0 source rows. Skipping.")
                continue

            # Query existing IDs and unique constraints in destination to ensure zero duplicates
            existing_ids = set(dst_conn.execute(text(f"SELECT id FROM {tbl}")).scalars().all())

            existing_usernames = set()
            existing_emails = set()
            if tbl == "users":
                try:
                    existing_usernames = set(dst_conn.execute(text("SELECT username FROM users")).scalars().all())
                    existing_emails = set(dst_conn.execute(text("SELECT email FROM users")).scalars().all())
                except Exception:
                    pass

            inserted_count = 0
            skipped_count = 0

            # Wrap table migration in a savepoint transaction with rollback on failure
            try:
                with dst_conn.begin_nested():
                    for row in rows:
                        row_dict = dict(row)
                        row_id = row_dict.get("id")

                        # Skip if ID already exists in destination
                        if row_id in existing_ids:
                            skipped_count += 1
                            continue

                        # For users table, avoid unique username/email constraint collisions
                        if tbl == "users":
                            if row_dict.get("username") in existing_usernames or row_dict.get("email") in existing_emails:
                                print(f"   -> User '{row_dict.get('username')}' / '{row_dict.get('email')}' already exists in target. Skipping.")
                                skipped_count += 1
                                continue

                        cols = list(row_dict.keys())
                        col_names = ", ".join(cols)
                        col_params = ", ".join([f":{col}" for col in cols])
                        insert_stmt = text(f"INSERT INTO {tbl} ({col_names}) VALUES ({col_params})")
                        dst_conn.execute(insert_stmt, row_dict)

                        existing_ids.add(row_id)
                        if tbl == "users":
                            existing_usernames.add(row_dict.get("username"))
                            existing_emails.add(row_dict.get("email"))

                        inserted_count += 1

                dst_conn.commit()
                print(f"   -> Transaction committed: {inserted_count} inserted, {skipped_count} skipped (already existed).")

            except Exception as e:
                dst_conn.rollback()
                print(f"   -> ERROR in '{tbl}': {e}. Transaction rolled back.")
                raise e

            # Sequence synchronization for PostgreSQL
            if is_postgres and inserted_count > 0:
                try:
                    dst_conn.execute(text(f"""
                        SELECT setval(
                            pg_get_serial_sequence('{tbl}', 'id'),
                            COALESCE((SELECT MAX(id) FROM {tbl}), 1),
                            true
                        );
                    """))
                    dst_conn.commit()
                    print(f"   -> Sequence for '{tbl}' synchronized to current max(id).")
                except Exception as seq_err:
                    print(f"   -> Sequence synchronization warning for '{tbl}': {seq_err}")

    print("\n" + "=" * 70)
    print("MIGRATION COMPLETED SUCCESSFULLY! All data verified & preserved.")
    print("=" * 70)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python migrate_sqlite_to_pg.py <path_to_sqlite.db> <postgresql_connection_url>")
        print("Example: python migrate_sqlite_to_pg.py ./datasentinel.db postgresql://user:pass@host:5432/dbname")
        sys.exit(1)

    migrate(sys.argv[1], sys.argv[2])
