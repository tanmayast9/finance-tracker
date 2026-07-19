"""
API routes for authentication (login, signup, logout)
"""

import random
import string
from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from sqlalchemy import func
from backend.app import db
from backend.models import User, Account
from backend.utils.auth import hash_password, verify_password, generate_token, token_required
from backend.utils.helpers import validate_request_json, DateTimeEncoder

# Schema definitions for request validation
SIGNUP_SCHEMA = {
    'username': {'type': 'string', 'required': True},
    'email': {'type': 'string', 'required': True, 'regex': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'},
    'password': {'type': 'string', 'required': True, 'min_length': 6},
    'full_name': {'type': 'string', 'required': False},
    'currency': {'type': 'string', 'required': False, 'default': 'USD'}
}

LOGIN_SCHEMA = {
    'email': {'type': 'string', 'required': True},
    'password': {'type': 'string', 'required': True}
}

REFRESH_TOKEN_SCHEMA = {
    'refresh_token': {'type': 'string', 'required': True}
}

CHANGE_PASSWORD_SCHEMA = {
    'current_password': {'type': 'string', 'required': True},
    'new_password': {'type': 'string', 'required': True, 'min_length': 8}
}

SEND_OTP_SCHEMA = {
    'phone': {'type': 'string', 'required': True}
}

VERIFY_OTP_SCHEMA = {
    'phone': {'type': 'string', 'required': True},
    'otp': {'type': 'string', 'required': True}
}
import json

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# In-memory OTP store: { user_id: { 'otp': str, 'expires_at': datetime } }
# Use Redis or DB in production for multi-worker setups
_phone_otp_store = {}
OTP_EXPIRE_MINUTES = 5
OTP_LENGTH = 6

@bp.route('/signup', methods=['POST'])
@validate_request_json(SIGNUP_SCHEMA)
def signup(validated_data):
    """User registration endpoint"""
    try:
        # Check if user already exists
        if User.query.filter_by(username=validated_data['username']).first():
            return jsonify({'error': 'Username already exists'}), 409
        
        email = (validated_data['email'] or '').strip().lower()
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'Email already exists'}), 409
        
        # Create new user
        user = User(
            username=validated_data['username'],
            email=email,
            password_hash=hash_password(validated_data['password']),
            full_name=validated_data.get('full_name', ''),
            currency=validated_data.get('currency', 'USD')
        )
        
        db.session.add(user)
        db.session.flush()
        # Create default account for new user
        default_account = Account(
            user_id=user.id,
            account_name='Default Account',
            account_type='bank',
            balance=0.0,
            currency=validated_data.get('currency', 'USD')
        )
        db.session.add(default_account)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        token_str = token.decode('utf-8') if isinstance(token, bytes) else str(token)
        
        return jsonify({
            'message': 'User created successfully',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            },
            'token': token_str
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Sign up failed. Check that the database is running and tables exist.'}), 500

@bp.route('/login', methods=['POST'])
@validate_request_json(LOGIN_SCHEMA)
def login(validated_data):
    """User login endpoint (accepts email or username)"""
    try:
        email_or_username = (validated_data.get('email') or validated_data.get('username', '')).strip()
        if not email_or_username:
            return jsonify({'error': 'Email is required'}), 400
        email_lower = email_or_username.lower()
        # Match by email (case-insensitive) or username
        user = User.query.filter(
            (func.lower(User.email) == email_lower) | (User.username == email_or_username)
        ).first()
        
        if not user or not verify_password(validated_data['password'], user.password_hash):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Update last login
        from datetime import datetime
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        token_str = token.decode('utf-8') if isinstance(token, bytes) else str(token)
        
        return jsonify({
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'theme_preference': user.theme_preference,
                'currency': user.currency
            },
            'token': token_str
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Login failed. Check that the database is running.'}), 500

@bp.route('/refresh-token', methods=['POST'])
@validate_request_json(REFRESH_TOKEN_SCHEMA)
@token_required
def refresh_token():
    """Refresh authentication token"""
    token = generate_token(request.user_id)
    token_str = token.decode('utf-8') if isinstance(token, bytes) else str(token)
    return jsonify({
        'message': 'Token refreshed',
        'token': token_str
    }), 200

@bp.route('/verify-email', methods=['POST'])
@validate_request_json(SIGNUP_SCHEMA)
def verify_email():
    """Verify email address (placeholder for email verification logic)"""
    data = request.get_json()
    
    if 'email' not in data:
        return jsonify({'error': 'Email required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # TODO: Implement email verification logic
    user.is_verified = True
    db.session.commit()
    
    return jsonify({'message': 'Email verified'}), 200

@bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """User logout endpoint"""
    # Token is invalidated on client side
    return jsonify({'message': 'Logged out successfully'}), 200

@bp.route('/change-password', methods=['POST'])
@token_required
@validate_request_json(CHANGE_PASSWORD_SCHEMA)
def change_password(validated_data):
    """Change user password"""
    user = User.query.get(request.user_id)
    
    if not verify_password(validated_data['current_password'], user.password_hash):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    user.password_hash = hash_password(validated_data['new_password'])
    db.session.commit()
    
    return jsonify({'message': 'Password changed successfully'}), 200


def _generate_otp():
    return ''.join(random.choices(string.digits, k=OTP_LENGTH))


@bp.route('/send-phone-otp', methods=['POST'])
@token_required
@validate_request_json(SEND_OTP_SCHEMA)
def send_phone_otp(validated_data):
    """Send OTP to the given phone number for verification"""
    phone = (validated_data.get('phone') or '').strip()
    if not phone or len(phone) < 10:
        return jsonify({'error': 'Valid phone number required'}), 400
    user = User.query.get(request.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.phone = phone
    user.phone_verified = False
    db.session.commit()
    otp = _generate_otp()
    _phone_otp_store[request.user_id] = {
        'otp': otp,
        'expires_at': datetime.utcnow() + timedelta(minutes=OTP_EXPIRE_MINUTES)
    }
    # TODO: Send SMS via Twilio/AWS SNS when configured. For dev, OTP is returned.
    import os
    if os.getenv('FLASK_ENV') == 'development' or os.getenv('DEBUG', '').lower() == 'true':
        return jsonify({
            'message': 'OTP sent',
            'otp_for_testing': otp,
            'expires_in_minutes': OTP_EXPIRE_MINUTES
        }), 200
    return jsonify({
        'message': 'OTP sent to your phone',
        'expires_in_minutes': OTP_EXPIRE_MINUTES
    }), 200


@bp.route('/verify-phone-otp', methods=['POST'])
@token_required
@validate_request_json(VERIFY_OTP_SCHEMA)
def verify_phone_otp(validated_data):
    """Verify phone using OTP and mark phone as verified"""
    otp = (validated_data.get('otp') or '').strip()
    if not otp or len(otp) != OTP_LENGTH:
        return jsonify({'error': 'Valid 6-digit OTP required'}), 400
    stored = _phone_otp_store.get(request.user_id)
    if not stored:
        return jsonify({'error': 'No OTP sent. Request a new one.'}), 400
    if datetime.utcnow() > stored['expires_at']:
        del _phone_otp_store[request.user_id]
        return jsonify({'error': 'OTP expired. Request a new one.'}), 400
    if stored['otp'] != otp:
        return jsonify({'error': 'Invalid OTP'}), 400
    user = User.query.get(request.user_id)
    if user:
        user.phone_verified = True
        db.session.commit()
    del _phone_otp_store[request.user_id]
    return jsonify({'message': 'Phone verified successfully'}), 200
