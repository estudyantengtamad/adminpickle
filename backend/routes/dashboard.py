"""
Admin Dashboard Routes
Handles dashboard stats, system log displays, and quick admin action triggers.
"""

from flask import Blueprint, render_template, jsonify, request
try:
    from flask_login import login_required, current_user
except ImportError:
    def login_required(f): return f
    class DummyUser:
        name = "System Admin"
    current_user = DummyUser()
from backend.models.mock_db import db

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """Renders the main admin dashboard page with live metrics and system audit logs."""
    return render_template('dashboard.html', metrics=db.metrics, logs=db.system_logs)


@dashboard_bp.route('/api/action/manual_match', methods=['POST'])
@login_required
def manual_match():
    """Manually triggers court rotation sweep for all active Open Play sessions."""
    active_sessions = [s for s in db.get_open_play_sessions() if s.status == 'active']
    for s in active_sessions:
        db.run_rotation_engine(s.id)

    db.add_audit_log("Triggered Manual Open Play Rotation Sweep", current_user.name)
    return jsonify({"success": True, "message": "Manual Open Play Rotation sweep executed across active sessions."})


@dashboard_bp.route('/api/action/block_slot', methods=['POST'])
@login_required
def block_slot():
    """Emergency action: Blocks court slot A3 for maintenance."""
    db.add_audit_log("Emergency Blocked Court Slot A3", current_user.name)
    return jsonify({"success": True, "message": "Court slot A3 temporarily blocked for system maintenance."})


@dashboard_bp.route('/api/action/issue_warning', methods=['POST'])
@login_required
def issue_warning():
    """Broadcasts a conduct warning to platform users."""
    data = request.get_json() or {}
    msg = data.get('reason', 'General Conduct Warning')

    db.add_audit_log(f"Issued System Warning: {msg}", current_user.name)
    return jsonify({"success": True, "message": f"Global alert broadcasted: {msg}"})
