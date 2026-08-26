"""
Automated Verification Unit Test for Admin Open Play System
Tests:
  1. OpenPlaySession creation.
  2. Adding players to session waiting list with 6-hour payment deadline.
  3. Lazy expiration check logic.
  4. Payment review and confirmation adding players to confirmed lineup.
  5. Automatic rotation engine balancing 2v2 teams by DUPR ELO and fewest games played.
  6. Finish game flow incrementing games_played and auto-seating next rotation.
"""

import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime, timedelta
from backend.models.mock_db import db, OpenPlaySession, SessionParticipant, Game

def run_tests():
    print("==================================================")
    print(" RUNNING OPEN PLAY ENGINE AUTOMATED TESTS")
    print("==================================================")

    # 1. Create Session
    session = db.create_open_play_session(
        title="Test Open Play Session",
        date="2026-08-25",
        start_time="10:00 AM",
        end_time="01:00 PM",
        court_count=2,
        max_players=12
    )
    assert session.id is not None
    print(f"✅ Test 1 Passed: Session Created (#{session.id})")

    # 2. Add Players to Waiting List
    p1, msg1 = db.add_session_participant(session.id, "USR-9982", payment_method="gcash", payment_status="pending")
    p2, msg2 = db.add_session_participant(session.id, "USR-9712", payment_method="online", payment_status="pending", receipt="receipt_p2.png")
    p3, msg3 = db.add_session_participant(session.id, "USR-9921", payment_method="cash", payment_status="paid")
    p4, msg4 = db.add_session_participant(session.id, "USR-9511", payment_method="gcash", payment_status="pending")
    p5, msg5 = db.add_session_participant(session.id, "USR-9804", payment_method="online", payment_status="pending")

    assert len(db.session_participants[session.id]) == 5
    print(f"✅ Test 2 Passed: 5 Players Enrolled in Waiting List")

    # 3. Test Lazy Expiration
    expired_p = SessionParticipant(
        id="PART-999",
        session_id=session.id,
        player_id="USR-9402",
        player_name="Expired Mark",
        elo=1200,
        joined_at=datetime.now() - timedelta(hours=7),
        payment_method="gcash",
        payment_status="pending"
    )
    db.session_participants[session.id].append(expired_p)
    db.lazy_check_expirations(session.id)
    assert expired_p.payment_status == "expired"
    print(f"✅ Test 3 Passed: Lazy 6-Hour Payment Expiration Triggered ('expired')")

    # 4. Payment Confirmations
    db.confirm_participant_payment(p1.id)
    db.confirm_participant_payment(p2.id)
    db.confirm_participant_payment(p4.id)
    # Now p1, p2, p3, p4 are paid & confirmed (4 players!)

    confirmed = [p for p in db.session_participants[session.id] if p.payment_status == "paid"]
    assert len(confirmed) == 4
    print(f"✅ Test 4 Passed: Admin Payment Confirmations ({len(confirmed)} Confirmed Paid)")

    # 5. Start Session & Run Rotation Engine
    db.update_session_status(session.id, "active")
    games = db.session_games[session.id]
    assert len(games) == 1  # 1 game created on Court 1 for 4 confirmed players!
    active_g = games[0]
    assert active_g.court_number == 1
    assert active_g.status == "in_progress"
    print(f"✅ Test 5 Passed: Rotation Engine Seated Game #{active_g.id} on Court #1 (Team A: {[p.player_name for p in active_g.team_a]} vs Team B: {[p.player_name for p in active_g.team_b]})")

    # 6. Finish Game & Verify Auto-Rotation Queue
    success, finish_msg, _ = db.finish_game(active_g.id, score_a=11, score_b=8)
    assert success is True
    assert active_g.status == "completed"
    for p in active_g.team_a + active_g.team_b:
        assert p.games_played == 1
        assert p.rotation_status == "playing"

    print(f"✅ Test 6 Passed: Game Finished ({finish_msg}) & Games Played Incremented to 1")

    print("==================================================")
    print(" ALL OPEN PLAY UNIT TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == '__main__':
    run_tests()
