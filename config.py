import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Configuration settings for the Flask application
    
    This class contains all configuration settings for the Flask application.
    Settings can be overridden by environment variables.
    """
    # Secret key for session signing and CSRF protection
    # In production, this should be set as an environment variable
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-replace-in-production'
    
    # Application port
    # Default to 3149 if not specified in environment
    PORT = int(os.environ.get('PORT') or 3149)
    
    # SQLAlchemy settings
    # SQLite database file path
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    # Disable tracking modifications to reduce overhead
    SQLALCHEMY_TRACK_MODIFICATIONS = False
