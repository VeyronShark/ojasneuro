"""Flask application factory."""
import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from config import config

db = SQLAlchemy()
jwt = JWTManager()

# Token blacklist for logout functionality
blacklisted_tokens = set()


@jwt.token_in_blocklist_loader
def check_if_token_in_blocklist(jwt_header, jwt_payload):
    """Check if a token has been blacklisted (logged out)."""
    jti = jwt_payload['jti']
    return jti in blacklisted_tokens


def create_app(config_name=None):
    """Create and configure the Flask application.
    
    Args:
        config_name: Configuration to use ('development', 'production', 'testing')
        
    Returns:
        Configured Flask application instance
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS for frontend integration
    # CORS_ORIGINS env var should contain comma-separated list of allowed origins
    cors_origins_env = os.environ.get('CORS_ORIGIN', '')
    
    if cors_origins_env:
        # Parse and clean origins from environment
        cors_origins = [origin.strip() for origin in cors_origins_env.split(',') if origin.strip()]
    else:
        # Default to localhost origins for development
        cors_origins = ['http://localhost:5173', 'http://localhost:3000', 'http://127.0.0.1:5173', 'http://127.0.0.1:3000']
    
    CORS(app, 
         origins=cors_origins,
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.schools import schools_bp
    from app.routes.classes import classes_bp
    from app.routes.children import children_bp
    from app.routes.events import events_bp
    from app.routes.analytics import analytics_bp
    from app.routes.insights import insights_bp
    from app.routes.consent import consent_bp
    from app.routes.reports import reports_bp
    from app.routes.templates import templates_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(schools_bp)
    app.register_blueprint(classes_bp)
    app.register_blueprint(children_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(insights_bp)
    app.register_blueprint(consent_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(templates_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
