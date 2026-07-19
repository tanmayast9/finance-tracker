"""
API routes for user management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import User, Account, AuditLog
from backend.utils.auth import token_required, verify_password, hash_password
from backend.utils.helpers import validate_request_json
from datetime import datetime

bp = Blueprint('users', __name__, url_prefix='/api/users')

@bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get current user profile"""
    user = User.query.get(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'phone': user.phone,
        'phone_verified': user.phone_verified,
        'bio': user.bio,
        'theme_preference': user.theme_preference,
        'currency': user.currency,
        'monthly_income': float(user.monthly_income or 0),
        'salary_day': user.salary_day,
        'two_factor_enabled': user.two_factor_enabled,
        'created_at': user.created_at.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None
    }), 200

@bp.route('/profile', methods=['PUT'])
@token_required
@validate_request_json()
def update_profile():
    """Update user profile"""
    user = User.query.get(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    # Update fields
    if 'full_name' in data:
        user.full_name = data['full_name']
    if 'phone' in data:
        if data['phone'] != user.phone:
            user.phone_verified = False
        user.phone = data['phone']
    if 'bio' in data:
        user.bio = data['bio']
    if 'theme_preference' in data:
        user.theme_preference = data['theme_preference']
    if 'currency' in data:
        user.currency = data['currency']
    if 'monthly_income' in data:
        try:
            user.monthly_income = float(data['monthly_income'])
        except (TypeError, ValueError):
            user.monthly_income = 0.0
    if 'salary_day' in data:
        v = data['salary_day']
        if v is None or v == '':
            user.salary_day = None
        else:
            try:
                d = int(v)
                user.salary_day = d if 1 <= d <= 31 else None
            except (TypeError, ValueError):
                user.salary_day = None
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Profile updated successfully'}), 200

@bp.route('/accounts', methods=['GET'])
@token_required
def get_accounts():
    """Get all user accounts"""
    accounts = Account.query.filter_by(user_id=request.user_id).all()
    
    return jsonify({
        'accounts': [
            {
                'id': acc.id,
                'account_name': acc.account_name,
                'account_type': acc.account_type,
                'balance': acc.balance,
                'currency': acc.currency,
                'is_active': acc.is_active
            }
            for acc in accounts
        ]
    }), 200

@bp.route('/accounts', methods=['POST'])
@token_required
@validate_request_json()
def create_account():
    """Create new account"""
    data = request.get_json()
    
    required_fields = ['account_name', 'account_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    account = Account(
        user_id=request.user_id,
        account_name=data['account_name'],
        account_type=data['account_type'],
        balance=data.get('balance', 0.0),
        currency=data.get('currency', 'USD')
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Account created',
        'account_id': account.id
    }), 201

@bp.route('/accounts/<int:account_id>', methods=['DELETE'])
@token_required
def delete_account(account_id):
    """Delete account"""
    account = Account.query.filter_by(id=account_id, user_id=request.user_id).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    db.session.delete(account)
    db.session.commit()
    
    return jsonify({'message': 'Account deleted'}), 200

@bp.route('/preferences', methods=['GET'])
@token_required
def get_preferences():
    """Get user preferences"""
    user = User.query.get(request.user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'theme_preference': user.theme_preference,
        'currency': user.currency,
        'two_factor_enabled': user.two_factor_enabled
    }), 200

@bp.route('/preferences', methods=['PUT'])
@token_required
@validate_request_json()
def update_preferences():
    """Update user preferences"""
    user = User.query.get(request.user_id)
    data = request.get_json()
    
    if 'theme_preference' in data:
        user.theme_preference = data['theme_preference']
    if 'currency' in data:
        user.currency = data['currency']
    if 'two_factor_enabled' in data:
        user.two_factor_enabled = data['two_factor_enabled']
    
    db.session.commit()
    
    return jsonify({'message': 'Preferences updated'}), 200

@bp.route('/activity-log', methods=['GET'])
@token_required
def get_activity_log():
    """Get user activity log"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    logs = AuditLog.query.filter_by(user_id=request.user_id).order_by(
        AuditLog.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'logs': [
            {
                'id': log.id,
                'action': log.action,
                'entity_type': log.entity_type,
                'created_at': log.created_at.isoformat()
            }
            for log in logs.items
        ],
        'total': logs.total,
        'page': page,
        'per_page': per_page
    }), 200
