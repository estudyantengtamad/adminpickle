"""
Adds any missing columns to Supabase PostgreSQL tables.
"""
from backend.app import create_app
from backend.models.mock_db import sqla
from sqlalchemy import text

def add_missing_columns():
    app = create_app()
    with app.app_context():
        print("[*] Checking & adding missing columns to Supabase tables...")
        try:
            sqla.session.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS dupr_last_synced FLOAT;"))
            sqla.session.commit()
            print("[+] Added 'dupr_last_synced' column to 'users' table successfully!")
        except Exception as e:
            print(f"[!] Note: {e}")

if __name__ == '__main__':
    add_missing_columns()
