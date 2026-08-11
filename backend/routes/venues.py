from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from backend.models.mock_db import db

venues_bp = Blueprint('venues', __name__)

@venues_bp.route('/venues')
@login_required
def venues_view():
    return render_template(
        'venues.html',
        venues=db.venues,
        time_slots=db.time_slots,
        courts=db.courts,
        court_grid=db.court_grid
    )

@venues_bp.route('/api/venues/toggle_slot', methods=['POST'])
@login_required
def toggle_slot():
    data = request.get_json() or {}
    time_slot = data.get('time_slot')
    court = data.get('court')

    new_status = db.toggle_court_slot(time_slot, court)
    if new_status:
        db.add_audit_log(f"Updated {court} slot at {time_slot} to '{new_status}'", current_user.name)
        return jsonify({"success": True, "new_status": new_status, "message": f"{court} at {time_slot} is now {new_status}."})
    return jsonify({"success": False, "message": "Invalid slot parameters."}), 400

@venues_bp.route('/api/venues/add_slot', methods=['POST'])
@login_required
def add_slot():
    data = request.get_json() or {}
    new_time = data.get('time', '08:00 PM')
    if new_time not in db.time_slots:
        db.time_slots.append(new_time)
        db.court_grid[new_time] = {c: "Available" for c in db.courts}
        db.add_audit_log(f"Added new court schedule time slot: {new_time}", current_user.name)
        return jsonify({"success": True, "message": f"Time slot {new_time} added successfully."})
    return jsonify({"success": False, "message": "Time slot already exists."}), 400

@venues_bp.route('/api/venues/block_time', methods=['POST'])
@login_required
def block_time():
    data = request.get_json() or {}
    time_slot = data.get('time_slot', '04:00 PM')
    if time_slot in db.court_grid:
        for court in db.courts:
            db.court_grid[time_slot][court] = "Maintenance"
        db.add_audit_log(f"Blocked all court slots at {time_slot} for maintenance", current_user.name)
        return jsonify({"success": True, "message": f"All courts at {time_slot} marked for Maintenance."})
    return jsonify({"success": False, "message": "Time slot not found."}), 400

@venues_bp.route('/api/venues/cancel_booking', methods=['POST'])
@login_required
def cancel_booking():
    data = request.get_json() or {}
    court = data.get('court', 'Court 1')
    time_slot = data.get('time_slot', '10:00 AM')

    if time_slot in db.court_grid and court in db.court_grid[time_slot]:
        db.court_grid[time_slot][court] = "Available"
        db.add_audit_log(f"Cancelled booking and refunded points for {court} at {time_slot}", current_user.name)
        return jsonify({"success": True, "message": f"Booking for {court} at {time_slot} cancelled and refunded."})
    return jsonify({"success": False, "message": "Booking not found."}), 400
