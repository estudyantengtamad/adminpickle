"""
Script to drop obsolete / previous tables from Supabase PostgreSQL database.
"""
from backend.app import create_app
from backend.models.mock_db import sqla
from sqlalchemy import text

def drop_tables():
    app = create_app()
    with app.app_context():
        print("[*] Connecting to database...")
        tables_to_drop = [
            "players",
            "users",
            "confirmed_bookings",
            "open_play_sessions",
            "session_participants",
            "player_ratings",
            "direct_bookings",
            "event_posts",
            "moderation_reports",
            "audit_logs",
            "platform_settings",
            "admin_users"
        ]
        for tbl in tables_to_drop:
            try:
                sqla.session.execute(text(f"DROP TABLE IF EXISTS {tbl} CASCADE;"))
                print(f"[-] Dropped table: {tbl}")
            except Exception as e:
                print(f"[!] Warning dropping {tbl}: {e}")
        
        sqla.session.commit()
        print("[+] All previous tables removed successfully!")

if __name__ == '__main__':
    drop_tables()
