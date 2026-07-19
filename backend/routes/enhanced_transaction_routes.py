"""
Enhanced transaction routes with additional features
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Transaction, Account, Category, Alert
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_, or_

bp = Blueprint('enhanced_transactions', __name__, url_prefix='/api/v2/transactions')

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json({
    'account_id': {'type': 'integer', 'required': True},
    'category_id': {'type': 'integer', 'required': True},
    'transaction_type': {'type': 'string', 'required': True, 'allowed': ['expense', 'income', 'transfer']},
    'amount': {'type': 'number', 'required': True, 'min': 0.01},
    'description': {'type': 'string', 'required': True},
    'transaction_date': {'type': 'string', 'required': False},
    'notes': {'type': 'string', 'required': False},
    'is_recurring': {'type': 'boolean', 'required': False},
    'recurring_frequency': {'type': 'string', 'required': False},
    'payment_method': {'type': 'string', 'required': False},
    'tags': {'type': 'list', 'required': False}
})
def create_transaction():
    """Create a new transaction with enhanced features"""
    data = request.get_json()
    user_id = request.user_id
    
    # Validate account
    account = Account.query.filter_by(
        id=data['account_id'],
        user_id=user_id
    ).first()
    
    if not account:
        return jsonify({'error': 'Account not found'}), 404
    
    # Validate category
    category = Category.query.filter_by(
        id=data['category_id'],
        user_id=user_id
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    # Parse transaction date or use current time
    transaction_date = datetime.fromisoformat(data.get('transaction_date')) if data.get('transaction_date') else datetime.utcnow()
    
    # Create transaction
    transaction = Transaction(
        user_id=user_id,
        account_id=data['account_id'],
        category_id=data['category_id'],
        transaction_type=data['transaction_type'],
        amount=data['amount'],
        description=data['description'],
        notes=data.get('notes'),
        transaction_date=transaction_date,
        is_recurring=data.get('is_recurring', False),
        recurring_frequency=data.get('recurring_frequency'),
        payment_method=data.get('payment_method'),
        tags=data.get('tags')
    )
    
    # Update account balance
    if data['transaction_type'] == 'expense':
        account.balance -= data['amount']
    elif data['transaction_type'] == 'income':
        account.balance += data['amount']
    # For transfers, we'll need a separate endpoint as it involves two accounts
    
    db.session.add(transaction)
    
    # Check for budget alerts
    check_budget_alerts(user_id, data['category_id'], data['amount'], transaction_date)
    
    # Check for large transaction alert
    check_large_transaction_alert(user_id, data['amount'], transaction)
    
    db.session.commit()
    
    return jsonify({
        'message': 'Transaction created successfully',
        'transaction': {
            'id': transaction.id,
            'amount': transaction.amount,
            'type': transaction.transaction_type,
            'description': transaction.description,
            'date': transaction.transaction_date.isoformat(),
            'category': category.name,
            'account_balance': account.balance
        }
    }), 201

def check_budget_alerts(user_id, category_id, amount, transaction_date):
    """Check if transaction exceeds budget and create alert if needed"""
    from datetime import date
    
    # Get current month and year
    current_month = transaction_date.month
    current_year = transaction_date.year
    
    # Check if there's a budget for this category and period
    budget = db.session.query(
        Budget
    ).filter(
        Budget.user_id == user_id,
        Budget.category_id == category_id,
        or_(
            and_(
                Budget.month == current_month,
                Budget.year == current_year
            ),
            Budget.period != 'monthly'
        )
    ).first()
    
    if not budget:
        return
    
    # Calculate total spent in this category for the period
    query = db.session.query(
        func.sum(Transaction.amount).label('total_spent')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.category_id == category_id,
        Transaction.transaction_type == 'expense'
    )
    
    if budget.period == 'monthly':
        query = query.filter(
            extract('month', Transaction.transaction_date) == current_month,
            extract('year', Transaction.transaction_date) == current_year
        )
    
    total_spent = query.scalar() or 0
    
    # Add current transaction amount
    total_spent += amount
    
    # Check if budget is exceeded
    if total_spent > budget.amount_limit:
        alert = Alert(
            user_id=user_id,
            alert_type='budget_exceeded',
            title=f'Budget Exceeded for {budget.category.name}',
            message=f'You have exceeded your {budget.period} budget of {budget.amount_limit} for {budget.category.name}.',
            severity='high',
            action_required=True
        )
        db.session.add(alert)
    # Check if approaching budget limit (80% threshold)
    elif total_spent >= (budget.amount_limit * 0.8):
        alert = Alert(
            user_id=user_id,
            alert_type='budget_warning',
            title=f'Approaching Budget Limit for {budget.category.name}',
            message=f'You have used {int((total_spent/budget.amount_limit)*100)}% of your {budget.period} budget for {budget.category.name}.',
            severity='medium'
        )
        db.session.add(alert)

def check_large_transaction_alert(user_id, amount, transaction):
    """Check if transaction is unusually large and create alert"""
    # Get user's average transaction amount
    avg_amount = db.session.query(
        func.avg(Transaction.amount)
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense'
    ).scalar() or 0
    
    # If transaction is 5x larger than average, create alert
    if avg_amount > 0 and amount > (avg_amount * 5):
        alert = Alert(
            user_id=user_id,
            alert_type='large_transaction',
            title='Large Transaction Detected',
            message=f'Large transaction of {amount} for {transaction.description} is significantly higher than your average transaction amount.',
            severity='medium'
        )
        db.session.add(alert)

@bp.route('/transfer', methods=['POST'])
@token_required
@validate_request_json({
    'from_account_id': {'type': 'integer', 'required': True},
    'to_account_id': {'type': 'integer', 'required': True},
    'amount': {'type': 'number', 'required': True, 'min': 0.01},
    'description': {'type': 'string', 'required': True},
    'transaction_date': {'type': 'string', 'required': False},
    'notes': {'type': 'string', 'required': False},
    'fee': {'type': 'number', 'required': False, 'min': 0}
})
def create_transfer():
    """Create a transfer between two accounts"""
    data = request.get_json()
    user_id = request.user_id
    
    # Validate accounts
    from_account = Account.query.filter_by(
        id=data['from_account_id'],
        user_id=user_id
    ).first()
    
    to_account = Account.query.filter_by(
        id=data['to_account_id'],
        user_id=user_id
    ).first()
    
    if not from_account or not to_account:
        return jsonify({'error': 'One or both accounts not found'}), 404
    
    if from_account.id == to_account.id:
        return jsonify({'error': 'Cannot transfer to the same account'}), 400
    
    # Check sufficient balance
    if from_account.balance < data['amount'] + data.get('fee', 0):
        return jsonify({'error': 'Insufficient balance'}), 400
    
    # Parse transaction date or use current time
    transaction_date = datetime.fromisoformat(data.get('transaction_date')) if data.get('transaction_date') else datetime.utcnow()
    
    # Get or create transfer category
    transfer_category = Category.query.filter_by(
        user_id=user_id,
        name='Transfer',
        category_type='transfer'
    ).first()
    
    if not transfer_category:
        transfer_category = Category(
            user_id=user_id,
            name='Transfer',
            category_type='transfer',
            is_custom=False
        )
        db.session.add(transfer_category)
        db.session.flush()  # Get the ID for the new category
    
    # Create withdrawal transaction
    withdrawal = Transaction(
        user_id=user_id,
        account_id=from_account.id,
        category_id=transfer_category.id,
        transaction_type='expense',
        amount=data['amount'] + data.get('fee', 0),
        description=f"Transfer to {to_account.account_name}: {data['description']}",
        notes=data.get('notes'),
        transaction_date=transaction_date,
        payment_method='transfer'
    )
    
    # Create deposit transaction
    deposit = Transaction(
        user_id=user_id,
        account_id=to_account.id,
        category_id=transfer_category.id,
        transaction_type='income',
        amount=data['amount'],
        description=f"Transfer from {from_account.account_name}: {data['description']}",
        notes=data.get('notes'),
        transaction_date=transaction_date,
        payment_method='transfer'
    )
    
    # Update account balances
    from_account.balance -= (data['amount'] + data.get('fee', 0))
    to_account.balance += data['amount']
    
    db.session.add_all([withdrawal, deposit])
    db.session.commit()
    
    return jsonify({
        'message': 'Transfer completed successfully',
        'from_account_balance': from_account.balance,
        'to_account_balance': to_account.balance
    }), 201

@bp.route('/recent', methods=['GET'])
@token_required
def get_recent_transactions():
    """Get recent transactions (last 5) for the dashboard"""
    transactions = Transaction.query.filter_by(
        user_id=request.user_id
    ).order_by(
        Transaction.transaction_date.desc()
    ).limit(5).all()
    
    return jsonify({
        'transactions': [{
            'id': t.id,
            'amount': t.amount,
            'type': t.transaction_type,
            'description': t.description,
            'date': t.transaction_date.isoformat(),
            'category': t.category.name if t.category else None,
            'account': t.account.account_name
        } for t in transactions]
    }), 200

@bp.route('/stats', methods=['GET'])
@token_required
def get_transaction_stats():
    """Get transaction statistics for dashboard"""
    user_id = request.user_id
    now = datetime.utcnow()
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Monthly income and expense totals
    monthly_totals = db.session.query(
        Transaction.transaction_type,
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_of_month,
        Transaction.transaction_date <= now,
        Transaction.transaction_type.in_(['income', 'expense'])
    ).group_by(
        Transaction.transaction_type
    ).all()
    
    # Category-wise spending
    category_spending = db.session.query(
        Category.name,
        func.sum(Transaction.amount).label('total')
    ).join(
        Category,
        Transaction.category_id == Category.id
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= start_of_month,
        Transaction.transaction_date <= now
    ).group_by(
        Category.name
    ).order_by(
        func.sum(Transaction.amount).desc()
    ).limit(5).all()
    
    # Payment method distribution
    payment_methods = db.session.query(
        Transaction.payment_method,
        func.sum(Transaction.amount).label('total'),
        func.count(Transaction.id).label('count')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date >= start_of_month,
        Transaction.transaction_date <= now
    ).group_by(
        Transaction.payment_method
    ).all()
    
    # Convert to dictionary for easier access
    totals = {t[0]: t[1] for t in monthly_totals}
    
    return jsonify({
        'monthly_income': totals.get('income', 0),
        'monthly_expenses': totals.get('expense', 0),
        'savings': totals.get('income', 0) - totals.get('expense', 0),
        'top_categories': [{'name': c[0], 'amount': c[1]} for c in category_spending],
        'payment_methods': [{
            'method': p[0] or 'other',
            'amount': p[1],
            'count': p[2]
        } for p in payment_methods]
    }), 200

@bp.route('/spending-trends', methods=['GET'])
@token_required
def get_spending_trends():
    """Get spending trends over time"""
    user_id = request.user_id
    now = datetime.utcnow()
    six_months_ago = (now - timedelta(days=180)).replace(day=1)
    
    # Get monthly spending for the last 6 months
    monthly_spending = db.session.query(
        extract('year', Transaction.transaction_date).label('year'),
        extract('month', Transaction.transaction_date).label('month'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= six_months_ago,
        Transaction.transaction_date <= now
    ).group_by(
        extract('year', Transaction.transaction_date),
        extract('month', Transaction.transaction_date)
    ).order_by(
        extract('year', Transaction.transaction_date).desc(),
        extract('month', Transaction.transaction_date).desc()
    ).all()
    
    # Get daily spending for the current month
    daily_spending = db.session.query(
        extract('day', Transaction.transaction_date).label('day'),
        func.sum(Transaction.amount).label('total')
    ).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_type == 'expense',
        Transaction.transaction_date >= now.replace(day=1),
        Transaction.transaction_date <= now
    ).group_by(
        extract('day', Transaction.transaction_date)
    ).order_by(
        extract('day', Transaction.transaction_date)
    ).all()
    
    return jsonify({
        'monthly_trends': [{
            'month': f"{int(m[0])}-{int(m[1]):02d}",
            'total': float(m[2]) if m[2] else 0.0
        } for m in monthly_spending],
        'daily_trends': [{
            'day': int(d[0]),
            'total': float(d[1]) if d[1] else 0.0
        } for d in daily_spending]
    }), 200
