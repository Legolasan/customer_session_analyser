"""
Flask application factory.
"""

from flask import Flask, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

# Data protection: Prevent accidental db.drop_all() in production
_original_drop_all = db.drop_all

def _safe_drop_all(*args, **kwargs):
    """Protected version of drop_all that prevents accidental data loss."""
    is_production = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    if is_production:
        raise RuntimeError(
            "CRITICAL: db.drop_all() is disabled in production to prevent data loss. "
            "Use migrations (flask db downgrade) instead."
        )
    logging.warning("db.drop_all() called in development mode - this will delete all data!")
    return _original_drop_all(*args, **kwargs)

# Override drop_all with safe version
db.drop_all = _safe_drop_all


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    from app.auth import User
    return User.get(user_id)


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    database_url = os.getenv('DATABASE_URL', 'sqlite:///customer_sessions.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Validate environment variables
    is_production = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
    if is_production:
        if not database_url or database_url.startswith('sqlite:///'):
            app.logger.warning("⚠️  Production environment detected but using SQLite - this is not recommended")
        app.logger.info("🔒 Production mode: Database operations are protected")
    else:
        app.logger.info("🔧 Development mode: Database operations enabled")
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure Flask-Login
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.unauthorized_handler
    def unauthorized():
        """Handle unauthorized access - return JSON for API requests, redirect for web."""
        if request.path.startswith('/api/') or request.is_json:
            return jsonify({'error': 'Authentication required'}), 401
        return redirect(url_for('main.login', next=request.url))
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Only create tables in development (migrations handle production)
    # CRITICAL: Never use db.create_all() in production to prevent data loss
    with app.app_context():
        is_production = os.getenv('RAILWAY_ENVIRONMENT') == 'production'
        if not is_production:
            try:
                db.create_all()  # Safe for local dev
                app.logger.info("✅ Database tables created (development mode)")
            except Exception as e:
                app.logger.error(f"❌ Error creating tables: {e}")
                app.logger.info("💡 Tip: If tables already exist, this is normal. Use migrations for schema changes.")
        else:
            app.logger.info("🔒 Production mode: Using migrations for schema management")
            app.logger.info("📋 To apply migrations, run: flask db upgrade")
        # In production, migrations handle schema
    
    return app

