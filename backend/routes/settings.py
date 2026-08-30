from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings_view():
    return render_template(
        'settings.html',
        total_courts=db.total_courts,
        audit_logs=db.audit_logs
    )

@settings_bp.route('/api/settings/courts', methods=['POST'])
@login_required
def update_courts():
    data = request.get_json() or {}
    court_count = data.get('court_count')
    if not court_count:
        return jsonify({"success": False, "message": "Court count is required."}), 400
    
    success, new_count = db.set_total_courts(court_count, current_user.name)
    return jsonify({
        "success": True,
        "court_count": new_count,
        "message": f"Venue court capacity successfully updated to {new_count} courts."
    })
