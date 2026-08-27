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


# ---------------------------------------------------------------------------
#  Digital Booking Sheet Routes (Admin Pen-and-Paper Replacement)
# ---------------------------------------------------------------------------

@venues_bp.route('/booking-sheet')
@login_required
def booking_sheet_view():
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    selected_date = request.args.get('date', today_str)

    sheet_data = db.get_booking_sheet_matrix(selected_date)

    return render_template(
        'booking_sheet.html',
        selected_date=selected_date,
        time_slots=sheet_data['time_slots'],
        courts=sheet_data['courts'],
        matrix=sheet_data['matrix'],
        today_str=today_str
    )


@venues_bp.route('/api/booking-sheet/matrix')
@login_required
def get_booking_matrix():
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    date = request.args.get('date', today_str)
    sheet_data = db.get_booking_sheet_matrix(date)
    return jsonify({"success": True, **sheet_data})


@venues_bp.route('/api/booking-sheet/grid')
@login_required
def get_booking_grid():
    from datetime import datetime
    today_str = datetime.now().strftime("%Y-%m-%d")
    date = request.args.get('date', today_str)
    court = request.args.get('court', 'Court 1')
    grid = db.get_booking_sheet_grid(date, court)
    return jsonify({"success": True, "grid": grid, "date": date, "court": court})



@venues_bp.route('/api/booking-sheet/save', methods=['POST'])
@login_required
def save_booking():
    data = request.get_json() or {}
    date = data.get('date')
    court = data.get('court')
    time_slot = data.get('time_slot')
    customer_name = data.get('customer_name', '').strip()
    payment_status = data.get('payment_status', 'paid')

    if not date or not court or not time_slot or not customer_name:
        return jsonify({"success": False, "message": "Date, Court, Time Slot, and Customer Name are required."}), 400

    success, msg = db.save_direct_booking(date, court, time_slot, customer_name, payment_status)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 400


@venues_bp.route('/api/booking-sheet/clear', methods=['POST'])
@login_required
def clear_booking():
    data = request.get_json() or {}
    date = data.get('date')
    court = data.get('court')
    time_slot = data.get('time_slot')

    if not date or not court or not time_slot:
        return jsonify({"success": False, "message": "Date, Court, and Time Slot are required."}), 400

    success, msg = db.clear_direct_booking(date, court, time_slot)
    if success:
        return jsonify({"success": True, "message": msg})
    return jsonify({"success": False, "message": msg}), 400

