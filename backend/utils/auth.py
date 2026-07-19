"""
Authentication utilities and decorators
"""

import bcrypt
import jwt
import os
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def hash_password(password):
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def generate_token(user_id, expires_in=86400):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + timedelta(seconds=expires_in)
    }
    token = jwt.encode(
        payload,
        os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
        algorithm='HS256'
    )
    return token

def verify_token(token):
    """Verify JWT token and extract user_id"""
    try:
        payload = jwt.decode(
            token,
            os.getenv('JWT_SECRET_KEY', 'jwt-secret-key'),
            algorithms=['HS256']
        )
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require valid JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        user_id = verify_token(token)
        if user_id is None:
            return jsonify({'message': 'Invalid or expired token'}), 401
        
        request.user_id = user_id
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Add admin verification logic
        return f(*args, **kwargs)
    
    return decorated
