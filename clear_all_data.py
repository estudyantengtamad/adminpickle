"""
Script to wipe all sample/mock data from Supabase tables, leaving only the Admin staff account.
"""
from backend.app import create_app
from backend.models.mock_db import (
    sqla, User, ConfirmedBooking, OpenPlaySession,
    SessionParticipant, PlayerRating, EventPost, AuditLog, PlatformSetting
)

def clear_mock_data():
    app = create_app()
    with app.app_context():
        print("[*] Clearing all sample/mock data from database tables...")
        
        SessionParticipant.query.delete()
        PlayerRating.query.delete()
        OpenPlaySession.query.delete()
        ConfirmedBooking.query.delete()
        EventPost.query.delete()
        User.query.delete()
        AuditLog.query.delete()
        
        sqla.session.commit()
        print("[✓] All sample/mock players, bookings, sessions, and events have been cleared!")
        print("[i] Admin login credentials ('admin') remain intact.")

if __name__ == '__main__':
    clear_mock_data()
