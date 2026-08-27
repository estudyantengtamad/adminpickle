"""
Open Play Controller Routes
Handles open play sessions, player waiting lists, payment approvals, court rotation, and match score recording.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
try:
    from flask_login import login_required, current_user
except ImportError:
    def login_required(f): return f
    class DummyUser:
        name = "System Admin"
    current_user = DummyUser()
from backend.models.mock_db import db

open_play_bp = Blueprint('open_play', __name__)


# ---------------------------------------------------------------------------
#  Helper Functions
# ---------------------------------------------------------------------------

def get_input(key, default=''):
    """Grabs a parameter value from either JSON payload or HTML form submit."""
    if request.is_json:
        return (request.get_json() or {}).get(key, default)
    return request.form.get(key, default)


def json_ok(message, **extras):
    """Sends a successful JSON response back to the client."""
    return jsonify({"success": True, "message": message, **extras})


def json_fail(message, status=400):
    """Sends an error JSON response back to the client."""
    return jsonify({"success": False, "message": message}), status


# ---------------------------------------------------------------------------
#  1. Sessions Hub (List All Sessions)
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play')
@login_required
def open_play_view():
    """Main Open Play hub page — shows summary counters and lists all sessions."""
    sessions = db.get_open_play_sessions()

    active_count = sum(1 for s in sessions if s.status == "active")
    upcoming_count = sum(1 for s in sessions if s.status == "upcoming")
    total_enrolled = sum(len(db.session_participants.get(s.id, [])) for s in sessions)
    pending_payments = sum(
        1 for parts in db.session_participants.values()
        for p in parts if p.payment_status == "pending"
    )

    return render_template(
        'open_play.html',
        sessions=sessions,
        players=db.players,
        active_count=active_count,
        upcoming_count=upcoming_count,
        total_enrolled=total_enrolled,
        pending_payments=pending_payments
    )


# ---------------------------------------------------------------------------
#  2. Create a New Session
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play/sessions/create', methods=['POST'])
@login_required
def create_session():
    """Creates a new Open Play session with title, date, times, court count, and max capacity."""
    title       = get_input('title', '').strip()
    date        = get_input('date', '').strip()
    start_time  = get_input('start_time', '').strip()
    end_time    = get_input('end_time', '').strip()
    court_count = int(get_input('court_count', 4))
    max_players = int(get_input('max_players', 16))

    # Date and times are required
    if not date or not start_time or not end_time:
        if request.is_json:
            return json_fail("Date, Start Time, and End Time are required.")
        flash("Date, Start Time, and End Time are required.", "danger")
        return redirect(url_for('open_play.open_play_view'))

    # Check for direct booking conflicts on courts during this time range
    conflict_msg = db.check_open_play_conflict(date, start_time, end_time, court_count)
    if conflict_msg:
        if request.is_json:
            return json_fail(conflict_msg)
        flash(conflict_msg, "danger")
        return redirect(url_for('open_play.open_play_view'))

    session = db.create_open_play_session(
        title=title or f"Open Play - {date}",
        date=date,
        start_time=start_time,
        end_time=end_time,
        court_count=court_count,
        max_players=max_players
    )

    if request.is_json:
        return json_ok(f"Session #{session.id} created!", session=session.to_dict())

    flash(f"Session #{session.id} ('{session.title}') created!", "success")
    return redirect(url_for('open_play.session_detail', session_id=session.id))


# ---------------------------------------------------------------------------
#  3. Session Command Center (Session Details & Waiting List)
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play/sessions/<session_id>')
@login_required
def session_detail(session_id):
    """Command center for one session — shows waiting list, payment receipts, courts, and match history."""
    session = db.get_open_play_session(session_id)
    if not session:
        flash("Session not found.", "danger")
        return redirect(url_for('open_play.open_play_view'))

    participants = db.session_participants.get(session_id, [])
    games = db.session_games.get(session_id, [])

    # Group players and games for easy template rendering
    pending_list    = [p for p in participants if p.payment_status in ("pending", "expired")]
    confirmed_list  = [p for p in participants if p.payment_status == "paid"]
    active_games     = [g for g in games if g.status == "in_progress"]
    completed_games  = [g for g in games if g.status == "completed"]

    return render_template(
        'open_play_detail.html',
        session=session,
        participants=participants,
        pending_list=pending_list,
        confirmed_list=confirmed_list,
        active_games=active_games,
        completed_games=completed_games,
        all_players=db.players
    )


# ---------------------------------------------------------------------------
#  4. Register Player to Session Waiting List
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play/sessions/<session_id>/add_player', methods=['POST'])
@login_required
def add_player(session_id):
    """Enrolls a registered player into the session's waiting list with a 6-hour payment window."""
    player_id      = get_input('player_id')
    payment_method = get_input('payment_method', 'gcash')
    payment_status = get_input('payment_status', 'pending')
    receipt        = get_input('receipt', None)

    if not player_id:
        if request.is_json:
            return json_fail("Player ID is required.")
        flash("Player selection is required.", "danger")
        return redirect(url_for('open_play.session_detail', session_id=session_id))

    participant, msg = db.add_session_participant(
        session_id=session_id,
        player_id=player_id,
        payment_method=payment_method,
        payment_status=payment_status,
        receipt=receipt
    )

    if not participant:
        if request.is_json:
            return json_fail(msg)
        flash(msg, "danger")
        return redirect(url_for('open_play.session_detail', session_id=session_id))

    if request.is_json:
        return json_ok(msg, participant=participant.to_dict())

    flash(msg, "success")
    return redirect(url_for('open_play.session_detail', session_id=session_id))


