import os
import uuid
from flask import Blueprint, render_template, request, jsonify, current_app, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from backend.models.mock_db import db

profile_bp = Blueprint('profile', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@profile_bp.route('/profile')
@login_required
def profile_view():
    """Renders the Administrator Profile & Customization screen."""
    return render_template('profile.html', user=current_user)

@profile_bp.route('/api/profile/upload-avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Handles avatar file uploads and image URL updates for the current administrator."""
    # Check if a file was uploaded via multipart/form-data
    if 'avatar' in request.files:
        file = request.files['avatar']
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected."}), 400
        
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            
            try:
                file.save(upload_path)
                avatar_url = url_for('static', filename=f'uploads/{unique_filename}')
                db.update_admin_avatar(current_user.id, avatar_url)
                return jsonify({
                    "success": True,
                    "avatar_url": avatar_url,
                    "message": "Profile photo updated successfully!"
                })
            except Exception as e:
                return jsonify({"success": False, "message": f"Failed to save file: {str(e)}"}), 500
        else:
            return jsonify({"success": False, "message": "Invalid file format. Please upload JPG, PNG, WEBP, or GIF."}), 400

    # Also handle JSON payload if user pasted an image link or data URL
    data = request.get_json(silent=True) or {}
    image_url = data.get('avatar_url', '').strip()
    if image_url:
        db.update_admin_avatar(current_user.id, image_url)
        return jsonify({
            "success": True,
            "avatar_url": image_url,
            "message": "Profile photo updated successfully!"
        })

    return jsonify({"success": False, "message": "No image file or URL provided."}), 400

@profile_bp.route('/api/profile/update-info', methods=['POST'])
@login_required
def update_profile_info():
    """Updates admin display name and/or role title."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    role = data.get('role', '').strip()

    if not name:
        return jsonify({"success": False, "message": "Display name cannot be blank."}), 400

    success, msg = db.update_admin_profile(current_user.id, name=name, role=role if role else "Administrator")
    if success:
        return jsonify({
            "success": True,
            "name": current_user.name,
            "role": current_user.role,
            "message": msg
        })
    return jsonify({"success": False, "message": msg}), 400
