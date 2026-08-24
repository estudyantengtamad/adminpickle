"""
PickleLegends Admin Platform - Open Play Controller Routes
Job: Manages HTTP requests & API endpoints for Open Play Sessions, Waiting Lists,
Receipt/Payment Verification, and the Fair Automatic Court Rotation Engine.
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash
try:
    from flask_login import login_required, current_user
except ImportError:
    def login_required(f): return f
    current_user = None
from backend.models.mock_db import db

open_play_bp = Blueprint('open_play', __name__)

# ==============================================================================
# 1. ADMIN DASHBOARD & SESSIONS HUB
# ==============================================================================

@open_play_bp.route('/open-play')
@login_required
def open_play_view():
    """
    Job: Render the main Admin Open Play Sessions Hub page.
    Displays upcoming, active, and completed sessions, summary statistics,
    and session creation form.
    """
    sessions = db.get_open_play_sessions()
    
    # Calculate executive summary metrics for open play
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


@open_play_bp.route('/open-play/sessions/create', methods=['POST'])
@login_required
def create_session():
    """
    Feature #1: Create an Open Play Session.
    Job: Processes form submit / JSON request to create a new session.
    Params: title, date, start_time, end_time, court_count, max_players.
    """
    if request.is_json:
        data = request.get_json() or {}
        title = data.get('title', '').strip()
        date = data.get('date', '').strip()
        start_time = data.get('start_time', '').strip()
        end_time = data.get('end_time', '').strip()
        court_count = int(data.get('court_count', 4))
        max_players = int(data.get('max_players', 16))
    else:
        title = request.form.get('title', '').strip()
        date = request.form.get('date', '').strip()
        start_time = request.form.get('start_time', '').strip()
        end_time = request.form.get('end_time', '').strip()
        court_count = int(request.form.get('court_count', 4))
        max_players = int(request.form.get('max_players', 16))

    if not date or not start_time or not end_time:
        if request.is_json:
            return jsonify({"success": False, "message": "Date, Start Time, and End Time are required."}), 400
        flash("Date, Start Time, and End Time are required.", "danger")
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
        return jsonify({
            "success": True, 
            "message": f"Open Play Session #{session.id} created successfully!",
            "session": session.to_dict()
        })
    
    flash(f"Open Play Session #{session.id} ('{session.title}') created successfully!", "success")
    return redirect(url_for('open_play.session_detail', session_id=session.id))


# ==============================================================================
# 2. SESSION COMMAND CENTER & WAITING LIST MANAGEMENT
# ==============================================================================

@open_play_bp.route('/open-play/sessions/<session_id>')
@login_required
def session_detail(session_id):
    """
    Feature #5: Per-Session Admin Command Center View.
    Job: Displays session details, waiting list (with payment statuses & 6-hr countdowns),
    confirmed player list, and live court matrix with rotation queue.
    """
    session = db.get_open_play_session(session_id)
    if not session:
        flash("Open Play Session not found.", "danger")
        return redirect(url_for('open_play.open_play_view'))

    participants = db.session_participants.get(session_id, [])
    games = db.session_games.get(session_id, [])
    
    # Split participants into waiting list vs confirmed
    pending_list = [p for p in participants if p.payment_status in ["pending", "expired"]]
    confirmed_list = [p for p in participants if p.payment_status == "paid"]
    active_games = [g for g in games if g.status == "in_progress"]
    completed_games = [g for g in games if g.status == "completed"]

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


@open_play_bp.route('/open-play/sessions/<session_id>/add_player', methods=['POST'])
@login_required
def add_player(session_id):
    """
    Feature #2: Add Registered Player to Waiting List.
    Job: Enrolls a player into a session's waiting list with payment details.
    """
    data = request.get_json() if request.is_json else request.form
    player_id = data.get('player_id')
    payment_method = data.get('payment_method', 'gcash')
    payment_status = data.get('payment_status', 'pending')
    receipt = data.get('receipt', None)

    if not player_id:
        if request.is_json:
            return jsonify({"success": False, "message": "Player ID is required."}), 400
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
            return jsonify({"success": False, "message": msg}), 400
        flash(msg, "danger")
        return redirect(url_for('open_play.session_detail', session_id=session_id))

    if request.is_json:
        return jsonify({"success": True, "message": msg, "participant": participant.to_dict()})

    flash(msg, "success")
    return redirect(url_for('open_play.session_detail', session_id=session_id))


# ==============================================================================
# 3. PAYMENT REVIEW FLOW & CONFIRMATION
# ==============================================================================

@open_play_bp.route('/open-play/participants/<participant_id>/confirm', methods=['POST'])
@login_required
def confirm_payment(participant_id):
    """
    Feature #3: Payment Confirmation Action.
    Job: Admin manually approves payment. Marks status 'paid', sets confirmed_at.
    Only once payment_status is 'paid' does player enter confirmed rotation pool!
    """
    success, msg = db.confirm_participant_payment(participant_id)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 400


@open_play_bp.route('/open-play/participants/<participant_id>/receipt', methods=['POST'])
@login_required
def upload_receipt(participant_id):
    """
    Feature #3: Receipt Upload Trigger.
    Job: Attaches mock receipt image reference string to participant entry.
    Visual indicator (green receipt icon) will appear next to name in admin list.
    """
    data = request.get_json() or {}
    receipt_path = data.get('receipt', 'receipt_mock_payment.png')
    
    success, msg = db.upload_participant_receipt(participant_id, receipt_path)
    if success:
        return jsonify({"success": True, "message": msg, "receipt": receipt_path})
    return jsonify({"success": False, "message": msg}), 400


# ==============================================================================
# 4. ROTATION ENGINE & MATCH CONTROLS
# ==============================================================================

@open_play_bp.route('/open-play/sessions/<session_id>/status', methods=['POST'])
@login_required
def update_status(session_id):
    """
    Feature #4: Session Lifecycle State Switch.
    Job: Switches status ('upcoming' -> 'active' -> 'completed').
    Starting a session ('active') automatically triggers the rotation engine!
    """
    data = request.get_json() or {}
    new_status = data.get('status')
    
    if new_status not in ['upcoming', 'active', 'completed']:
        return jsonify({"success": False, "message": "Invalid status value."}), 400

    success = db.update_session_status(session_id, new_status)
    if success:
        return jsonify({
            "success": True, 
            "message": f"Session #{session_id} is now {new_status.upper()}!",
            "status": new_status
        })
    return jsonify({"success": False, "message": "Session update failed."}), 400


@open_play_bp.route('/open-play/games/<game_id>/finish', methods=['POST'])
@login_required
def finish_game(game_id):
    """
    Feature #4: Finish Game & Execute Auto-Rotation.
    Job: Admin marks court game finished. Increments games_played by 1 for players,
    returns them to rotation queue, and automatically seats next 4 players!
    """
    data = request.get_json() or {}
    score_a = data.get('score_a', 11)
    score_b = data.get('score_b', 9)

    success, msg, new_games = db.finish_game(game_id, score_a, score_b)
    if success:
        return jsonify({
            "success": True, 
            "message": msg,
            "new_games": [g.to_dict() for g in new_games]
        })
    return jsonify({"success": False, "message": msg}), 400


@open_play_bp.route('/open-play/sessions/<session_id>/trigger_rotation', methods=['POST'])
@login_required
def trigger_rotation(session_id):
    """
    Feature #4: Manual Rotation Engine Sweep.
    Job: Forces rotation engine check to pair waiting confirmed players onto free courts.
    """
    new_games = db.run_rotation_engine(session_id)
    if new_games:
        return jsonify({
            "success": True, 
            "message": f"Rotation engine generated {len(new_games)} new match(es)!",
            "new_games": [g.to_dict() for g in new_games]
        })
    return jsonify({
        "success": True, 
        "message": "Rotation sweep completed. No open courts or not enough waiting confirmed players (min 4).",
        "new_games": []
    })
