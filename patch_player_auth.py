"""
Patch script for Pickle-Legends auth.py and models.py to fix session persistence across refresh.
"""
import os

def patch_files():
    player_root = r"C:\Users\Acer\Pickle-Legends\pickle_legends\backend"
    auth_path = os.path.join(player_root, "routes", "auth.py")
    models_path = os.path.join(player_root, "models.py")

    # -------------------------------------------------------------
    # 1. PATCH auth.py
    # -------------------------------------------------------------
    if os.path.exists(auth_path):
        with open(auth_path, "r", encoding="utf-8") as f:
            auth_code = f.read()

        new_auth_code = """from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
from pickle_legends.backend.models import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def opening_screen():
    return render_template('auth.html')

@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    data = request.json or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username:
        return jsonify({"success": False, "message": "Please enter your Username or Player Name"}), 400

    user = db.login_user(username, password)
    if not user:
        return jsonify({"success": False, "message": "Invalid username or credentials."}), 400

    # Save to session cookie
    session['user_handle'] = user['handle']
    session['user_name'] = user['name']

    return jsonify({
        "success": True,
        "message": f"Welcome back, {user['name']}!",
        "user": user,
        "redirect_url": url_for('dashboard.dashboard')
    })

@auth_bp.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json or {}
    full_name = data.get('full_name', '').strip()
    player_name = data.get('player_name', '').strip()
    email = data.get('email', '').strip()
    contact = data.get('contact', '').strip()
    skill_level = data.get('skill_level', 'Beginner').strip()
    self_reported_skill = data.get('self_reported_skill', skill_level).strip()
    dupr_id = data.get('dupr_id', '').strip()
    password = data.get('password', '').strip()
    confirm_password = data.get('confirm_password', '').strip()

    if not full_name or not player_name:
        return jsonify({"success": False, "message": "Full Name and Player Name are required"}), 400

    if password and confirm_password and password != confirm_password:
        return jsonify({"success": False, "message": "Passwords do not match"}), 400

    dupr_rating = None
    dupr_verified = False
    dupr_warning = None

    # Optional DUPR verification step
    if dupr_id:
        from pickle_legends.backend.integrations.dupr_client import get_dupr_client, DuprIntegrationError
        client = get_dupr_client()
        try:
            dupr_info = client.get_user_by_dupr_id(dupr_id)
            dupr_rating = dupr_info.get("rating", 4.0)
            dupr_verified = dupr_info.get("verified", True)
        except DuprIntegrationError as e:
            dupr_warning = f"Couldn't verify DUPR ID '{dupr_id}' ({str(e)}). Your account was created with self-reported skill '{self_reported_skill}'. You can link DUPR anytime from settings."

    user = db.register_user(
        full_name=full_name,
        player_name=player_name,
        email=email,
        contact=contact,
        skill_level=skill_level,
        password=password,
        dupr_id=dupr_id if dupr_verified else None,
        dupr_rating=dupr_rating,
        dupr_verified=dupr_verified,
        self_reported_skill=self_reported_skill
    )

    # Save to session cookie
    session['user_handle'] = user['handle']
    session['user_name'] = user['name']

    msg = f"Account created! Welcome to Pickle Legends, {user['name']}!"
    if dupr_verified:
        msg += f" (DUPR Rating: {dupr_rating:.2f} Verified)"
    elif dupr_warning:
        msg += f" {dupr_warning}"

    return jsonify({
        "success": True,
        "message": msg,
        "user": user,
        "dupr_warning": dupr_warning,
        "redirect_url": url_for('dashboard.dashboard')
    })

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.opening_screen'))
"""
        with open(auth_path, "w", encoding="utf-8") as f:
            f.write(new_auth_code)
        print("[+] Patched pickle_legends/backend/routes/auth.py successfully!")

    # -------------------------------------------------------------
    # 2. PATCH models.py DataStore.user property
    # -------------------------------------------------------------
    if os.path.exists(models_path):
        with open(models_path, "r", encoding="utf-8") as f:
            models_code = f.read()

        # Ensure flask session is imported
        if "from flask import session" not in models_code:
            models_code = "from flask import session\n" + models_code

        # Replace @property def user(self) with session-aware lookup
        old_user_prop = """    # --- Live Database Properties ---
    @property
    def user(self):
        try:
            u = User.query.first()
            if u:
                return u.to_dict()
        except Exception:
            pass"""

        new_user_prop = """    # --- Live Database Properties ---
    @property
    def user(self):
        try:
            from flask import session
            # 1. Lookup the active user from the session cookie
            logged_in_handle = session.get('user_handle') or session.get('user_name')
            if logged_in_handle:
                u = User.query.filter(
                    (sqla.func.lower(User.handle) == str(logged_in_handle).lower()) |
                    (sqla.func.lower(User.name) == str(logged_in_handle).lower()) |
                    (sqla.func.lower(User.email) == str(logged_in_handle).lower())
                ).first()
                if u:
                    return u.to_dict()

            # 2. Fallback to newest registered user
            u = User.query.order_by(User.created_at.desc()).first()
            if u:
                return u.to_dict()
        except Exception:
            pass"""

        if old_user_prop in models_code:
            models_code = models_code.replace(old_user_prop, new_user_prop)
        else:
            # Fallback replacement
            target_piece = """    @property
    def user(self):
        try:
            u = User.query.first()"""
            replacement_piece = """    @property
    def user(self):
        try:
            from flask import session
            logged_in_handle = session.get('user_handle') or session.get('user_name')
            if logged_in_handle:
                u = User.query.filter(
                    (sqla.func.lower(User.handle) == str(logged_in_handle).lower()) |
                    (sqla.func.lower(User.name) == str(logged_in_handle).lower()) |
                    (sqla.func.lower(User.email) == str(logged_in_handle).lower())
                ).first()
                if u:
                    return u.to_dict()
            u = User.query.order_by(User.created_at.desc()).first()"""
            if target_piece in models_code:
                models_code = models_code.replace(target_piece, replacement_piece)

        with open(models_path, "w", encoding="utf-8") as f:
            f.write(models_code)
        print("[+] Patched pickle_legends/backend/models.py successfully!")

if __name__ == "__main__":
    patch_files()
