"""
API routes for account management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Account, Transaction
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime

bp = Blueprint('accounts', __name__, url_prefix='/api/accounts')

@bp.route('/', methods=['GET'])
@token_required
def get_accounts():
    """Get all accounts for user"""
    accounts = Account.query.filter_by(user_id=request.user_id, is_active=True).all()
    
    return jsonify({
        'accounts': [{
            'id': acc.id,
            'name': acc.account_name,
            'type': acc.account_type,
            'balance': acc.balance,
            'currency': acc.currency,
            'created_at': acc.created_at.isoformat(),
            'updated_at': acc.updated_at.isoformat()
        } for acc in accounts]
    }), 200

# Define the account schema at module level
ACCOUNT_SCHEMA = {
    'account_name': {'type': 'string', 'required': True},
    'account_type': {'type': 'string', 'required': True},
    'initial_balance': {'type': 'number', 'required': False, 'default': 0.0},
    'currency': {'type': 'string', 'required': False, 'default': 'USD'}
}

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json(ACCOUNT_SCHEMA)
def create_account(validated_data):
    """Create a new account"""
    # Check if account with same name exists
    existing = Account.query.filter_by(
        user_id=request.user_id,
        account_name=validated_data['account_name']
    ).first()
    
    if existing:
        return jsonify({'error': 'Account with this name already exists'}), 400
    
    # Create new account
    account = Account(
        user_id=request.user_id,
        account_name=validated_data['account_name'],
        account_type=validated_data['account_type'],
        balance=validated_data.get('initial_balance', 0.0),
        currency=validated_data.get('currency', 'USD'),
        is_active=True
    )
    
    db.session.add(account)
    db.session.commit()
    
    return jsonify({
        'message': 'Account created successfully',
        'account': {
            'id': account.id,
            'name': account.account_name,
            'type': account.account_type,
            'balance': account.balance,
            'currency': account.currency
        }
    }), 201

@bp.route('/<int:account_id>', methods=['GET'])
@token_required
def get_account(account_id):
    """Get account details with recent transactions"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=request.user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Get recent transactions
    transactions = Transaction.query.filter_by(
        account_id=account_id
    ).order_by(
        Transaction.transaction_date.desc()
    ).limit(5).all()
    
    return jsonify({
        'account': {
            'id': account.id,
            'name': account.account_name,
            'type': account.account_type,
            'balance': account.balance,
            'currency': account.currency,
            'created_at': account.created_at.isoformat(),
            'updated_at': account.updated_at.isoformat()
        },
        'recent_transactions': [{
            'id': t.id,
            'amount': t.amount,
            'type': t.transaction_type,
            'description': t.description,
            'date': t.transaction_date.isoformat(),
            'category': t.category.name if t.category else None
        } for t in transactions]
    }), 200

@bp.route('/<int:account_id>', methods=['PUT'])
@token_required
@validate_request_json({
    'account_name': {'type': 'string', 'required': False},
    'account_type': {'type': 'string', 'required': False},
    'is_active': {'type': 'boolean', 'required': False}
})
def update_account(account_id):
    """Update account details"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=request.user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    data = request.get_json()
    
    # Update fields if provided
    if 'account_name' in data:
        # Check if new name is already taken
        existing = Account.query.filter(
            Account.id != account_id,
            Account.user_id == request.user_id,
            Account.account_name == data['account_name']
        ).first()
        
        if existing:
            return jsonify({'error': 'Another account with this name already exists'}), 400
            
        account.account_name = data['account_name']
    
    if 'account_type' in data:
        account.account_type = data['account_type']
    
    if 'is_active' in data:
        account.is_active = data['is_active']
    
    account.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Account updated successfully',
        'account': {
            'id': account.id,
            'name': account.account_name,
            'type': account.account_type,
            'is_active': account.is_active,
            'updated_at': account.updated_at.isoformat()
        }
    }), 200

@bp.route('/<int:account_id>', methods=['DELETE'])
@token_required
def delete_account(account_id):
    """Delete an account (soft delete)"""
    account = Account.query.filter_by(
        id=account_id,
        user_id=request.user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Check if account has transactions
    has_transactions = Transaction.query.filter_by(account_id=account_id).first() is not None
    
    if has_transactions:
        # Soft delete
        account.is_active = False
        account.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Account deactivated successfully'}), 200
    else:
        # Hard delete if no transactions
        db.session.delete(account)
        db.session.commit()
        return jsonify({'message': 'Account deleted successfully'}), 200

@bp.route('/<int:account_id>/transactions', methods=['GET'])
@token_required
def get_account_transactions(account_id):
    """Get all transactions for a specific account"""
    # Verify account belongs to user
    account = Account.query.filter_by(
        id=account_id,
        user_id=request.user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # Build query
    query = Transaction.query.filter_by(account_id=account_id)
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.transaction_date.between(start, end))
    
    # Execute query with pagination
    transactions = query.order_by(
        Transaction.transaction_date.desc()
    ).paginate(page=page, per_page=per_page)
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'amount': t.amount,
            'type': t.transaction_type,
            'description': t.description,
            'date': t.transaction_date.isoformat(),
            'category': t.category.name if t.category else None,
            'notes': t.notes
        } for t in transactions.items],
        'pagination': {
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page,
            'per_page': per_page
        }
    }), 200

@bp.route('/summary', methods=['GET'])
@token_required
def get_accounts_summary():
    """Get summary of all accounts with balances"""
    accounts = Account.query.filter_by(
        user_id=request.user_id,
        is_active=True
    ).all()
    
    total_balance = sum(acc.balance for acc in accounts)
    
    return jsonify({
        'total_balance': total_balance,
        'accounts': [{
            'id': acc.id,
            'name': acc.account_name,
            'type': acc.account_type,
            'balance': acc.balance,
            'currency': acc.currency,
            'is_active': acc.is_active
        } for acc in accounts]
    }), 200
