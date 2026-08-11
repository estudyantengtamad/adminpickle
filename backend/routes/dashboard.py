from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    return render_template('dashboard.html', metrics=db.metrics, logs=db.system_logs)

@dashboard_bp.route('/api/action/manual_match', methods=['POST'])
@login_required
def manual_match():
    db.add_audit_log("Triggered Manual Matchmaking sweep", current_user.name)
    return jsonify({"success": True, "message": "Manual Matchmaking sweep initialized across all queue regions."})

@dashboard_bp.route('/api/action/block_slot', methods=['POST'])
@login_required
def block_slot():
    db.add_audit_log("Emergency Blocked Court Slot A3", current_user.name)
    return jsonify({"success": True, "message": "Court slot A3 temporarily blocked for system maintenance."})

@dashboard_bp.route('/api/action/issue_warning', methods=['POST'])
@login_required
def issue_warning():
    data = request.get_json() or {}
    msg = data.get('reason', 'General Conduct Warning')
    db.add_audit_log(f"Issued System Warning: {msg}", current_user.name)
    return jsonify({"success": True, "message": f"Global alert broadcasted: {msg}"})
