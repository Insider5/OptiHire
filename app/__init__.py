from flask import Flask, render_template
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config
import os
import json
import logging
from logging.handlers import RotatingFileHandler

# Initialize extensions
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "60 per hour"])


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions with app
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'

    # ─── Custom Jinja filters ────────────────────────────────
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Convert JSON string to Python object"""
        if isinstance(value, str):
            try:
                return json.loads(value)
            except Exception:
                return []
        return value or []

    @app.template_filter('percentage')
    def percentage_filter(value):
        """Convert a 0-1 float to a percentage string, e.g. 0.87 → '87.0%'"""
        try:
            return f"{float(value) * 100:.1f}%"
        except (TypeError, ValueError):
            return '0.0%'

    @app.template_filter('score_color')
    def score_color_filter(value):
        """Return a Tailwind text color class based on score 0-1"""
        try:
            v = float(value) * 100
        except (TypeError, ValueError):
            return 'text-gray-500'
        if v >= 75:
            return 'text-green-600'
        elif v >= 50:
            return 'text-yellow-600'
        else:
            return 'text-red-500'

    # ─── Global template functions & filters ─────────────────
    def get_unread_count(user):
        """Return unread notification count for a user (used in nav bell)"""
        try:
            from app.storage import get_storage
            return get_storage().get_unread_count(user.id)
        except Exception:
            return 0

    app.template_global('get_unread_count')(get_unread_count)
    app.template_filter('get_unread_count')(get_unread_count)

    # ─── Create required folders ─────────────────────────────
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATA_DIR'], exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs'), exist_ok=True)

    # ─── Register blueprints ─────────────────────────────────
    from app.routes import auth, main, jobs, candidates, dashboard
    from app.routes import profile, analytics, interviews, interview_room

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.register_blueprint(jobs.bp)
    app.register_blueprint(candidates.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(profile.bp)
    app.register_blueprint(analytics.bp)
    app.register_blueprint(interviews.bp)
    app.register_blueprint(interview_room.bp)

    # ─── Error handlers ──────────────────────────────────────
    @app.errorhandler(404)
    def not_found_error(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        app.logger.error(f'Server Error: {e}')
        return render_template('errors/500.html'), 500

    @app.errorhandler(403)
    def forbidden_error(e):
        return render_template('errors/403.html'), 403

    # ─── File-based logging ──────────────────────────────────
    if not app.debug and not app.testing:
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'optihire.log'),
            maxBytes=1_048_576,  # 1 MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(module)s: %(message)s'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('OptiHire startup')

    return app
