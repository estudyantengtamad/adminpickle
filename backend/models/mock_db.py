"""
PickleLegends Admin Platform - In-Memory Mock Database
Contains mock data stores and business logic for User Management, Venues, Moderation,
and the Admin-Side "Open Play" Session Hosting & Fair Rotation Engine.
"""

from datetime import datetime, timedelta
try:
    from flask_login import UserMixin
except ImportError:
    class UserMixin:
        pass
from werkzeug.security import generate_password_hash, check_password_hash

# ==============================================================================
# 1. ADMIN USER & AUTHENTICATION MODEL
# ==============================================================================

class AdminUser(UserMixin):  # type: ignore[misc]
    """
    Represents an authenticated Administrative User on the PickleLegends platform.
    Job: Wraps user credentials and role details for Flask-Login integration.
    """
    def __init__(self, id, username, name, role, avatar_url, password_hash):
        self.id = id
        self.username = username
        self.name = name
        self.role = role
        self.avatar_url = avatar_url
        self.password_hash = password_hash

    def check_password(self, password):
        """Verifies clear-text password against stored bcrypt/werkzeug hash."""
        return check_password_hash(self.password_hash, password)


# ==============================================================================
# 2. OPEN PLAY DATA MODELS (LOGICAL ENTITIES)
# ==============================================================================

class OpenPlaySession:
    """
    OpenPlaySession Entity
    Job: Stores host information for an Admin Open Play session.
    Fields:
      - id: Unique session string ID (e.g., 'SESS-101')
      - title: Event name (e.g., 'Downtown Morning DUPR Open Play')
      - date: YYYY-MM-DD formatted date string
      - start_time: Formatted start time (e.g., '08:00 AM')
      - end_time: Formatted end time (e.g., '11:00 AM')
      - court_count: Total available court count for this session (e.g., 3)
      - max_players: Total capacity / player limit (e.g., 16)
      - status: Current state ('upcoming', 'active', 'completed')
      - created_at: Datetime when session was created by admin
    """
    def __init__(self, id, title, date, start_time, end_time, court_count, max_players, status="upcoming"):
        self.id = id
        self.title = title
        self.date = date
        self.start_time = start_time
        self.end_time = end_time
        self.court_count = int(court_count)
        self.max_players = int(max_players)
        self.status = status  # 'upcoming', 'active', or 'completed'
        self.created_at = datetime.now()

    def to_dict(self):
        """Serializes session object into standard dictionary for API responses."""
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "court_count": self.court_count,
            "max_players": self.max_players,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class SessionParticipant:
    """
    SessionParticipant Entity
    Job: Tracks a player's entry on a session's waiting list or confirmed lineup.
    Fields:
      - id: Unique participant entry ID (e.g., 'PART-501')
      - session_id: Reference ID of OpenPlaySession
      - player_id: Reference ID of Player (e.g., 'USR-9982')
      - player_name: Handle / Display name of player
      - elo: Player's skill rating (DUPR-style ELO)
      - joined_at: Datetime when player joined/was added to waiting list
      - payment_deadline: Datetime deadline for payment (joined_at + 6 hours)
      - payment_status: 'pending', 'paid', or 'expired'
      - payment_method: 'gcash', 'online', or 'cash'
      - receipt: Mock file/image reference string or None (e.g., 'receipt_USR-9982.png')
      - confirmed_at: Datetime when admin confirmed/approved payment
      - games_played: Counter tracking how many games player completed in this session
      - rotation_status: Current queue status ('waiting', 'playing', 'resting')
    """
    def __init__(self, id, session_id, player_id, player_name, elo, joined_at=None,
                 payment_method="gcash", payment_status="pending", receipt=None, confirmed_at=None):
        self.id = id
        self.session_id = session_id
        self.player_id = player_id
        self.player_name = player_name
        self.elo = int(elo)
        self.joined_at = joined_at or datetime.now()
        # 6-Hour payment deadline policy:
        self.payment_deadline = self.joined_at + timedelta(hours=6)
        self.payment_status = payment_status  # 'pending', 'paid', or 'expired'
        self.payment_method = payment_method  # 'gcash', 'online', 'cash'
        self.receipt = receipt  # mock file reference or URL string
        self.confirmed_at = confirmed_at
        self.games_played = 0
        self.rotation_status = "waiting"  # 'waiting', 'playing', 'resting'

    def is_deadline_passed(self):
        """Checks if the 6-hour payment deadline has elapsed."""
        return datetime.now() > self.payment_deadline

    def to_dict(self):
        """Serializes participant into dictionary format."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "player_id": self.player_id,
            "player_name": self.player_name,
            "elo": self.elo,
            "joined_at": self.joined_at.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_deadline": self.payment_deadline.strftime("%Y-%m-%d %H:%M:%S"),
            "payment_status": self.payment_status,
            "payment_method": self.payment_method,
            "receipt": self.receipt,
            "confirmed_at": self.confirmed_at.strftime("%Y-%m-%d %H:%M:%S") if self.confirmed_at else None,
            "games_played": self.games_played,
            "rotation_status": self.rotation_status
        }


class Game:
    """
    Game Entity
    Job: Represents an active or completed 2v2 Open Play match on a court.
    Fields:
      - id: Unique match ID (e.g., 'GAME-701')
      - session_id: Reference ID of OpenPlaySession
      - court_number: Assigned court number (1 to court_count)
      - team_a: List of 2 participant dicts/objects
      - team_b: List of 2 participant dicts/objects
      - team_a_score: Final score for Team A (default 0)
      - team_b_score: Final score for Team B (default 0)
      - started_at: Datetime when match started
      - ended_at: Datetime when match finished
      - status: Match execution state ('in_progress', 'completed')
    """
    def __init__(self, id, session_id, court_number, team_a, team_b, status="in_progress"):
        self.id = id
        self.session_id = session_id
        self.court_number = int(court_number)
        self.team_a = team_a  # [participant_a1, participant_a2]
        self.team_b = team_b  # [participant_b1, participant_b2]
        self.team_a_score = 0
        self.team_b_score = 0
        self.started_at = datetime.now()
        self.ended_at = None
        self.status = status  # 'in_progress' or 'completed'

    def to_dict(self):
        """Serializes game data for UI rendering."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "court_number": self.court_number,
            "team_a": [p.player_name if hasattr(p, 'player_name') else p['player_name'] for p in self.team_a],
            "team_b": [p.player_name if hasattr(p, 'player_name') else p['player_name'] for p in self.team_b],
            "team_a_score": self.team_a_score,
            "team_b_score": self.team_b_score,
            "started_at": self.started_at.strftime("%H:%M:%S"),
            "ended_at": self.ended_at.strftime("%H:%M:%S") if self.ended_at else None,
            "status": self.status
        }


