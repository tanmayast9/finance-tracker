import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    # Using SQLite temporarily - MySQL connection needs troubleshooting
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///finance_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
