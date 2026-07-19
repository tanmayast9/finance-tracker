"""
API routes for analytics and insights
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Transaction, Category, FinancialHealth, User, Goal, Loan, Investment
from backend.utils.auth import token_required
from datetime import datetime, timedelta
from sqlalchemy import func, and_

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')

@bp.route('/dashboard', methods=['GET'])
@token_required
def get_dashboard():
    """Get dashboard summary"""
    now = datetime.utcnow()
    start_of_month = datetime(now.year, now.month, 1)
    end_of_month = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month < 12 else datetime(now.year + 1, 1, 1) - timedelta(days=1)
    
    # Get month totals
    expenses = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= start_of_month,
            Transaction.transaction_date <= end_of_month
        )
    ).scalar() or 0
    
    income = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= start_of_month,
            Transaction.transaction_date <= end_of_month
        )
    ).scalar() or 0
    
    savings = income - expenses
    savings_rate = (savings / income * 100) if income > 0 else 0
    
    # Get account balances
    from backend.models import Account
    total_balance = db.session.query(func.sum(Account.balance)).filter(
        Account.user_id == request.user_id
    ).scalar() or 0
    
    # Get net worth
    net_worth = total_balance
    
    # Get latest transactions
    latest_transactions = Transaction.query.filter_by(
        user_id=request.user_id
    ).order_by(Transaction.transaction_date.desc()).limit(5).all()
    
    return jsonify({
        'month': now.month,
        'year': now.year,
        'income': float(income),
        'expenses': float(expenses),
        'savings': float(savings),
        'savings_rate': float(savings_rate),
        'account_balance': float(total_balance),
        'net_worth': float(net_worth),
        'latest_transactions': [
            {
                'id': trans.id,
                'type': trans.transaction_type,
                'amount': trans.amount,
                'category': trans.category.name,
                'description': trans.description,
                'date': trans.transaction_date.isoformat()
            }
            for trans in latest_transactions
        ]
    }), 200

@bp.route('/monthly-summary', methods=['GET'])
@token_required
def get_monthly_summary():
    """Get monthly expense/income summary"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    now = datetime.utcnow()
    if not year:
        year = now.year
    if not month:
        month = now.month
    
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    
    # Get expenses by category
    expense_by_cat = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end
        )
    ).group_by(Category.id, Category.name).all()
    
    # Get income by category
    income_by_cat = db.session.query(
        Category.name,
        func.sum(Transaction.amount)
    ).join(Transaction).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end
        )
    ).group_by(Category.id, Category.name).all()
    
    total_income = sum(amount for _, amount in income_by_cat) if income_by_cat else 0
    total_expense = sum(amount for _, amount in expense_by_cat) if expense_by_cat else 0
    
    return jsonify({
        'month': month,
        'year': year,
        'income': {
            'total': float(total_income),
            'by_category': [
                {'category': cat, 'amount': float(amount)}
                for cat, amount in income_by_cat
            ]
        },
        'expense': {
            'total': float(total_expense),
            'by_category': [
                {'category': cat, 'amount': float(amount)}
                for cat, amount in expense_by_cat
            ]
        },
        'savings': float(total_income - total_expense)
    }), 200

@bp.route('/category-analysis', methods=['GET'])
@token_required
def get_category_analysis():
    """Get detailed category-wise analysis"""
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    
    now = datetime.utcnow()
    if not year:
        year = now.year
    if not month:
        month = now.month
    
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end = datetime(year, month + 1, 1) - timedelta(days=1)
    
    categories = Category.query.filter_by(
        user_id=request.user_id,
        category_type='expense'
    ).all()
    
    analysis = []
    total_expense = 0
    
    for category in categories:
        spent = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == request.user_id,
                Transaction.category_id == category.id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end
            )
        ).scalar() or 0
        
        total_expense += spent
        
        analysis.append({
            'category': category.name,
            'amount': float(spent),
            'icon': category.icon,
            'color': category.color
        })
    
    # Calculate percentages
    for item in analysis:
        item['percentage'] = (item['amount'] / total_expense * 100) if total_expense > 0 else 0
    
    # Sort by amount descending
    analysis.sort(key=lambda x: x['amount'], reverse=True)
    
    return jsonify({
        'month': month,
        'year': year,
        'total': float(total_expense),
        'categories': analysis
    }), 200

@bp.route('/trends', methods=['GET'])
@token_required
def get_spending_trends():
    """Get spending trends for last 12 months"""
    months_back = request.args.get('months', 12, type=int)
    
    now = datetime.utcnow()
    trends = []
    
    for i in range(months_back - 1, -1, -1):
        target_month = now - timedelta(days=30*i)
        month = target_month.month
        year = target_month.year
        
        start = datetime(year, month, 1)
        if month == 12:
            end = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = datetime(year, month + 1, 1) - timedelta(days=1)
        
        expense = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == request.user_id,
                Transaction.transaction_type == 'expense',
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end
            )
        ).scalar() or 0
        
        income = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == request.user_id,
                Transaction.transaction_type == 'income',
                Transaction.transaction_date >= start,
                Transaction.transaction_date <= end
            )
        ).scalar() or 0
        
        trends.append({
            'month': month,
            'year': year,
            'expense': float(expense),
            'income': float(income),
            'savings': float(income - expense)
        })
    
    return jsonify({
        'months': months_back,
        'trends': trends
    }), 200

@bp.route('/health-score', methods=['GET'])
@token_required
def get_financial_health():
    """Calculate financial health score"""
    now = datetime.utcnow()
    start = datetime(now.year, now.month, 1)
    end = datetime(now.year, now.month + 1, 1) - timedelta(days=1) if now.month < 12 else datetime(now.year + 1, 1, 1) - timedelta(days=1)
    
    # Get totals
    income = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'income',
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end
        )
    ).scalar() or 0
    
    expense = db.session.query(func.sum(Transaction.amount)).filter(
        and_(
            Transaction.user_id == request.user_id,
            Transaction.transaction_type == 'expense',
            Transaction.transaction_date >= start,
            Transaction.transaction_date <= end
        )
    ).scalar() or 0
    
    savings = income - expense
    savings_rate = (savings / income * 100) if income > 0 else 0
    
    # Calculate health score (0-100)
    score = 50  # Base score
    
    # Savings rate impact
    if savings_rate > 30:
        score += 25
    elif savings_rate > 10:
        score += 15
    elif savings_rate > 0:
        score += 5
    
    # Expense ratio impact
    expense_ratio = (expense / income * 100) if income > 0 else 0
    if expense_ratio < 60:
        score += 15
    elif expense_ratio < 80:
        score += 5
    
    # Ensure score is within 0-100
    score = max(0, min(100, score))
    
    return jsonify({
        'health_score': float(score),
        'savings_rate': float(savings_rate),
        'expense_ratio': float(expense_ratio),
        'income': float(income),
        'expense': float(expense),
        'savings': float(savings),
        'insights': generate_insights(score, savings_rate, expense_ratio)
    }), 200

def generate_insights(score, savings_rate, expense_ratio):
    """Generate AI insights based on financial health"""
    insights = []
    
    if score >= 80:
        insights.append("Excellent financial health! Keep maintaining this discipline.")
    elif score >= 60:
        insights.append("Good financial health. Focus on increasing savings rate.")
    else:
        insights.append("Work on reducing expenses and increasing savings.")
    
    if savings_rate < 10:
        insights.append("Try to increase your savings rate to at least 10-15% of income.")
    
    if expense_ratio > 80:
        insights.append("Your expenses are high relative to income. Review discretionary spending.")
    
    return insights
