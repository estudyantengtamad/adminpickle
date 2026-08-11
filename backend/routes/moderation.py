from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

moderation_bp = Blueprint('moderation', __name__)

@moderation_bp.route('/moderation')
@login_required
def moderation_view():
    return render_template(
        'moderation.html',
        reports=db.reported_players,
        chat_logs=db.chat_logs,
        tournaments=db.tournaments
    )

@moderation_bp.route('/api/moderation/action', methods=['POST'])
@login_required
def report_action():
    data = request.get_json() or {}
    report_id = data.get('report_id')
    action = data.get('action')  # warning, mute, ban, dismiss

    report = next((r for r in db.reported_players if r['id'] == report_id), None)
    if report:
        if action == 'warning':
            report['status'] = 'Warning Issued'
            db.add_audit_log(f"Issued toxic behavior warning to player {report['player_name']}", current_user.name)
            return jsonify({"success": True, "status": "Warning Issued", "message": f"Warning sent to {report['player_name']}."})
        elif action == 'mute':
            report['status'] = 'Chat Muted (48h)'
            db.add_audit_log(f"Muted chat privileges for player {report['player_name']}", current_user.name)
            return jsonify({"success": True, "status": "Chat Muted (48h)", "message": f"Muted chat for {report['player_name']}."})
        elif action == 'ban':
            report['status'] = 'Account Banned'
            db.update_player_status(report['player_id'], 'Banned')
            db.add_audit_log(f"Banned account for reported player {report['player_name']}", current_user.name)
            return jsonify({"success": True, "status": "Account Banned", "message": f"Account {report['player_name']} banned."})
        elif action == 'dismiss':
            report['status'] = 'Resolved (Dismissed)'
            db.add_audit_log(f"Dismissed moderation report {report_id}", current_user.name)
            return jsonify({"success": True, "status": "Resolved (Dismissed)", "message": f"Report {report_id} dismissed."})

    return jsonify({"success": False, "message": "Report not found."}), 404

@moderation_bp.route('/api/moderation/create_event', methods=['POST'])
@login_required
def create_event():
    data = request.get_json() or {}
    title = data.get('title', 'New Tournament')
    venue = data.get('venue', 'Current Paddle Club')
    date_str = data.get('date', 'Dec 15, 2026')
    tag = data.get('tag', 'TOURNAMENT')

    new_evt = {
        "id": f"EVT-{104 + len(db.tournaments)}",
        "title": title,
        "venue": venue,
        "date": date_str,
        "status": "Published",
        "tag": tag
    }
    db.tournaments.insert(0, new_evt)
    db.add_audit_log(f"Created new event posting: '{title}' at {venue}", current_user.name)
    return jsonify({"success": True, "event": new_evt, "message": f"Event '{title}' posted successfully."})
