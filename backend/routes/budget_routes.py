"""
API routes for budget management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Budget, Category, Transaction
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime
from sqlalchemy import and_, func

bp = Blueprint('budgets', __name__, url_prefix='/api/budgets')

@bp.route('/', methods=['GET'])
@token_required
def get_budgets():
    """Get all budgets for user"""
    period = request.args.get('period', 'monthly')
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    from datetime import date
    now = datetime.utcnow()
    
    if not year:
        year = now.year
    if not month and period == 'monthly':
        month = now.month
    
    budgets = Budget.query.filter_by(user_id=request.user_id, period=period)
    
    if period == 'monthly':
        budgets = budgets.filter_by(year=year, month=month)
    elif period == 'yearly':
        budgets = budgets.filter_by(year=year)
    
    budgets = budgets.all()
    
    budget_data = []
    
    for budget in budgets:
        # Calculate spent amount
        if period == 'monthly':
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
        else:
            start = datetime(year, 1, 1)
            end = datetime(year + 1, 1, 1)
        
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == request.user_id,
                Transaction.category_id == budget.category_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start,
                Transaction.transaction_date < end
            )
        ).scalar() or 0
        
        remaining = budget.amount_limit - spent
        percentage = (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
        
        budget_data.append({
            'id': budget.id,
            'category': budget.category.name,
            'limit': budget.amount_limit,
            'spent': float(spent),
            'remaining': remaining,
            'percentage': percentage,
            'alert_threshold': budget.alert_threshold
        })
    
    return jsonify({
        'period': period,
        'year': year,
        'month': month if period == 'monthly' else None,
        'budgets': budget_data
    }), 200

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json()
def create_budget():
    """Create new budget"""
    data = request.get_json()
    
    required_fields = ['category_id', 'amount_limit']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Verify category ownership
    category = Category.query.filter_by(
        id=data['category_id'],
        user_id=request.user_id
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Check if budget already exists
    now = datetime.utcnow()
    existing = Budget.query.filter_by(
        user_id=request.user_id,
        category_id=data['category_id'],
        period=data.get('period', 'monthly'),
        year=data.get('year', now.year),
        month=data.get('month', now.month)
    ).first()
    
    if existing:
        return jsonify({'error': 'Budget already exists for this category and period'}), 409
    
    budget = Budget(
        user_id=request.user_id,
        category_id=data['category_id'],
        amount_limit=data['amount_limit'],
        period=data.get('period', 'monthly'),
        year=data.get('year', now.year),
        month=data.get('month', now.month),
        alert_threshold=data.get('alert_threshold', 80)
    )
    
    db.session.add(budget)
    db.session.commit()
    
    return jsonify({
        'message': 'Budget created',
        'budget_id': budget.id
    }), 201

@bp.route('/<int:budget_id>', methods=['PUT'])
@token_required
@validate_request_json()
def update_budget(budget_id):
    """Update budget"""
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=request.user_id
    ).first()
    
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    data = request.get_json()
    
    if 'amount_limit' in data:
        budget.amount_limit = data['amount_limit']
    if 'alert_threshold' in data:
        budget.alert_threshold = data['alert_threshold']
    
    budget.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Budget updated'}), 200

@bp.route('/<int:budget_id>', methods=['DELETE'])
@token_required
def delete_budget(budget_id):
    """Delete budget"""
    budget = Budget.query.filter_by(
        id=budget_id,
        user_id=request.user_id
    ).first()
    
    if not budget:
        return jsonify({'error': 'Budget not found'}), 404
    
    db.session.delete(budget)
    db.session.commit()
    
    return jsonify({'message': 'Budget deleted'}), 200
