from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings')
@login_required
def settings_view():
    return render_template(
        'settings.html',
        recipe=db.recipe_settings,
        audit_logs=db.audit_logs
    )

@settings_bp.route('/api/settings/save', methods=['POST'])
@login_required
def save_settings():
    data = request.get_json() or {}

    db.recipe_settings['recognition'] = int(data.get('recognition', db.recipe_settings['recognition']))
    db.recipe_settings['engagement'] = int(data.get('engagement', db.recipe_settings['engagement']))
    db.recipe_settings['competition'] = int(data.get('competition', db.recipe_settings['competition']))
    db.recipe_settings['improvement'] = int(data.get('improvement', db.recipe_settings['improvement']))
    db.recipe_settings['play'] = int(data.get('play', db.recipe_settings['play']))
    db.recipe_settings['experience'] = int(data.get('experience', db.recipe_settings['experience']))

    summary = (
        f"Saved RECIPE Framework Sliders: R:{db.recipe_settings['recognition']} "
        f"E:{db.recipe_settings['engagement']} C:{db.recipe_settings['competition']} "
        f"I:{db.recipe_settings['improvement']} P:{db.recipe_settings['play']} Ex:{db.recipe_settings['experience']}"
    )
    db.add_audit_log(summary, current_user.name)

    return jsonify({"success": True, "message": "Platform RECIPE parameters updated successfully and audit log generated."})
