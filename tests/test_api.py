"""
Unit tests for Finance Application
"""

import pytest
import json
from datetime import datetime
from backend.app import create_app, db
from backend.models import User, Account, Category, Transaction
from backend.utils.auth import hash_password, verify_password, generate_token

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create test user and keep it attached to the active session during the test."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=hash_password('password123'),
            full_name='Test User'
        )
        db.session.add(user)
        db.session.commit()
        yield user

class TestAuthentication:
    """Test authentication endpoints"""
    
    def test_signup(self, client):
        """Test user signup"""
        response = client.post('/api/auth/signup', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'Password123',
            'full_name': 'New User'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'token' in data
        assert data['user']['username'] == 'newuser'
    
    def test_login(self, client, test_user):
        """Test user login"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
    
    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401

class TestExpenses:
    """Test expense management"""
    
    def test_create_expense(self, client, app, test_user):
        """Test creating an expense"""
        with app.app_context():
            # Create account
            account = Account(
                user_id=test_user.id,
                account_name='Test Account',
                account_type='bank',
                balance=10000
            )
            db.session.add(account)
            
            # Create category
            category = Category(
                user_id=test_user.id,
                name='Food',
                category_type='expense'
            )
            db.session.add(category)
            db.session.commit()
            account_id = account.id
            category_id = category.id
            token = generate_token(test_user.id)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.post('/api/expenses/', 
            headers=headers,
            json={
                'amount': 50.0,
                'category_id': category_id,
                'account_id': account_id,
                'description': 'Lunch'
            }
        )
        
        assert response.status_code == 201

class TestBudgets:
    """Test budget management"""
    
    def test_create_budget(self, client, app, test_user):
        """Test creating a budget"""
        with app.app_context():
            category = Category(
                user_id=test_user.id,
                name='Food',
                category_type='expense'
            )
            db.session.add(category)
            db.session.commit()
            category_id = category.id
            
            token = generate_token(test_user.id)
        
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.post('/api/budgets/', 
            headers=headers,
            json={
                'category_id': category_id,
                'amount_limit': 1000.0,
                'alert_threshold': 80
            }
        )
        
        assert response.status_code == 201

class TestAnalytics:
    """Test analytics endpoints"""
    
    def test_get_dashboard(self, client, test_user):
        """Test getting dashboard"""
        token = generate_token(test_user.id)
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/analytics/dashboard', headers=headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'income' in data
        assert 'expenses' in data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
