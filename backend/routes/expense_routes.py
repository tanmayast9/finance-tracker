"""
API routes for expense management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Transaction, Category, Budget, Account, Alert
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from backend.utils.ai_client import GeminiClient
from datetime import datetime, timedelta
from sqlalchemy import func, and_

bp = Blueprint('expenses', __name__, url_prefix='/api/expenses')
ai_client = GeminiClient()

@bp.route('/', methods=['GET'])
@token_required
def get_expenses():
    """Get all expenses for user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category_id = request.args.get('category_id', type=int)
    account_id = request.args.get('account_id', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(
        user_id=request.user_id,
        transaction_type='expense'
    )
    
    # Apply filters
    if category_id:
        query = query.filter_by(category_id=category_id)
    if account_id:
        query = query.filter_by(account_id=account_id)
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.transaction_date.between(start, end))
    
    expenses = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'expenses': [
            {
                'id': exp.id,
                'amount': exp.amount,
                'category': exp.category.name,
                'description': exp.description,
                'notes': exp.notes,
                'transaction_date': exp.transaction_date.isoformat(),
                'account': exp.account.account_name
            }
            for exp in expenses.items
        ],
        'total': expenses.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json()
def create_expense():
    """Create new expense"""
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
        transaction_type='expense',
        amount=data['amount'],
        description=data.get('description', ''),
        notes=data.get('notes', ''),
        transaction_date=datetime.fromisoformat(
            data.get('transaction_date', datetime.utcnow().isoformat())
        ),
        tags=data.get('tags', [])
    )
    
    # Update account balance
    account.balance -= data['amount']
    
    db.session.add(transaction)
    
    # Check budget alerts
    check_budget_alerts(request.user_id, data['category_id'])
    
    db.session.commit()
    
    return jsonify({
        'message': 'Expense recorded',
        'transaction_id': transaction.id
    }), 201

@bp.route('/<int:expense_id>', methods=['PUT'])
@token_required
@validate_request_json()
def update_expense(expense_id):
    """Update expense"""
    expense = Transaction.query.filter_by(
        id=expense_id,
        user_id=request.user_id,
        transaction_type='expense'
    ).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    data = request.get_json()
    old_amount = expense.amount
    
    if 'amount' in data:
        expense.amount = data['amount']
        # Update account balance
        expense.account.balance = expense.account.balance + old_amount - data['amount']
    
    if 'description' in data:
        expense.description = data['description']
    if 'notes' in data:
        expense.notes = data['notes']
    if 'category_id' in data:
        expense.category_id = data['category_id']
    
    expense.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Expense updated'}), 200

@bp.route('/<int:expense_id>', methods=['DELETE'])
@token_required
def delete_expense(expense_id):
    """Delete expense"""
    expense = Transaction.query.filter_by(
        id=expense_id,
        user_id=request.user_id,
        transaction_type='expense'
    ).first()
    
    if not expense:
        return jsonify({'error': 'Expense not found'}), 404
    
    # Refund amount to account
    expense.account.balance += expense.amount
    
    db.session.delete(expense)
    db.session.commit()
    
    return jsonify({'message': 'Expense deleted'}), 200

@bp.route('/daily-log', methods=['GET'])
@token_required
def get_daily_log():
    """Get daily expense log"""
    date_str = request.args.get('date')
    
    if date_str:
        target_date = datetime.fromisoformat(date_str).date()
    else:
        target_date = datetime.utcnow().date()
    
    start_of_day = datetime.combine(target_date, datetime.min.time())
    end_of_day = datetime.combine(target_date, datetime.max.time())
    
    expenses = Transaction.query.filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= start_of_day,
            Transaction.transaction_date <= end_of_day
        )
    ).all()
    
    total_spent = sum(exp.amount for exp in expenses)
    
    return jsonify({
        'date': target_date.isoformat(),
        'expenses': [
            {
                'id': exp.id,
                'amount': exp.amount,
                'category': exp.category.name,
                'description': exp.description,
                'time': exp.transaction_date.isoformat()
            }
            for exp in expenses
        ],
        'total_spent': total_spent
    }), 200

def check_budget_alerts(user_id, category_id):
    """Check if expense exceeds budget and create alert"""
    budget = Budget.query.filter_by(
        user_id=user_id,
        category_id=category_id
    ).first()
    
    if not budget:
        return
    
    # Calculate current month spending
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month < 12 else datetime(now.year + 1, 1, 1) - timedelta(days=1)
    
    spent = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == user_id,
            Transaction.category_id == category_id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= start_of_month,
            Transaction.transaction_date <= end_of_month
        )
    ).scalar() or 0
    
    percentage = (spent / budget.amount_limit * 100) if budget.amount_limit > 0 else 0
    
    if percentage > 100:
        # Create alert
        alert = Alert(
            user_id=user_id,
            alert_type='budget_exceeded',
            title=f'Budget exceeded for {Category.query.get(category_id).name}',
            message=f'You have exceeded your budget. Spent: ₹{spent:.2f}, Limit: ₹{budget.amount_limit:.2f}',
            severity='high'
        )
        db.session.add(alert)
    elif percentage > budget.alert_threshold:
        # Create warning alert
        alert = Alert(
            user_id=user_id,
            alert_type='budget_warning',
            title=f'Budget warning for {Category.query.get(category_id).name}',
            message=f'You have spent {percentage:.1f}% of your budget',
            severity='medium'
        )
        db.session.add(alert)
