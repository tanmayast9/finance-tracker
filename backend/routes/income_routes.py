"""
API routes for income management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Transaction, Category, Account
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime
from sqlalchemy import and_, func

bp = Blueprint('income', __name__, url_prefix='/api/income')

@bp.route('/', methods=['GET'])
@token_required
def get_income():
    """Get all income for user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(
        user_id=request.user_id,
        transaction_type='income'
    )
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.transaction_date.between(start, end))
    
    income = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'income': [
            {
                'id': inc.id,
                'amount': inc.amount,
                'category': inc.category.name,
                'description': inc.description,
                'notes': inc.notes,
                'transaction_date': inc.transaction_date.isoformat(),
                'account': inc.account.account_name
            }
            for inc in income.items
        ],
        'total': income.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json()
def create_income():
    """Create new income"""
    data = request.get_json()
    
    required_fields = ['amount', 'category_id', 'account_id']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify account ownership
    account = Account.query.filter_by(
        id=data['account_id'],
        user_id=request.user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Verify category ownership
    category = Category.query.filter_by(
        id=data['category_id'],
        user_id=request.user_id
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Create transaction
    transaction = Transaction(
        user_id=request.user_id,
        account_id=data['account_id'],
        category_id=data['category_id'],
        transaction_type='income',
        amount=data['amount'],
        description=data.get('description', ''),
        notes=data.get('notes', ''),
        transaction_date=datetime.fromisoformat(
            data.get('transaction_date', datetime.utcnow().isoformat())
        )
    )
    
    # Update account balance
    account.balance += data['amount']
    
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        'message': 'Income recorded',
        'transaction_id': transaction.id
    }), 201

@bp.route('/<int:income_id>', methods=['PUT'])
@token_required
@validate_request_json()
def update_income(income_id):
    """Update income"""
    income = Transaction.query.filter_by(
        id=income_id,
        user_id=request.user_id,
        transaction_type='income'
    ).first()
    
    if not income:
        return jsonify({'error': 'Income not found'}), 404
    
    data = request.get_json()
    old_amount = income.amount
    
    if 'amount' in data:
        income.amount = data['amount']
        # Update account balance
        income.account.balance = income.account.balance - old_amount + data['amount']
    
    if 'description' in data:
        income.description = data['description']
    if 'notes' in data:
        income.notes = data['notes']
    if 'category_id' in data:
        income.category_id = data['category_id']
    
    income.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Income updated'}), 200

@bp.route('/<int:income_id>', methods=['DELETE'])
@token_required
def delete_income(income_id):
    """Delete income"""
    income = Transaction.query.filter_by(
        id=income_id,
        user_id=request.user_id,
        transaction_type='income'
    ).first()
    
    if not income:
        return jsonify({'error': 'Income not found'}), 404
    
    # Deduct amount from account
    income.account.balance -= income.amount
    
    db.session.delete(income)
    db.session.commit()
    
    return jsonify({'message': 'Income deleted'}), 200

@bp.route('/summary', methods=['GET'])
@token_required
def get_income_summary():
    """Get income summary"""
    period = request.args.get('period', 'monthly')  # monthly, yearly
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    from datetime import date
    from .expense_routes import get_date_range_for_period
    
    start_date, end_date = get_date_range_for_period(period, year, month)
    
    income_by_category = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= datetime.combine(start_date, datetime.min.time()),
            Transaction.transaction_date <= datetime.combine(end_date, datetime.max.time())
        )
    ).group_by(Category.id, Category.name).all()
    
    total_income = sum(amount for _, amount in income_by_category) if income_by_category else 0
    
    return jsonify({
        'period': period,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'total_income': total_income,
        'by_category': [
            {
                'category': category,
                'amount': float(amount)
            }
            for category, amount in income_by_category
        ]
    }), 200
