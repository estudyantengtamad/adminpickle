from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

matchmaking_bp = Blueprint('matchmaking', __name__)

@matchmaking_bp.route('/matchmaking')
@login_required
def matchmaking_view():
    return render_template(
        'matchmaking.html',
        queue=db.matchmaking_queue,
        params=db.matchmaking_params
    )

@matchmaking_bp.route('/api/matchmaking/save_params', methods=['POST'])
@login_required
def save_params():
    data = request.get_json() or {}
    db.matchmaking_params['max_skill_gap'] = int(data.get('max_skill_gap', 50))
    db.matchmaking_params['density_multiplier'] = float(data.get('density_multiplier', 1.25))
    db.matchmaking_params['smart_matchmaking'] = bool(data.get('smart_matchmaking', True))

    db.add_audit_log(
        f"Updated Matchmaking Params: Skill Gap ±{db.matchmaking_params['max_skill_gap']}, Multiplier {db.matchmaking_params['density_multiplier']}x",
        current_user.name
    )
    return jsonify({"success": True, "message": "Matchmaking calibration parameters saved successfully!"})

@matchmaking_bp.route('/api/matchmaking/force_search', methods=['POST'])
@login_required
def force_search():
    db.add_audit_log("Triggered Forced Matchmaking Search Sweep", current_user.name)
    return jsonify({"success": True, "message": "Forced match search executed across active queue pools."})

@matchmaking_bp.route('/api/matchmaking/reset', methods=['POST'])
@login_required
def emergency_reset():
    db.add_audit_log("EMERGENCY RESET triggered on Matchmaking Engine", current_user.name)
    return jsonify({"success": True, "message": "Matchmaking engine reset. All queued pairings re-evaluated."})