# ==============================================================================
# BOOKING SHEET CONSTANTS & HELPER UTILITIES
# ==============================================================================

BOOKING_TIME_SLOTS = [
    "06:00 AM", "07:00 AM", "08:00 AM", "09:00 AM", "10:00 AM", "11:00 AM",
    "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM", "04:00 PM", "05:00 PM",
    "06:00 PM", "07:00 PM", "08:00 PM", "09:00 PM", "10:00 PM", "11:00 PM", "12:00 AM"
]

BOOKING_COURTS = ["Court 1", "Court 2", "Court 3", "Court 4", "Court 5", "Court 6"]


def parse_time_to_minutes(time_str):
    """Converts time strings like '08:00 AM', '1:30 PM', '12:00AM' to minutes from midnight."""
    if not time_str:
        return 0
    t_str = time_str.strip().upper()
    # Normalize formats like "12:00AM" -> "12:00 AM"
    if t_str.endswith("AM") and not t_str.endswith(" AM"):
        t_str = t_str[:-2] + " AM"
    elif t_str.endswith("PM") and not t_str.endswith(" PM"):
        t_str = t_str[:-2] + " PM"

    try:
        dt = datetime.strptime(t_str, "%I:%M %p")
        return dt.hour * 60 + dt.minute
    except ValueError:
        try:
            dt = datetime.strptime(t_str, "%H:%M")
            return dt.hour * 60 + dt.minute
        except ValueError:
            return 0


def parse_court_number(court_val, default=1):
    """Safely extracts integer court number from 'Court 1', '1', or int 1."""
    if isinstance(court_val, int):
        return court_val
    if isinstance(court_val, str):
        if court_val.isdigit():
            return int(court_val)
        if "Court" in court_val:
            try:
                return int(court_val.replace("Court", "").strip())
            except ValueError:
                pass
    return default



class DirectBooking:
    """
    DirectBooking Entity
    Job: Stores admin-created direct court reservations on the Digital Booking Sheet.
    Fields:
      - id: Unique booking ID (e.g. 'BK-1001')
      - date: Date string 'YYYY-MM-DD'
      - court: Court identifier string 'Court 1'
      - time_slot: Time slot string '08:00 AM'
      - customer_name: Player/Customer name
      - payment_status: 'paid' or 'unpaid'
      - created_at: Datetime created
    """
    def __init__(self, id, date, court, time_slot, customer_name, payment_status="paid", rent_paddle=False, paddle_count=0, duration_hours=1, group_id=None, start_time_slot=None, created_at=None):
        self.id = id
        self.group_id = group_id or id
        self.date = date
        self.court = court
        self.time_slot = time_slot
        self.start_time_slot = start_time_slot or time_slot
        self.customer_name = customer_name
        self.payment_status = payment_status.lower()  # 'paid' or 'unpaid'
        self.rent_paddle = bool(rent_paddle)
        self.paddle_count = int(paddle_count) if rent_paddle else 0
        self.duration_hours = int(duration_hours) if duration_hours else 1
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "group_id": self.group_id,
            "date": self.date,
            "court": self.court,
            "time_slot": self.time_slot,
            "start_time_slot": self.start_time_slot,
            "customer_name": self.customer_name,
            "payment_status": self.payment_status,
            "rent_paddle": self.rent_paddle,
            "paddle_count": self.paddle_count,
            "duration_hours": self.duration_hours,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


class EventPost:
    """
    EventPost Entity
    Job: Stores tournaments, open play announcements, promos, and club notices visible on player dashboards.
    Fields:
      - id: Unique event ID (e.g., 'EVT-101')
      - title: Event name / headline
      - event_type: 'Tournament', 'Open Play Day', 'Announcement', 'Promo'
      - date: Display date string (e.g., 'Nov 15, 2026')
      - description: Short summary / details (max 200 chars recommended)
      - image_url: Optional photo / poster banner URL or base64 data string
      - author: Name of posting admin
      - status: 'Published'
      - created_at: Datetime
    """
    def __init__(self, id, title, event_type="Announcement", date=None, description="", image_url="", author="Admin", status="Published", created_at=None):
        self.id = id
        self.title = title
        self.event_type = event_type
        self.date = date or datetime.now().strftime("%b %d, %Y")
        self.description = description or ""
        self.image_url = image_url or ""
        self.author = author
        self.status = status
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "event_type": self.event_type,
            "date": self.date,
            "description": self.description,
            "image_url": self.image_url,
            "author": self.author,
            "status": self.status,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# ==============================================================================
# 3. MAIN MOCK DATABASE STORE & BUSINESS LOGIC ENGINE
# ==============================================================================

