import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, render_template
from flask_login import LoginManager
from backend.config import Config
from backend.models.mock_db import db

def create_app():
    # Resolve absolute paths for frontend templates & static assets
    base_dir = os.path.abspath(os.path.dirname(__file__))
    template_dir = os.path.abspath(os.path.join(base_dir, '../frontend/templates'))
    static_dir = os.path.abspath(os.path.join(base_dir, '../frontend/static'))

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access the admin platform.'
    login_manager.login_message_category = 'info'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.get_user_by_id(user_id)

    # Register Blueprints
    from backend.routes.auth import auth_bp
    from backend.routes.dashboard import dashboard_bp
    from backend.routes.users import users_bp
    from backend.routes.matchmaking import matchmaking_bp
    from backend.routes.venues import venues_bp
    from backend.routes.moderation import moderation_bp
    from backend.routes.settings import settings_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(matchmaking_bp)
    app.register_blueprint(venues_bp)
    app.register_blueprint(moderation_bp)
    app.register_blueprint(settings_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', page_title="404 Not Found"), 404

    return app

if __name__ == '__main__':
    app = create_app()
    print("==================================================")
    print("  Pickle Legends - Admin Platform Running!")
    print("  Access URL: http://127.0.0.1:5000")
    print("==================================================")
    app.run(host='0.0.0.0', port=5000, debug=True)
