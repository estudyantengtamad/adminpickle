from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class AdminUser(UserMixin):
    def __init__(self, id, username, name, role, avatar_url, password_hash):
        self.id = id
        self.username = username
        self.name = name
        self.role = role
        self.avatar_url = avatar_url
        self.password_hash = password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class MockDatabase:
    def __init__(self):
        # Admin account
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

        # Executive Metrics
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

        # System Logs
        self.system_logs = [
            {"id": "LOG-9081", "timestamp": "Today, 21:44:12", "action": "Automated RECIPE parameter adjustment applied", "admin": "System (Auto)", "status": "Completed"},
            {"id": "LOG-9080", "timestamp": "Today, 20:15:00", "action": "Manual match forced: #USR-9982 vs #USR-9121", "admin": "Karl Alegrado", "status": "Active"},
            {"id": "LOG-9079", "timestamp": "Today, 18:30:22", "action": "Court A4 at Downtown Paddle Club set to Maintenance", "admin": "Karl Alegrado", "status": "Active"},
            {"id": "LOG-9078", "timestamp": "Today, 15:10:05", "action": "Penalty issued for User #USR-8812 (Toxic chat report)", "admin": "Sarah Jenkins", "status": "Verified"},
            {"id": "LOG-9077", "timestamp": "Yesterday, 22:00:19", "action": "System backup completed (24.8 GB)", "admin": "System (Auto)", "status": "Completed"},
        ]

        # Player Management Data
        self.players = [
            {
                "id": "USR-9982",
                "name": "Sarah Jenkins",
                "elo": 1942,
                "tier": "Diamond",
                "win_rate": "74.2%",
                "status": "Active",
                "matches": 312,
                "reports": 0,
                "notes": "Top tier competitive player. Consistent league attendee."
            },
            {
                "id": "USR-9921",
                "name": "Karl Alegrado",
                "elo": 1835,
                "tier": "Gold",
                "win_rate": "68.5%",
                "status": "Active",
                "matches": 240,
                "reports": 0,
                "notes": "Platform developer & tournament organizer."
            },
            {
                "id": "USR-9804",
                "name": "Darnell Castro",
                "elo": 1690,
                "tier": "Platinum",
                "win_rate": "62.1%",
                "status": "Active",
                "matches": 189,
                "reports": 1,
                "notes": "Regular evening queue player."
            },
            {
                "id": "USR-9712",
                "name": "Grace Santos",
                "elo": 2010,
                "tier": "Diamond",
                "win_rate": "81.0%",
                "status": "Active",
                "matches": 450,
                "reports": 0,
                "notes": "National pickleball championship contender."
            },
            {
                "id": "USR-9650",
                "name": "Jaye Antonio",
                "elo": 1420,
                "tier": "Silver",
                "win_rate": "51.4%",
                "status": "Frozen",
                "matches": 95,
                "reports": 3,
                "notes": "Temporary cooldown pending identity verification."
            },
            {
                "id": "USR-9511",
                "name": "Vaughn Hancock",
                "elo": 1550,
                "tier": "Gold",
                "win_rate": "55.8%",
                "status": "Active",
                "matches": 130,
                "reports": 0,
                "notes": "Casual weekend player."
            },
            {
                "id": "USR-9402",
                "name": "Mark Rivera",
                "elo": 1210,
                "tier": "Bronze",
                "win_rate": "42.0%",
                "status": "Active",
                "matches": 60,
                "reports": 0,
                "notes": "New member, beginner league."
            },
            {
                "id": "USR-9311",
                "name": "Mabelle Kimball",
                "elo": 1780,
                "tier": "Platinum",
                "win_rate": "69.4%",
                "status": "Banned",
                "matches": 210,
                "reports": 8,
                "notes": "Banned for repeated unsportsmanlike conduct in ranked ladder."
            }
        ]

        # Matchmaking Configurator Data
        self.matchmaking_queue = [
            {"p1": "USR-9982 (Sarah J.)", "p2": "USR-9712 (Grace S.)", "mode": "Ranked Match", "wait": "12s", "status": "Matched"},
            {"p1": "USR-9921 (Karl A.)", "p2": "USR-9511 (Vaughn H.)", "mode": "Public Casual", "wait": "45s", "status": "In Queue"},
            {"p1": "USR-9804 (Darnell C.)", "p2": "USR-9311 (Mabelle K.)", "mode": "Ranked Match", "wait": "78s", "status": "Calibrating"},
            {"p1": "USR-9402 (Mark R.)", "p2": "USR-9650 (Jaye A.)", "mode": "Public Casual", "wait": "28s", "status": "In Queue"},
            {"p1": "USR-9110 (Elmo V.)", "p2": "USR-9004 (Tina L.)", "mode": "Tournament Queue", "wait": "95s", "status": "Matched"}
        ]

        self.matchmaking_params = {
            "max_skill_gap": 50,
            "density_multiplier": 1.25,
            "smart_matchmaking": True
        }

        # Venue & Court Manager Data
        self.venues = [
            {"id": 1, "name": "Current Paddle Club", "courts": 6, "rate": "120 pts/hr", "active": True},
            {"id": 2, "name": "Quantum Courts", "courts": 8, "rate": "150 pts/hr", "active": False},
            {"id": 3, "name": "Riverside Arena", "courts": 4, "rate": "100 pts/hr", "active": False},
            {"id": 4, "name": "Harbor Sports Center", "courts": 5, "rate": "130 pts/hr", "active": False}
        ]

        self.time_slots = ["08:00 AM", "10:00 AM", "12:00 PM", "02:00 PM", "04:00 PM", "06:00 PM"]
        self.courts = ["Court 1", "Court 2", "Court 3", "Court 4", "Court 5"]

        # Court Status Grid: slot -> court -> status
        # Statuses: Available, Booked, Maintenance, Reserved
        self.court_grid = {
            "08:00 AM": {"Court 1": "Available", "Court 2": "Booked", "Court 3": "Maintenance", "Court 4": "Available", "Court 5": "Available"},
            "10:00 AM": {"Court 1": "Booked", "Court 2": "Booked", "Court 3": "Maintenance", "Court 4": "Reserved", "Court 5": "Available"},
            "12:00 PM": {"Court 1": "Available", "Court 2": "Available", "Court 3": "Booked", "Court 4": "Available", "Court 5": "Booked"},
            "02:00 PM": {"Court 1": "Available", "Court 2": "Reserved", "Court 3": "Available", "Court 4": "Available", "Court 5": "Available"},
            "04:00 PM": {"Court 1": "Booked", "Court 2": "Available", "Court 3": "Maintenance", "Court 4": "Available", "Court 5": "Available"},
            "06:00 PM": {"Court 1": "Available", "Court 2": "Booked", "Court 3": "Booked", "Court 4": "Available", "Court 5": "Available"},
        }

        # Moderation Hub Data
        self.reported_players = [
            {
                "id": "REP-801",
                "player_id": "USR-9311",
                "player_name": "Mabelle Kimball",
                "reporter": "USR-9982",
                "reason": "Toxic language in lobby chat & stall tactics",
                "severity": "High",
                "date": "Today, 19:40",
                "status": "Pending Action"
            },
            {
                "id": "REP-802",
                "player_id": "USR-9804",
                "player_name": "Darnell Castro",
                "reporter": "USR-9402",
                "reason": "Unannounced match rage quit",
                "severity": "Medium",
                "date": "Yesterday, 21:15",
                "status": "Under Review"
            },
            {
                "id": "REP-803",
                "player_id": "USR-9650",
                "player_name": "Jaye Antonio",
                "reporter": "USR-9712",
                "reason": "Suspicious disconnect rate during ranked playoff",
                "severity": "Low",
                "date": "Aug 10, 16:00",
                "status": "Under Review"
            }
        ]

        self.chat_logs = {
            "USR-9311": [
                {"time": "19:35", "sender": "Mabelle Kimball", "text": "Are you guys serious? Learn how to serve properly.", "toxic": True},
                {"time": "19:36", "sender": "Sarah Jenkins", "text": "Hey keep it friendly please.", "toxic": False},
                {"time": "19:37", "sender": "Mabelle Kimball", "text": "Whatever, I'm just going to idle and let you lose.", "toxic": True}
            ],
            "USR-9804": [
                {"time": "21:10", "sender": "Darnell Castro", "text": "Lag spikes again, GG I'm out.", "toxic": False}
            ]
        }

        self.tournaments = [
            {"id": "EVT-101", "title": "Autumn Open 2026", "venue": "Current Paddle Club", "date": "Nov 15, 2026", "status": "Published", "tag": "TOURNAMENT"},
            {"id": "EVT-102", "title": "Weekend Warmup", "venue": "Quantum Courts", "date": "Nov 22, 2026", "status": "Draft", "tag": "MONTHLY DUPR"},
            {"id": "EVT-103", "title": "Junior Showcase", "venue": "Harbor Sports Center", "date": "Dec 01, 2026", "status": "Published", "tag": "ACADEMY"}
        ]

        # System Settings RECIPE Framework Sliders (0 - 100)
        self.recipe_settings = {
            "recognition": 85,
            "engagement": 72,
            "competition": 90,
            "improvement": 68,
            "play": 95,
            "experience": 88
        }

        self.audit_logs = [
            {"timestamp": "Friday, 21:47:19", "admin": "Karl Alegrado", "action": "Updated RECIPE Slider Improvement to 68 PTS", "ip": "192.168.1.45"},
            {"timestamp": "Friday, 20:41:02", "admin": "Karl Alegrado", "action": "Issued Toxic Warning to User #USR-9311", "ip": "192.168.1.45"},
            {"timestamp": "Today, 17:15:33", "admin": "Sarah Jenkins", "action": "Blocked Court A3 at Downtown Paddle Club for maintenance", "ip": "10.0.0.12"},
            {"timestamp": "Thursday, 14:02:11", "admin": "Karl Alegrado", "action": "Updated manual credit +100 PTS for User #USR-9982", "ip": "192.168.1.45"},
            {"timestamp": "Wednesday, 11:20:45", "admin": "System Tech", "action": "Automated system update & security patch v3.4.1", "ip": "127.0.0.1"}
        ]

    def get_user_by_id(self, user_id):
        return self.users.get(str(user_id))

    def get_user_by_username(self, username):
        for user in self.users.values():
            if user.username == username:
                return user
        return None

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

# Global singleton database instance
db = MockDatabase()
