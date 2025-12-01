"""Configuration settings for the Flask application."""
import os
from datetime import timedelta


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access']
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Privacy: Never collect GPS or microphone data (Requirement 9.4)
    COLLECT_GPS_DATA = False
    COLLECT_MICROPHONE_DATA = False


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///dev.db'
    )


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    
    # Handle Render's postgres:// vs postgresql:// URL format
    # Get raw URL from environment
    database_url = os.getenv('DATABASE_URL', '')
    # Convert legacy postgres:// to postgresql:// for SQLAlchemy compatibility
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    # Force use of pg8000 driver
    if database_url.startswith('postgresql://'):
        database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
    # Translate sslmode parameter (pg8000 expects 'ssl')
    if 'sslmode=' in database_url:
        # Simple replacement: drop sslmode and enable ssl
        database_url = database_url.replace('sslmode=require', 'ssl=true')
        database_url = database_url.replace('sslmode=disable', 'ssl=false')
    SQLALCHEMY_DATABASE_URI = database_url
    
    # Override with stronger settings in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