# ---------------------------------------------------------------------------
#  5. Payment Approvals & Receipts
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play/participants/<participant_id>/confirm', methods=['POST'])
@login_required
def confirm_payment(participant_id):
    """Admin approves a player's payment. Only paid players enter the court rotation pool."""
    success, msg = db.confirm_participant_payment(participant_id)
    if success:
        return json_ok(msg)
    return json_fail(msg)


@open_play_bp.route('/open-play/participants/<participant_id>/receipt', methods=['POST'])
@login_required
def upload_receipt(participant_id):
    """Attaches a receipt screenshot filename (e.g. GCash proof) to a player's registration."""
    data = request.get_json() or {}
    receipt_path = data.get('receipt', 'receipt_mock_payment.png')

    success, msg = db.upload_participant_receipt(participant_id, receipt_path)
    if success:
        return json_ok(msg, receipt=receipt_path)
    return json_fail(msg)


# ---------------------------------------------------------------------------
#  6. Session Status & Rotation Controls
# ---------------------------------------------------------------------------

@open_play_bp.route('/open-play/sessions/<session_id>/status', methods=['POST'])
@login_required
def update_status(session_id):
    """
    Changes session status (upcoming -> active -> completed).
    Starting a session ('active') automatically runs the rotation engine to seat players.
    """
    data = request.get_json() or {}
    new_status = data.get('status')

    if new_status not in ('upcoming', 'active', 'completed'):
        return json_fail("Invalid status. Use: upcoming, active, or completed.")

    success = db.update_session_status(session_id, new_status)
    if success:
        return json_ok(f"Session #{session_id} is now {new_status.upper()}!", status=new_status)
    return json_fail("Session update failed.")


@open_play_bp.route('/open-play/games/<game_id>/finish', methods=['POST'])
@login_required
def finish_game(game_id):
    """
    Records final scores for a match and marks it completed.
    Optionally auto-seats the next 4 waiting players if auto_rotate is True.
    """
    data = request.get_json() or {}
    score_a = data.get('score_a', 11)
    score_b = data.get('score_b', 9)
    auto_rotate = data.get('auto_rotate', True)

    success, msg, new_games = db.finish_game(game_id, score_a, score_b, auto_rotate=auto_rotate)
    if success:
        return json_ok(msg, new_games=[g.to_dict() for g in new_games])
    return json_fail(msg)


@open_play_bp.route('/open-play/sessions/<session_id>/trigger_rotation', methods=['POST'])
@login_required
def trigger_rotation(session_id):
    """Manually triggers the rotation engine for a specific court or all open courts."""
    data = request.get_json() or {}
    court_number = data.get('court_number', None)

    new_games = db.run_rotation_engine(session_id, target_court=court_number)

    if new_games:
        return json_ok(
            f"Rotation created {len(new_games)} new match(es)!",
            new_games=[g.to_dict() for g in new_games]
        )

    return json_ok(
        "No matches created — either all courts are busy or not enough waiting players (need 4).",
        new_games=[]
    )
