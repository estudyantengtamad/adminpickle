"""
Database Initialization & Table Migration Script
Creates database tables in PostgreSQL / Supabase and seeds real player accounts,
confirmed bookings, and open play sessions directly matching the Player App (player/model.py).
"""
import time
from datetime import datetime
from backend.app import create_app
from backend.models.mock_db import (
    sqla, AdminUser, User, ConfirmedBooking, OpenPlaySession,
    SessionParticipant, PlayerRating, EventPost, AuditLog, PlatformSetting
)
from werkzeug.security import generate_password_hash

import sys
from sqlalchemy import text

def init_database(reset=False):
    app = create_app()
    with app.app_context():
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        display_uri = db_uri.split('@')[-1] if '@' in db_uri else db_uri
        print(f"[*] Connecting to Supabase database: {display_uri}")

        if reset or '--reset' in sys.argv or '--drop' in sys.argv:
            print("[!] Dropping old/previous tables...")
            sqla.session.execute(text("""
                DROP TABLE IF EXISTS players CASCADE;
                DROP TABLE IF EXISTS users CASCADE;
                DROP TABLE IF EXISTS confirmed_bookings CASCADE;
                DROP TABLE IF EXISTS open_play_sessions CASCADE;
                DROP TABLE IF EXISTS session_participants CASCADE;
                DROP TABLE IF EXISTS player_ratings CASCADE;
                DROP TABLE IF EXISTS direct_bookings CASCADE;
                DROP TABLE IF EXISTS event_posts CASCADE;
                DROP TABLE IF EXISTS moderation_reports CASCADE;
                DROP TABLE IF EXISTS audit_logs CASCADE;
                DROP TABLE IF EXISTS platform_settings CASCADE;
                DROP TABLE IF EXISTS admin_users CASCADE;
            """))
            sqla.session.commit()
            print("[+] Successfully dropped old tables.")

        print("[*] Creating all database tables...")
        sqla.create_all()
        print("[+] All database tables created successfully!")

        # 1. Seed Default Administrator
        existing_admin = AdminUser.query.filter_by(username="admin").first()
        if not existing_admin:
            print("[*] Seeding default administrator account ('admin')...")
            default_admin = AdminUser(
                username="admin",
                name="Karl Alegrado",
                role="Lead Platform Admin",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
                password_hash=generate_password_hash("password123")
            )
            sqla.session.add(default_admin)
            print("[+] Seeded Admin: 'admin' / 'password123'")
        else:
            print(f"[i] Admin account already exists (Username: {existing_admin.username})")

        # 2. Seed Real Player Profiles (from player/model.py)
        if User.query.count() == 0:
            print("[*] Seeding real player accounts from Player App...")
            players_data = [
                User(
                    handle="zask_game",
                    name="Zask Paddler",
                    email="zask.paddler@picklelegends.ph",
                    contact="0917-123-4567",
                    bio="Pickleball enthusiast & competitive doubles player based in Butuan City.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Aggressive Kitchen Play",
                    member_since="July 2026",
                    rank="Beginner - Intermediate",
                    rank_short="Beginner",
                    avatar=None,
                    initials="ZP",
                    elo=1420,
                    xp=1200,
                    max_xp=2000,
                    wins=4,
                    losses=3,
                    total_games=7,
                    win_rate="57%",
                    dupr_id="DUPR-8812",
                    dupr_rating=3.25,
                    dupr_verified=True,
                    self_reported_skill="Intermediate",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="mining_paddy",
                    name="Mining Paddy",
                    email="mining.paddy@picklelegends.ph",
                    contact="0918-234-5678",
                    bio="Tournament champion. Power dinking and fast spin serves.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Power Baseline",
                    member_since="June 2026",
                    rank="Advanced / DUPR Rated (3.5+)",
                    rank_short="Diamond",
                    avatar="/static/assets/paddy.png",
                    initials="MP",
                    elo=1980,
                    xp=2450,
                    max_xp=3000,
                    wins=28,
                    losses=4,
                    total_games=32,
                    win_rate="87.5%",
                    dupr_id="DUPR-9011",
                    dupr_rating=4.50,
                    dupr_verified=True,
                    self_reported_skill="Advanced",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="karlito",
                    name="Karlito Manabat",
                    email="karlito.manabat@picklelegends.ph",
                    contact="0919-345-6789",
                    bio="Top ranked league doubles player. Speed and court vision.",
                    preferred_court="PickleYard Butuan Arena",
                    play_style="All-Round Tactical",
                    member_since="May 2026",
                    rank="Advanced (3.5 - 4.0)",
                    rank_short="Platinum",
                    avatar="/static/assets/karlito.png",
                    initials="KM",
                    elo=1840,
                    xp=2180,
                    max_xp=2500,
                    wins=22,
                    losses=6,
                    total_games=28,
                    win_rate="78.6%",
                    dupr_id="DUPR-9124",
                    dupr_rating=3.90,
                    dupr_verified=True,
                    self_reported_skill="Advanced",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="theux",
                    name="Theux trutut",
                    email="theux@picklelegends.ph",
                    contact="0920-456-7890",
                    bio="Fast attacker & consistent third-shot drop specialist.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Aggressive Net",
                    member_since="July 2026",
                    rank="Intermediate - Advanced",
                    rank_short="Gold",
                    avatar="/static/assets/theux.png",
                    initials="TT",
                    elo=1720,
                    xp=1920,
                    max_xp=2200,
                    wins=18,
                    losses=8,
                    total_games=26,
                    win_rate="69.2%",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="alex_r",
                    name="Alex Rivera",
                    email="alex.rivera@picklelegends.ph",
                    contact="0921-567-8901",
                    bio="Weekend player. Great sportsmanship and friendly matches.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Defensive Control",
                    member_since="August 2026",
                    rank="Intermediate",
                    rank_short="Silver",
                    avatar=None,
                    initials="AR",
                    elo=1510,
                    xp=950,
                    max_xp=1500,
                    wins=9,
                    losses=7,
                    total_games=16,
                    win_rate="56.2%",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="sofia_g",
                    name="Sofia Garcia",
                    email="sofia.garcia@picklelegends.ph",
                    contact="0922-678-9012",
                    bio="Singles and doubles player. Competitive mindset.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Strategic Placement",
                    member_since="August 2026",
                    rank="Intermediate",
                    rank_short="Silver",
                    avatar=None,
                    initials="SG",
                    elo=1480,
                    xp=880,
                    max_xp=1500,
                    wins=8,
                    losses=6,
                    total_games=14,
                    win_rate="57.1%",
                    status="Active",
                    reports=0
                ),
                User(
                    handle="mark_k",
                    name="Mark Kenneth",
                    email="mark.k@picklelegends.ph",
                    contact="0923-789-0123",
                    bio="New to the club, eager to join open play rotations.",
                    preferred_court="Butuan Ground Zero Pickleball Yard",
                    play_style="Beginner Balanced",
                    member_since="September 2026",
                    rank="Beginner",
                    rank_short="Bronze",
                    avatar=None,
                    initials="MK",
                    elo=1260,
                    xp=450,
                    max_xp=1000,
                    wins=3,
                    losses=4,
                    total_games=7,
                    win_rate="42.8%",
                    status="Active",
                    reports=0
                )
            ]
            for u in players_data:
                sqla.session.add(u)
            print(f"[+] Seeded {len(players_data)} player accounts into 'users' table.")
        else:
            print(f"[i] Users already present in database ({User.query.count()} players)")

        # 3. Seed Confirmed Bookings (from player/model.py)
        if ConfirmedBooking.query.count() == 0:
            print("[*] Seeding confirmed court bookings...")
            bookings = [
                ConfirmedBooking(
                    id="BK-4081",
                    court="Butuan Ground Zero Pickleball Yard",
                    court_no="Court 1 (Main Championship)",
                    customer_name="Zask Paddler",
                    date="October 16, 2026",
                    time="06:00 PM",
                    duration="2 hrs",
                    amount_paid=600.0,
                    payment_method="GCash",
                    staff_name="Coach Dave Reyes",
                    status="Confirmed",
                    flow_type="direct"
                ),
                ConfirmedBooking(
                    id="BK-9122",
                    court="Butuan Ground Zero Pickleball Yard",
                    court_no="Court 2 (Air-Conditioned Indoor)",
                    customer_name="Zask Paddler",
                    date="October 18, 2026",
                    time="08:00 AM",
                    duration="2 hrs",
                    amount_paid=600.0,
                    payment_method="GCash",
                    staff_name="Officer Marcus Tan",
                    status="Confirmed",
                    flow_type="direct"
                ),
                ConfirmedBooking(
                    id="BK-7729",
                    court="PickleYard Butuan Arena",
                    court_no="Court 3 (Outdoor Pro)",
                    customer_name="Mining Paddy",
                    date="October 24, 2026",
                    time="05:00 PM",
                    duration="2 hrs",
                    amount_paid=500.0,
                    payment_method="PayMaya",
                    staff_name="Coach Sarah Cruz",
                    status="Confirmed",
                    flow_type="direct"
                )
            ]
            for b in bookings:
                sqla.session.add(b)
            print(f"[+] Seeded {len(bookings)} confirmed bookings.")

        # 4. Seed Open Play Sessions (from player/model.py)
        if OpenPlaySession.query.count() == 0:
            print("[*] Seeding open play sessions...")
            sessions = [
                OpenPlaySession(
                    id="op_1",
                    title="Thursday Night Rally & Dinks",
                    booking_id="BK-4081",
                    court="Butuan Ground Zero Pickleball Yard",
                    court_no="Court 1 (Main Court)",
                    date="October 16, 2026",
                    time="6:00 PM - 8:00 PM",
                    staff_name="Coach Dave Reyes",
                    host_name="Zask Paddler",
                    host_handle="zask_game",
                    host_initials="ZP",
                    match_format="Doubles 2v2 Round Robin",
                    skill_level="Intermediate (3.0 - 3.5)",
                    max_players=8,
                    fee_per_player="₱75 / player (Split Court Fee)",
                    notes="Franklin X-40 balls provided! Come 10 mins early for warmup.",
                    status="open",
                    court_count=3
                ),
                OpenPlaySession(
                    id="op_2",
                    title="Weekend Morning Shootout",
                    booking_id="BK-9122",
                    court="Butuan Ground Zero Pickleball Yard",
                    court_no="Court 2 (Indoor Air-con)",
                    date="October 18, 2026",
                    time="8:00 AM - 10:00 AM",
                    staff_name="Officer Marcus Tan",
                    host_name="Zask Paddler",
                    host_handle="zask_game",
                    host_initials="ZP",
                    match_format="King of the Court",
                    skill_level="All Skill Levels Welcome",
                    max_players=8,
                    fee_per_player="₱75 / player (Split Court Fee)",
                    notes="Friendly rotation style. All paddles welcome!",
                    status="full",
                    court_count=3
                ),
                OpenPlaySession(
                    id="op_3",
                    title="Competitive DUPR Rated Doubles",
                    booking_id="BK-7729",
                    court="PickleYard Butuan Arena",
                    court_no="Court 3 (Outdoor Pro)",
                    date="October 20, 2026",
                    time="5:00 PM - 7:00 PM",
                    staff_name="Coach Sarah Cruz",
                    host_name="Mining Paddy",
                    host_handle="mining_paddy",
                    host_initials="MP",
                    match_format="Competitive Ladder",
                    skill_level="Advanced / DUPR Rated (3.5+)",
                    max_players=8,
                    fee_per_player="₱100 / player (Court + Balls)",
                    notes="Official DUPR sanctioned matches. Log results after games.",
                    status="open",
                    court_count=3
                )
            ]
            for s in sessions:
                sqla.session.add(s)

            # Seed joined participants for op_1
            participants = [
                SessionParticipant(id="part_1", session_id="op_1", player_id="zask_game", player_name="Zask Paddler", initials="ZP", elo=1420, is_host=True),
                SessionParticipant(id="part_2", session_id="op_1", player_id="alex_r", player_name="Alex Rivera", initials="AR", elo=1510, is_host=False),
                SessionParticipant(id="part_3", session_id="op_1", player_id="sofia_g", player_name="Sofia Garcia", initials="SG", elo=1480, is_host=False),
                SessionParticipant(id="part_4", session_id="op_1", player_id="mark_k", player_name="Mark Kenneth", initials="MK", elo=1260, is_host=False),
                SessionParticipant(id="part_5", session_id="op_1", player_id="karlito", player_name="Karlito Manabat", initials="KM", elo=1840, is_host=False),
                SessionParticipant(id="part_6", session_id="op_1", player_id="theux", player_name="Theux trutut", initials="TT", elo=1720, is_host=False)
            ]
            for p in participants:
                sqla.session.add(p)
            print(f"[+] Seeded {len(sessions)} open play sessions with confirmed participants.")

        # 5. Seed Event Posts
        if EventPost.query.count() == 0:
            print("[*] Seeding event posts & announcements...")
            events = [
                EventPost(
                    id="EVT-101",
                    title="Autumn Open Championship 2026",
                    event_type="Tournament",
                    date="Nov 15, 2026",
                    description="Annual club tournament with DUPR division brackets and a $5,000 prize pool. Registration open for Singles and Doubles.",
                    image_url="https://images.unsplash.com/photo-1599474924187-334a4ae5bd3c?auto=format&fit=crop&w=800&q=80",
                    author="Karl Alegrado"
                ),
                EventPost(
                    id="EVT-102",
                    title="Weekly Saturday Open Play & Social Mixer",
                    event_type="Open Play Day",
                    date="Every Saturday, 8:00 AM - 12:00 PM",
                    description="All courts open for friendly rotation matches and paddle king-of-the-court. New players welcome!",
                    image_url="https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=800&q=80",
                    author="Karl Alegrado"
                ),
                EventPost(
                    id="EVT-103",
                    title="Free Carbon Paddle Rental Promo",
                    event_type="Promo",
                    date="Nov 01 - Nov 07, 2026",
                    description="Book 2 or more hours on any weekday afternoon (1 PM - 5 PM) and get up to 2 carbon pro paddles free.",
                    image_url="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80",
                    author="Karl Alegrado"
                )
            ]
            for e in events:
                sqla.session.add(e)
            print(f"[+] Seeded {len(events)} club events.")

        # 6. Seed Audit Logs
        if AuditLog.query.count() == 0:
            sqla.session.add(AuditLog(action="Connected Unified Cloud Database with Player App", admin="System (Auto)"))
            sqla.session.add(AuditLog(action="Configured Butuan Ground Zero Court Venues", admin="Karl Alegrado"))

        sqla.session.commit()
        print("\n[✓] Database initialization complete! All tables and live data are synchronized in Supabase.")

if __name__ == '__main__':
    init_database()
