"""
Database initialization and migration utilities
"""

import os
import sys

def init_database():
    """Initialize database with tables"""
    from backend.app import create_app, db
    
    app = create_app()
    
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database initialized successfully!")

def create_sample_data():
    """Create sample data for testing"""
    from backend.app import create_app, db
    from backend.models import User, Account, Category, Transaction
    from backend.utils.auth import hash_password
    from datetime import datetime, timedelta
    
    app = create_app()
    
    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("Sample data already exists")
            return
        
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=hash_password('password123'),
            full_name='Test User',
            currency='USD'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create test account
        account = Account(
            user_id=user.id,
            account_name='My Bank Account',
            account_type='bank',
            balance=10000.0,
            currency='USD'
        )
        db.session.add(account)
        db.session.flush()
        
        # Create default expense and income categories
        expense_categories = [
            {'name': 'Food & Dining', 'icon': '🍽️', 'color': '#FF6B6B'},
            {'name': 'Transportation', 'icon': '🚗', 'color': '#4ECDC4'},
            {'name': 'Shopping', 'icon': '🛍️', 'color': '#FFE66D'},
        ]
        income_categories = [
            {'name': 'Salary', 'icon': '💼', 'color': '#2ECC71'},
            {'name': 'Freelance', 'icon': '💻', 'color': '#3498DB'},
            {'name': 'Bonus', 'icon': '🎁', 'color': '#F39C12'},
            {'name': 'Other', 'icon': '📌', 'color': '#CCCCCC'},
        ]
        
        for cat in expense_categories:
            category = Category(
                user_id=user.id,
                name=cat['name'],
                category_type='expense',
                icon=cat['icon'],
                color=cat['color'],
                is_custom=False
            )
            db.session.add(category)
        
        for cat in income_categories:
            category = Category(
                user_id=user.id,
                name=cat['name'],
                category_type='income',
                icon=cat['icon'],
                color=cat['color'],
                is_custom=False
            )
            db.session.add(category)
        
        db.session.commit()
        print("Sample data created successfully!")

if __name__ == '__main__':
    init_database()
    create_sample_data()