class MockDatabase:
    """
    In-Memory Mock Database Singleton.
    Job: Maintains platform state across admin users, players, venues, settings,
    and Open Play sessions + rotation execution.
    """
    def __init__(self):
        # Admin account credential store
        self.users = {
            "1": AdminUser(
                id="1",
                username="admin",
                name="Karl Alegrado",
                role="Lead Platform Admin",
                avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80",
                password_hash=generate_password_hash("password123")
            )
        }

        # Executive Platform Metrics
        self.metrics = {
            "total_users": 12847,
            "daily_active": 3241,
            "active_bookings": 487,
            "total_revenue": "$2.4M",
            "latency_history": [
                {"time": "00:00", "latency": 18},
                {"time": "04:00", "latency": 15},
                {"time": "08:00", "latency": 28},
                {"time": "12:00", "latency": 42},
                {"time": "16:00", "latency": 35},
                {"time": "20:00", "latency": 22},
            ]
        }

        # System Logs & Audit Trail
        self.system_logs = [
            {"id": "LOG-9081", "timestamp": "Today, 21:44:12", "action": "Automated Open Play rotation check completed", "admin": "System (Auto)", "status": "Completed"},
            {"id": "LOG-9080", "timestamp": "Today, 20:15:00", "action": "Open Play Session #SESS-102 set to Active", "admin": "Karl Alegrado", "status": "Active"},
            {"id": "LOG-9079", "timestamp": "Today, 18:30:22", "action": "Payment confirmed for Participant #PART-502", "admin": "Karl Alegrado", "status": "Active"},
            {"id": "LOG-9078", "timestamp": "Today, 15:10:05", "action": "Penalty issued for User #USR-8812 (Toxic chat report)", "admin": "Sarah Jenkins", "status": "Verified"},
            {"id": "LOG-9077", "timestamp": "Yesterday, 22:00:19", "action": "System backup completed (24.8 GB)", "admin": "System (Auto)", "status": "Completed"},
        ]

        # Player Registry (Skill ELO Ratings)
        self.players = [
            {"id": "USR-9982", "name": "Sarah Jenkins", "elo": 1942, "tier": "Diamond", "win_rate": "74.2%", "status": "Active", "matches": 312, "reports": 0, "notes": "Top tier competitive player. Consistent league attendee."},
            {"id": "USR-9921", "name": "Karl Alegrado", "elo": 1835, "tier": "Gold", "win_rate": "68.5%", "status": "Active", "matches": 240, "reports": 0, "notes": "Platform developer & tournament organizer."},
            {"id": "USR-9804", "name": "Darnell Castro", "elo": 1690, "tier": "Platinum", "win_rate": "62.1%", "status": "Active", "matches": 189, "reports": 1, "notes": "Regular evening open play player."},
            {"id": "USR-9712", "name": "Grace Santos", "elo": 2010, "tier": "Diamond", "win_rate": "81.0%", "status": "Active", "matches": 450, "reports": 0, "notes": "National pickleball championship contender."},
            {"id": "USR-9650", "name": "Jaye Antonio", "elo": 1420, "tier": "Silver", "win_rate": "51.4%", "status": "Frozen", "matches": 95, "reports": 3, "notes": "Temporary cooldown pending identity verification."},
            {"id": "USR-9511", "name": "Vaughn Hancock", "elo": 1550, "tier": "Gold", "win_rate": "55.8%", "status": "Active", "matches": 130, "reports": 0, "notes": "Casual weekend player."},
            {"id": "USR-9402", "name": "Mark Rivera", "elo": 1210, "tier": "Bronze", "win_rate": "42.0%", "status": "Active", "matches": 60, "reports": 0, "notes": "New member, beginner league."},
            {"id": "USR-9311", "name": "Mabelle Kimball", "elo": 1780, "tier": "Platinum", "win_rate": "69.4%", "status": "Banned", "matches": 210, "reports": 8, "notes": "Banned for repeated unsportsmanlike conduct."},
            {"id": "USR-9201", "name": "Leo Valdes", "elo": 1620, "tier": "Gold", "win_rate": "60.0%", "status": "Active", "matches": 110, "reports": 0, "notes": "Solid mid-tier player."},
            {"id": "USR-9110", "name": "Elmo Villanueva", "elo": 1880, "tier": "Diamond", "win_rate": "71.0%", "status": "Active", "matches": 290, "reports": 0, "notes": "Fast power server."},
            {"id": "USR-9004", "name": "Tina Laurel", "elo": 1490, "tier": "Silver", "win_rate": "53.2%", "status": "Active", "matches": 85, "reports": 0, "notes": "Consistent drop shot player."},
            {"id": "USR-8910", "name": "Rico Solis", "elo": 1710, "tier": "Platinum", "win_rate": "64.5%", "status": "Active", "matches": 175, "reports": 0, "notes": "Aggressive kitchen player."}
        ]

        # Venue & Court Manager Data
        self.total_courts = 6
        self.venues = [
            {"id": 1, "name": "Current Paddle Club", "courts": self.total_courts, "rate": "120 pts/hr", "active": True},
            {"id": 2, "name": "Quantum Courts", "courts": 8, "rate": "150 pts/hr", "active": False},
            {"id": 3, "name": "Riverside Arena", "courts": 4, "rate": "100 pts/hr", "active": False},
            {"id": 4, "name": "Harbor Sports Center", "courts": 5, "rate": "130 pts/hr", "active": False}
        ]

        self.time_slots = ["08:00 AM", "10:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM"]
        self.courts = ["Court 1", "Court 2", "Court 3", "Court 4", "Court 5", "Court 6"]

        self.court_grid = {
            "08:00 AM": {"Court 1": "Available", "Court 2": "Booked", "Court 3": "Maintenance", "Court 4": "Available", "Court 5": "Available", "Court 6": "Available"},
            "10:00 AM": {"Court 1": "Booked", "Court 2": "Booked", "Court 3": "Maintenance", "Court 4": "Reserved", "Court 5": "Available", "Court 6": "Available"},
            "12:00 PM": {"Court 1": "Available", "Court 2": "Available", "Court 3": "Booked", "Court 4": "Available", "Court 5": "Booked", "Court 6": "Available"},
            "02:00 PM": {"Court 1": "Available", "Court 2": "Reserved", "Court 3": "Available", "Court 4": "Available", "Court 5": "Available", "Court 6": "Available"},
            "04:00 PM": {"Court 1": "Booked", "Court 2": "Available", "Court 3": "Maintenance", "Court 4": "Available", "Court 5": "Available", "Court 6": "Available"},
            "06:00 PM": {"Court 1": "Available", "Court 2": "Booked", "Court 3": "Booked", "Court 4": "Available", "Court 5": "Available", "Court 6": "Available"},
        }

        # Moderation Data (Clean, straightforward report queue)
        self.reported_players = [
            {"id": "REP-801", "player_id": "USR-9311", "player_name": "Mabelle Kimball", "reporter": "USR-9982 (Sarah)", "reason": "Unsportsmanlike conduct and delaying court rotation", "severity": "High", "date": "Today, 19:40", "status": "Pending Action"},
            {"id": "REP-802", "player_id": "USR-9804", "player_name": "Darnell Castro", "reporter": "USR-9402 (Mark)", "reason": "No-show for reserved match slot", "severity": "Medium", "date": "Yesterday, 21:15", "status": "Pending Action"},
        ]

        self.chat_logs = {
            "USR-9311": [
                {"time": "19:35", "sender": "Mabelle Kimball", "text": "Are you guys serious? Learn how to serve properly.", "toxic": True},
                {"time": "19:36", "sender": "Sarah Jenkins", "text": "Hey keep it friendly please.", "toxic": False},
            ]
        }

        # Event & Announcement Posts (Surfaced to player dashboards & admin)
        self.event_posts = [
            EventPost(
                id="EVT-101",
                title="Autumn Open Championship 2026",
                event_type="Tournament",
                date="Nov 15, 2026",
                description="Annual club tournament with DUPR division brackets and a $5,000 prize pool. Registration is open for Singles and Doubles.",
                image_url="https://images.unsplash.com/photo-1599474924187-334a4ae5bd3c?auto=format&fit=crop&w=800&q=80",
                author="Karl Alegrado"
            ),
            EventPost(
                id="EVT-102",
                title="Weekly Saturday Open Play & Social Mixer",
                event_type="Open Play Day",
                date="Every Saturday, 8:00 AM - 12:00 PM",
                description="All available courts open for friendly rotation matches and paddle king-of-the-court. New players welcome!",
                image_url="https://images.unsplash.com/photo-1626224583764-f87db24ac4ea?auto=format&fit=crop&w=800&q=80",
                author="Karl Alegrado"
            ),
            EventPost(
                id="EVT-103",
                title="Weekday Free Paddle Rental Promo",
                event_type="Promo",
                date="Nov 01 - Nov 07, 2026",
                description="Book 2 or more hours on any weekday afternoon (1 PM - 5 PM) and get up to 2 carbon pro paddles free for your game.",
                image_url="https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80",
                author="Karl Alegrado"
            ),
            EventPost(
                id="EVT-104",
                title="Court 3 Morning Maintenance Notice",
                event_type="Announcement",
                date="Tomorrow, 07:00 AM - 09:00 AM",
                description="Court 3 will be offline briefly for surface cleaning and net tension check. All other courts operate normally.",
                image_url="",
                author="Karl Alegrado"
            )
        ]

        self.tournaments = [
            {"id": "EVT-101", "title": "Autumn Open 2026", "venue": "Current Paddle Club", "date": "Nov 15, 2026", "status": "Published", "tag": "TOURNAMENT"},
        ]

        self.audit_logs = [
            {"timestamp": "Today, 20:00:00", "admin": "Karl Alegrado", "action": "Initialized Open Play Platform Engine", "ip": "192.168.1.45"}
        ]

        # ======================================================================
        # OPEN PLAY MOCK STORES & SEED DATA
        # ======================================================================
        self.open_play_sessions = {}
        self.session_participants = {}  # session_id -> list of SessionParticipant
        self.session_games = {}         # session_id -> list of Game
        self.past_combinations = {}     # session_id -> set of frozensets of player_ids

        # Seed Sample Open Play Sessions
        self._seed_open_play_data()

        # Digital Booking Sheet Data Store (date, court, time_slot) -> DirectBooking
        self.direct_bookings = {}
        self._seed_direct_bookings()

    # --------------------------------------------------------------------------
    # SEED DATA INITIALIZER
    # --------------------------------------------------------------------------
    def _seed_open_play_data(self):
        """No-op: Open Play module disabled."""
        pass


    # --------------------------------------------------------------------------
    # USER & PLAYER LOGIC
    # --------------------------------------------------------------------------
    def get_user_by_id(self, user_id):
        return self.users.get(str(user_id))

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None

    def update_admin_profile(self, user_id, name=None, role=None):
        """Updates admin display name and/or role title."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        old_name = user.name
        if name and name.strip():
            user.name = name.strip()
        if role and role.strip():
            user.role = role.strip()
        self.add_audit_log(f"Updated admin profile info for {user.username} (Name: '{user.name}', Role: '{user.role}')", user.name)
        return True, "Profile details updated successfully."

    def update_admin_avatar(self, user_id, avatar_url):
        """Updates admin profile picture URL."""
        user = self.get_user_by_id(user_id)
        if not user:
            return False, "User not found."
        user.avatar_url = avatar_url.strip()
        self.add_audit_log(f"Updated profile photo for administrator {user.name}", user.name)
        return True, "Profile photo updated successfully."

    def update_player_status(self, player_id, new_status):
        for p in self.players:
            if p["id"] == player_id:
                p["status"] = new_status
                return True
        return False

    def reset_player_rating(self, player_id, new_elo=1500):
        for p in self.players:
            if p["id"] == player_id:
                p["elo"] = new_elo
                return True
        return False

    def toggle_court_slot(self, time_slot, court):
        if time_slot in self.court_grid and court in self.court_grid[time_slot]:
            current = self.court_grid[time_slot][court]
            statuses = ["Available", "Booked", "Maintenance", "Reserved"]
            next_idx = (statuses.index(current) + 1) % len(statuses)
            self.court_grid[time_slot][court] = statuses[next_idx]
            return self.court_grid[time_slot][court]
        return None

    def set_total_courts(self, count, admin="Karl Alegrado"):
        """Sets the venue court count and synchronizes court listings."""
        try:
            count = max(1, min(20, int(count)))
        except (ValueError, TypeError):
            count = 6
        
        self.total_courts = count
        if self.venues:
            self.venues[0]["courts"] = count
        
        self.courts = [f"Court {i}" for i in range(1, count + 1)]
        global BOOKING_COURTS
        BOOKING_COURTS = [f"Court {i}" for i in range(1, count + 1)]
        
        self.add_audit_log(f"Updated venue court capacity to {count} courts", admin)
        return True, count

    def get_event_posts(self):
        """Returns all published events sorted by newest first."""
        return self.event_posts

    def create_event_post(self, title, event_type="Announcement", date=None, description="", image_url="", author="Karl Alegrado"):
        """Creates a new event/announcement post visible to players and admins."""
        existing_ids = {p.id for p in self.event_posts}
        counter = 101 + len(self.event_posts)
        while f"EVT-{counter}" in existing_ids:
            counter += 1
        
        post_id = f"EVT-{counter}"
        new_post = EventPost(
            id=post_id,
            title=title.strip(),
            event_type=event_type,
            date=date.strip() if date else datetime.now().strftime("%b %d, %Y"),
            description=description.strip(),
            image_url=image_url.strip() if image_url else "",
            author=author
        )
        self.event_posts.insert(0, new_post)
        self.add_audit_log(f"Published new {event_type} post: '{new_post.title}'", author)
        return new_post

    def delete_event_post(self, post_id, admin="Karl Alegrado"):
        """Deletes an event post by ID."""
        target = next((p for p in self.event_posts if p.id == post_id), None)
        if target:
            self.event_posts.remove(target)
            self.add_audit_log(f"Removed event post '{target.title}' ({post_id})", admin)
            return True
        return False

    def dismiss_report(self, report_id, admin="Karl Alegrado"):
        """Dismisses a player moderation report (e.g. false alarm / resolved)."""
        target = next((r for r in self.reported_players if r["id"] == report_id), None)
        if target:
            self.reported_players.remove(target)
            self.add_audit_log(f"Dismissed player report {report_id} against {target['player_name']}", admin)
            return True, f"Report {report_id} has been dismissed."
        return False, "Report not found."

    def warn_and_dismiss_report(self, report_id, admin="Karl Alegrado"):
        """Issues an official conduct warning to player and clears report."""
        target = next((r for r in self.reported_players if r["id"] == report_id), None)
        if target:
            player_name = target["player_name"]
            player_id = target.get("player_id")
            # Update player report counter if in players list
            for p in self.players:
                if p["id"] == player_id or p["name"] == player_name:
                    try:
                        p["reports"] = int(p.get("reports", 0)) + 1
                    except (ValueError, TypeError):
                        p["reports"] = 1
                    break
            self.reported_players.remove(target)
            self.add_audit_log(f"Issued formal conduct warning to {player_name} and closed report {report_id}", admin)
            return True, f"Conduct warning issued to {player_name}. Report cleared."
        return False, "Report not found."

    def add_audit_log(self, action, admin="Karl Alegrado"):
        now_str = datetime.now().strftime("%A, %H:%M:%S")
        self.audit_logs.insert(0, {
            "timestamp": now_str,
            "admin": admin,
            "action": action,
            "ip": "192.168.1.45"
        })
        self.system_logs.insert(0, {
            "id": f"LOG-{9082 + len(self.system_logs)}",
            "timestamp": "Just now",
            "action": action,
            "admin": admin,
            "status": "Completed"
        })

    # ==========================================================================
    # 4. OPEN PLAY ADMIN BUSINESS LOGIC METHODS
    # ==========================================================================

    def create_open_play_session(self, title, date, start_time, end_time, court_count, max_players):
        """Creates a new Open Play session (e.g. Saturday 9:00 AM on 4 courts)."""
        existing_sids = set(self.open_play_sessions.keys())
        counter = 101
        while f"SESS-{counter}" in existing_sids:
            counter += 1
        session_id = f"SESS-{counter}"
        session = OpenPlaySession(
            id=session_id,
            title=title or f"Open Play - {date}",
            date=date,
            start_time=start_time,
            end_time=end_time,
            court_count=court_count,
            max_players=max_players,
            status="upcoming"
        )
        self.open_play_sessions[session_id] = session
        self.session_participants[session_id] = []
        self.session_games[session_id] = []
        self.past_combinations[session_id] = set()

        self.add_audit_log(f"Created Open Play Session '{session.title}' ({court_count} Courts, Max {max_players} Players)")
        return session

    def get_open_play_sessions(self):
        """Returns all Open Play sessions sorted by creation date."""
        return list(self.open_play_sessions.values())

    def get_open_play_session(self, session_id):
        """Fetches session details and automatically checks if any pending payments have hit the 6-hour limit."""
        session = self.open_play_sessions.get(session_id)
        if session:
            self.lazy_check_expirations(session_id)
        return session

    def update_session_status(self, session_id, new_status):
        """
        Changes session state ('upcoming' -> 'active' -> 'completed').
        Starting a session ('active') automatically runs the rotation engine to seat players.
        """
        session = self.get_open_play_session(session_id)
        if not session:
            return False

        old_status = session.status
        session.status = new_status
        self.add_audit_log(f"Updated Session {session_id} status from '{old_status}' to '{new_status}'")

        if new_status == "active":
            # Run automatic rotation engine immediately to fill courts
            self.run_rotation_engine(session_id)
        elif new_status == "completed":
            # Clear playing rotation status on active games
            for g in self.session_games.get(session_id, []):
                if g.status == "in_progress":
                    g.status = "completed"
                    g.ended_at = datetime.now()

        return True

    def lazy_check_expirations(self, session_id):
        """
        Checks if 6 hours have passed since a player joined with pending payment.
        If deadline passed and payment is still 'pending', marks it 'expired'.
        """
        participants = self.session_participants.get(session_id, [])
        now = datetime.now()
        for p in participants:
            if p.payment_status == "pending" and now > p.payment_deadline:
                p.payment_status = "expired"

    def add_session_participant(self, session_id, player_id, payment_method="gcash", payment_status="pending", receipt=None):
        """Enrolls a registered player into a session's waiting list with a 6-hour payment window."""
        session = self.get_open_play_session(session_id)
        if not session:
            return None, "Session not found."

        # Check capacity
        participants = self.session_participants.get(session_id, [])
        if len(participants) >= session.max_players:
            return None, "Session player capacity reached."

        # Fetch player info
        player_info = next((p for p in self.players if p["id"] == player_id), None)
        player_name = player_info["name"] if player_info else f"Player {player_id}"
        elo = player_info["elo"] if player_info else 1500

        # Prevent duplicate enrollment in same session
        if any(p.player_id == player_id for p in participants):
            return None, f"Player {player_name} is already registered in this session."

        existing_ids = {p.id for parts in self.session_participants.values() for p in parts}
        counter = 501
        while f"PART-{counter}" in existing_ids:
            counter += 1
        part_id = f"PART-{counter}"
        joined_at = datetime.now()

        participant = SessionParticipant(
            id=part_id,
            session_id=session_id,
            player_id=player_id,
            player_name=player_name,
            elo=elo,
            joined_at=joined_at,
            payment_method=payment_method,
            payment_status=payment_status,
            receipt=receipt,
            confirmed_at=joined_at if payment_status == "paid" else None
        )

        participants.append(participant)
        self.add_audit_log(f"Added player {player_name} to session {session_id} waiting list ({payment_method.upper()}, status: {payment_status})")

        # If session is active and payment was pre-marked paid, trigger rotation check
        if session.status == "active" and payment_status == "paid":
            self.run_rotation_engine(session_id)

        return participant, "Player added to waiting list successfully!"

    def upload_participant_receipt(self, participant_id, receipt_filename):
        """Attaches a receipt screenshot filename to a player's registration."""
        for s_id, parts in self.session_participants.items():
            for p in parts:
                if p.id == participant_id:
                    p.receipt = receipt_filename
                    self.add_audit_log(f"Uploaded payment receipt reference for participant {p.player_name}")
                    return True, "Receipt uploaded successfully."
        return False, "Participant not found."

    def confirm_participant_payment(self, participant_id):
        """
        Approves a player's payment (paid).
        Only once payment is approved does the player enter the court rotation pool!
        """
        for session_id, parts in self.session_participants.items():
            for p in parts:
                if p.id == participant_id:
                    p.payment_status = "paid"
                    p.confirmed_at = datetime.now()
                    self.add_audit_log(f"Admin confirmed payment for player {p.player_name} in session {session_id}")

                    # If session is active, evaluate rotation queue immediately!
                    session = self.open_play_sessions.get(session_id)
                    if session and session.status == "active":
                        self.run_rotation_engine(session_id)

                    return True, f"Payment confirmed for {p.player_name}!"
        return False, "Participant not found."

    # --------------------------------------------------------------------------
    # AUTOMATIC ROTATION ENGINE (FAIR PLAY MATCHMAKING)
    # --------------------------------------------------------------------------

    def run_rotation_engine(self, session_id, target_court=None):
        """
        Automatic Court Rotation Engine:
        1. Selects 4 paid waiting players with the FEWEST games played.
        2. Shuffles them into 2 teams of 2.
        3. Avoids repeating the exact same 4-player matchup.
        4. Assigns them to the target open court (or all open courts if target_court is None).
        5. Updates their status to 'playing'.
        """
        session = self.open_play_sessions.get(session_id)
        if not session or session.status != "active":
            return []

        # Step 1: Lazily check expirations on waiting list
        self.lazy_check_expirations(session_id)

        participants = self.session_participants.get(session_id, [])
        games = self.session_games.get(session_id, [])

        # Find currently occupied courts
        occupied_courts = {g.court_number for g in games if g.status == "in_progress"}

        # Find available court numbers
        if target_court is not None:
            target_court = int(target_court)
            if target_court in occupied_courts or target_court < 1 or target_court > session.court_count:
                return []
            available_courts = [target_court]
        else:
            available_courts = [c for c in range(1, session.court_count + 1) if c not in occupied_courts]

        if not available_courts:
            return []  # No courts available!

        # Filter confirmed players ('paid') who are currently 'waiting'
        confirmed_waiting = [
            p for p in participants
            if p.payment_status == "paid" and p.rotation_status == "waiting"
        ]

        created_games = []

        # Fill available courts as long as we have 4+ confirmed waiting players
        while available_courts and len(confirmed_waiting) >= 4:
            # Sort by fewest games played first (fairness), break ties by joined_at
            confirmed_waiting.sort(key=lambda p: (p.games_played, p.joined_at))

            # Select 4 candidate players
            chosen_4 = self._select_fair_four_players(confirmed_waiting, session_id)
            if len(chosen_4) < 4:
                break

            # Remove chosen 4 from waiting queue for next loop iteration
            for p in chosen_4:
                confirmed_waiting.remove(p)

            # Split into 2 teams of 2
            team_a, team_b = self._balance_teams_by_elo(chosen_4)

            # Assign next open court
            court_num = available_courts.pop(0)

            # Mark players as playing
            for p in chosen_4:
                p.rotation_status = "playing"

            # Record 4-player combination in history store
            group_key = frozenset([p.player_id for p in chosen_4])
            if session_id not in self.past_combinations:
                self.past_combinations[session_id] = set()
            self.past_combinations[session_id].add(group_key)

            existing_gids = {g.id for s_games in self.session_games.values() for g in s_games}
            counter = 701
            while f"GAME-{counter}" in existing_gids:
                counter += 1
            game_id = f"GAME-{counter}"
            game = Game(
                id=game_id,
                session_id=session_id,
                court_number=court_num,
                team_a=team_a,
                team_b=team_b,
                status="in_progress"
            )

            games.append(game)
            created_games.append(game)

            player_names = ", ".join([p.player_name for p in chosen_4])
            self.add_audit_log(f"Auto-Rotation: Assigned Game {game_id} on Court #{court_num} with players [{player_names}]")

        return created_games

    def _select_fair_four_players(self, candidates, session_id):
        """
        Helper: Selects 4 players prioritizing fewest games played while avoiding
        repeating the exact same 4-player group if another candidate set exists.
        """
        if len(candidates) < 4:
            return []

        history = self.past_combinations.get(session_id, set())

        # Primary selection: first 4 sorted candidates
        primary = candidates[:4]
        group_key = frozenset([p.player_id for p in primary])

        # If primary group was not used recently, pick them!
        if group_key not in history or len(candidates) == 4:
            return primary

        # If primary group was already paired, check if swapping 4th candidate with 5th candidate creates fresh group
        if len(candidates) >= 5:
            alt_four = [candidates[0], candidates[1], candidates[2], candidates[4]]
            alt_key = frozenset([p.player_id for p in alt_four])
            if alt_key not in history:
                return alt_four

        # Fallback if all variations exhausted: use primary
        return primary

    def _balance_teams_by_elo(self, four_players):
        """Shuffles 4 players randomly into Team A (2 players) and Team B (2 players)."""
        import random
        shuffled = list(four_players)
        random.shuffle(shuffled)
        team_a = [shuffled[0], shuffled[1]]
        team_b = [shuffled[2], shuffled[3]]
        return team_a, team_b

    def finish_game(self, game_id, score_a=11, score_b=9, auto_rotate=True):
        """
        Marks a game as completed and records the final score.
        Increments games_played (+1) for each player and returns them to the waiting pool.
        If auto_rotate is True, automatically seats the next match on the freed court.
        """
        target_game = None
        target_session_id = None

        for s_id, games in self.session_games.items():
            for g in games:
                if g.id == game_id:
                    target_game = g
                    target_session_id = s_id
                    break

        if not target_game:
            return False, "Game not found.", []

        if target_game.status == "completed":
            return False, "Game is already finished.", []

        # Mark game completed
        target_game.status = "completed"
        target_game.team_a_score = int(score_a)
        target_game.team_b_score = int(score_b)
        target_game.ended_at = datetime.now()

        # Update participants: increment games_played, set status to 'waiting'
        all_match_players = target_game.team_a + target_game.team_b
        for p in all_match_players:
            p.games_played += 1
            p.rotation_status = "waiting"

        self.add_audit_log(f"Game {game_id} (Court #{target_game.court_number}) finished (Score: {score_a}-{score_b}). Players returned to rotation queue.")

        new_games = []
        if auto_rotate:
            new_games = self.run_rotation_engine(target_session_id, target_court=target_game.court_number)

        msg = f"Game marked finished ({score_a}-{score_b})."
        if new_games:
            msg += f" Auto-rotation seated new match on Court #{new_games[0].court_number}!"
        elif not auto_rotate:
            msg += f" Court #{target_game.court_number} is now open."

        return True, msg, new_games

    # ==========================================================================
    # DIGITAL BOOKING SHEET METHODS & CONFLICT ENGINE
    # ==========================================================================

    def _seed_direct_bookings(self):
        """Seeds sample direct court bookings for demonstration."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        seeds = [
            (today_str, "Court 1", "09:00 AM", "Juan Dela Cruz", "paid", True, 2),
            (today_str, "Court 1", "10:00 AM", "Maria Santos", "unpaid", False, 0),
            (today_str, "Court 3", "02:00 PM", "Pedro Penduko", "paid", True, 1),
            (today_str, "Court 2", "04:00 PM", "Ana Reyes", "unpaid", False, 0),
        ]
        booking_counter = 1001
        for d, c, t, name, status, rent_p, p_cnt in seeds:
            b_id = f"BK-{booking_counter}"
            self.direct_bookings[(d, c, t)] = DirectBooking(
                id=b_id, date=d, court=c, time_slot=t, customer_name=name, payment_status=status, rent_paddle=rent_p, paddle_count=p_cnt
            )
            booking_counter += 1

    def get_booking_sheet_matrix(self, date):
        """
        Returns full court matrix for ALL courts across all time slots for a specified date.
        """
        matrix = {}
        for time_slot in BOOKING_TIME_SLOTS:
            matrix[time_slot] = {}
            slot_start = parse_time_to_minutes(time_slot)
            slot_end = slot_start + 60

            for court in BOOKING_COURTS:
                court_num = parse_court_number(court)

                # Check Open Play overlap
                open_play_match = None
                for s in self.open_play_sessions.values():
                    if s.date == date and court_num <= s.court_count:
                        s_start = parse_time_to_minutes(s.start_time)
                        s_end = parse_time_to_minutes(s.end_time)
                        if max(slot_start, s_start) < min(slot_end, s_end):
                            open_play_match = s
                            break

                if open_play_match:
                    matrix[time_slot][court] = {
                        "status": "open_play",
                        "title": open_play_match.title,
                        "session_id": open_play_match.id,
                        "time_range": f"{open_play_match.start_time} - {open_play_match.end_time}",
                        "customer_name": None,
                        "payment_status": None,
                        "rent_paddle": False,
                        "paddle_count": 0,
                        "booking_id": None
                    }
                else:
                    booking_key = (date, court, time_slot)
                    if booking_key in self.direct_bookings:
                        b = self.direct_bookings[booking_key]
                        matrix[time_slot][court] = {
                            "status": "booked",
                            "customer_name": b.customer_name,
                            "payment_status": b.payment_status,
                            "rent_paddle": getattr(b, 'rent_paddle', False),
                            "paddle_count": getattr(b, 'paddle_count', 0),
                            "duration_hours": getattr(b, 'duration_hours', 1),
                            "group_id": getattr(b, 'group_id', b.id),
                            "start_time_slot": getattr(b, 'start_time_slot', b.time_slot),
                            "booking_id": b.id,
                            "title": None,
                            "time_range": None
                        }
                    else:
                        matrix[time_slot][court] = {
                            "status": "vacant",
                            "customer_name": None,
                            "payment_status": None,
                            "rent_paddle": False,
                            "paddle_count": 0,
                            "duration_hours": 1,
                            "group_id": None,
                            "start_time_slot": time_slot,
                            "booking_id": None,
                            "title": None,
                            "time_range": None
                        }


        return {
            "date": date,
            "time_slots": BOOKING_TIME_SLOTS,
            "courts": BOOKING_COURTS,
            "matrix": matrix
        }

    def get_booking_sheet_grid(self, date, court):
        """
        Returns time-slot list for a single court on a given date.
        Reuses get_booking_sheet_matrix for clean consistency.
        """
        sheet_matrix = self.get_booking_sheet_matrix(date)
        grid = []
        for time_slot in sheet_matrix["time_slots"]:
            cell_info = sheet_matrix["matrix"][time_slot].get(court, {
                "status": "vacant",
                "customer_name": None,
                "payment_status": None,
                "rent_paddle": False,
                "paddle_count": 0,
                "duration_hours": 1,
                "group_id": None,
                "booking_id": None,
                "title": None,
                "time_range": None
            })
            grid.append({
                "time_slot": time_slot,
                **cell_info
            })
        return grid

    def save_direct_booking(self, date, court, time_slot, customer_name, payment_status="paid", rent_paddle=False, paddle_count=0, duration_hours=1):
        """Saves or updates a direct court booking (supporting multi-hour bookings) after verifying no conflicts."""
        if not customer_name or not customer_name.strip():
            return False, "Customer / Player name is required."

        try:
            duration_hours = max(1, int(duration_hours))
        except (ValueError, TypeError):
            duration_hours = 1

        # Determine target consecutive time slots
        if time_slot in BOOKING_TIME_SLOTS:
            start_idx = BOOKING_TIME_SLOTS.index(time_slot)
            end_idx = start_idx + duration_hours
            if end_idx > len(BOOKING_TIME_SLOTS):
                return False, f"Cannot book {duration_hours} hours starting at {time_slot}: Exceeds available daily schedule."
            slots_to_book = BOOKING_TIME_SLOTS[start_idx:end_idx]
        else:
            slots_to_book = [time_slot]

        court_num = parse_court_number(court)

        # Check existing booking for this slot to see if we are updating a current booking group
        primary_key = (date, court, time_slot)
        existing_group = None
        if primary_key in self.direct_bookings:
            existing_group = getattr(self.direct_bookings[primary_key], 'group_id', None)

        # 1. Conflict Check across ALL target slots
        for target_slot in slots_to_book:
            slot_start = parse_time_to_minutes(target_slot)
            slot_end = slot_start + 60

            # Check Open Play conflict
            for s in self.open_play_sessions.values():
                if s.date == date and court_num <= s.court_count:
                    s_start = parse_time_to_minutes(s.start_time)
                    s_end = parse_time_to_minutes(s.end_time)
                    if max(slot_start, s_start) < min(slot_end, s_end):
                        return False, f"Cannot book slot ({target_slot}): Reserved for Open Play session '{s.title}' ({s.start_time} - {s.end_time})."

            # Check direct booking conflict (allow replacing slots that belong to the SAME group_id)
            target_key = (date, court, target_slot)
            if target_key in self.direct_bookings:
                existing_b = self.direct_bookings[target_key]
                if not existing_group or getattr(existing_b, 'group_id', None) != existing_group:
                    return False, f"Cannot book {duration_hours} hours: Slot at {target_slot} is already booked by '{existing_b.customer_name}'."

        # If updating, clean up any previous slots from the old group that are no longer in slots_to_book
        if existing_group:
            keys_to_remove = [k for k, b in self.direct_bookings.items() if getattr(b, 'group_id', None) == existing_group]
            for k in keys_to_remove:
                del self.direct_bookings[k]

        clean_name = customer_name.strip()
        clean_status = payment_status.lower()
        rent_paddle = bool(rent_paddle)
        try:
            paddle_count = int(paddle_count) if rent_paddle else 0
        except (ValueError, TypeError):
            paddle_count = 1 if rent_paddle else 0

        group_id = f"GRP-{date}-{court.replace(' ', '')}-{parse_time_to_minutes(time_slot)}"
        paddle_info = f" (+{paddle_count} Paddle rental)" if (rent_paddle and paddle_count > 0) else ""
        dur_info = f" for {duration_hours} hour(s) ({slots_to_book[0]} - {slots_to_book[-1]})" if duration_hours > 1 else ""

        # Save DirectBooking records for each consecutive slot
        for target_slot in slots_to_book:
            b_id = f"BK-{len(self.direct_bookings) + 1001}"
            b = DirectBooking(
                id=b_id, group_id=group_id, date=date, court=court, time_slot=target_slot,
                start_time_slot=time_slot, customer_name=clean_name, payment_status=clean_status,
                rent_paddle=rent_paddle, paddle_count=paddle_count, duration_hours=duration_hours
            )
            self.direct_bookings[(date, court, target_slot)] = b

        action = f"Saved direct booking for '{clean_name}' on {court} starting at {time_slot}{dur_info} ({clean_status.upper()}){paddle_info}"
        self.add_audit_log(action)
        return True, f"Booking for '{clean_name}' on {court} saved successfully ({duration_hours} hr{'s' if duration_hours > 1 else ''})!"


    def clear_direct_booking(self, date, court, time_slot):
        """Clears/cancels a direct booking for a specific slot and any linked multi-hour slots."""
        key = (date, court, time_slot)
        if key in self.direct_bookings:
            target_b = self.direct_bookings[key]
            group_id = getattr(target_b, 'group_id', None)

            if group_id:
                keys_to_clear = [k for k, b in self.direct_bookings.items() if getattr(b, 'group_id', None) == group_id]
            else:
                keys_to_clear = [key]

            for k in keys_to_clear:
                if k in self.direct_bookings:
                    del self.direct_bookings[k]

            self.add_audit_log(f"Cancelled direct booking for '{target_b.customer_name}' on {court} at {time_slot}")
            return True, f"Booking for '{target_b.customer_name}' on {court} cleared."
        return False, "No active booking found for this slot."

    def check_open_play_conflict(self, date, start_time, end_time, court_count):
        """
        Checks if creating a new Open Play session conflicts with any existing direct court bookings.
        Returns a descriptive error message if conflict found, otherwise None.
        """
        sess_start = parse_time_to_minutes(start_time)
        sess_end = parse_time_to_minutes(end_time)
        target_court_count = int(court_count)

        for (b_date, b_court, b_slot), b in self.direct_bookings.items():
            if b_date == date:
                c_num = parse_court_number(b_court)
                if c_num <= target_court_count:
                    slot_start = parse_time_to_minutes(b_slot)
                    slot_end = slot_start + 60

                    if max(sess_start, slot_start) < min(sess_end, slot_end):
                        return f"{b_court} already has a direct booking at {b_slot} for '{b.customer_name}' ({b.payment_status.upper()}) on {date} — creating this Open Play session will overlap."

        return None



# Global singleton database instance
db = MockDatabase()

