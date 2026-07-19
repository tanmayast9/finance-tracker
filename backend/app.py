"""
Finance Application - Main Flask Application
Core application factory and configuration
"""

from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables
load_dotenv()

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()

def get_database_uri():
    """Resolve the database URI with a SQLite fallback for local development."""
    database_url = os.getenv('DATABASE_URL') or os.getenv('DB_URI')
    if database_url:
        return database_url

    if os.getenv('USE_SQLITE', '').lower() in {'1', 'true', 'yes', 'on'}:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'finance.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f'sqlite:///{db_path}'

    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_password = os.getenv('DB_PASSWORD', '')
    db_name = os.getenv('DB_NAME', 'finance')
    db_port = os.getenv('DB_PORT', '3306')

    use_mysql = (
        os.getenv('USE_MYSQL', '').lower() in {'1', 'true', 'yes', 'on'}
        or db_host not in (None, '', 'localhost', '127.0.0.1')
        or db_user not in (None, '', 'root')
        or db_name not in (None, '', 'finance')
        or db_port not in (None, '', '3306')
        or (db_password not in (None, '') and db_host not in (None, '', 'localhost', '127.0.0.1'))
    )

    if not use_mysql:
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'finance.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f'sqlite:///{db_path}'

    return f'mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'


def create_app():
    """Application factory function"""
    # Define frontend directory path
    frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    
    # Create the Flask application
    app = Flask(__name__, static_folder=frontend_dir)
    
    # Configuration
    app.config.from_mapping(
        # Database configuration
        SQLALCHEMY_DATABASE_URI=get_database_uri(),
        JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
        JWT_ACCESS_TOKEN_EXPIRES=timedelta(hours=24)
    )
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Register blueprints
    with app.app_context():
        from .routes import (
            auth_routes, expense_routes, income_routes, 
            budget_routes, analytics_routes, category_routes,
            transaction_routes, user_routes, account_routes,
            enhanced_transaction_routes
        )
        
        app.register_blueprint(auth_routes.bp)
        app.register_blueprint(expense_routes.bp)
        app.register_blueprint(income_routes.bp)
        app.register_blueprint(budget_routes.bp)
        app.register_blueprint(analytics_routes.bp)
        app.register_blueprint(category_routes.bp)
        app.register_blueprint(transaction_routes.bp)
        app.register_blueprint(enhanced_transaction_routes.bp)
        app.register_blueprint(user_routes.bp)
        app.register_blueprint(account_routes.bp)
        
        # Create database tables
        db.create_all()

    # Frontend serving routes (serve index and static assets)
    @app.route('/', defaults={'path': 'index.html'})
    @app.route('/<path:path>')
    def serve_frontend(path):
        # Prevent overlapping API routes
        if path.startswith('api/'):
            abort(404)
        return send_from_directory(app.static_folder, path)
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy", "message": "Finance API is running"})
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
