"""
Advanced Financial Features API Routes
Loan tracking, investments, subscriptions, net worth
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Loan, Investment, Subscription, Goal
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime
from ml_models.calculators import (
    EMICalculator, NetWorthCalculator, 
    DebtPayoffPlanner, SIPCalculator
)

bp = Blueprint('advanced', __name__, url_prefix='/api/advanced')

# Loan Management
@bp.route('/loans', methods=['GET'])
@token_required
def get_loans():
    """Get all loans"""
    loans = Loan.query.filter_by(user_id=request.user_id).all()
    
    return jsonify({
        'loans': [
            {
                'id': loan.id,
                'name': loan.loan_name,
                'type': loan.loan_type,
                'principal': loan.principal_amount,
                'rate': loan.interest_rate,
                'tenure': loan.tenure_months,
                'emi': loan.emi_amount,
                'remaining': loan.remaining_amount,
                'status': loan.status
            }
            for loan in loans
        ]
    }), 200

@bp.route('/loans', methods=['POST'])
@token_required
@validate_request_json()
def create_loan():
    """Create new loan"""
    data = request.get_json()
    
    required = ['loan_name', 'loan_type', 'principal_amount', 'interest_rate', 'tenure_months']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Calculate EMI
    emi = EMICalculator.calculate_emi(
        data['principal_amount'],
        data['interest_rate'],
        data['tenure_months']
    )
    
    loan = Loan(
        user_id=request.user_id,
        loan_name=data['loan_name'],
        loan_type=data['loan_type'],
        principal_amount=data['principal_amount'],
        interest_rate=data['interest_rate'],
        tenure_months=data['tenure_months'],
        start_date=datetime.fromisoformat(data.get('start_date', datetime.utcnow().isoformat())),
        remaining_amount=data['principal_amount'],
        emi_amount=emi
    )
    
    db.session.add(loan)
    db.session.commit()
    
    return jsonify({
        'message': 'Loan created',
        'loan_id': loan.id,
        'emi': emi
    }), 201

@bp.route('/loans/<int:loan_id>/emi-schedule', methods=['GET'])
@token_required
def get_emi_schedule(loan_id):
    """Get EMI amortization schedule"""
    loan = Loan.query.filter_by(id=loan_id, user_id=request.user_id).first()
    
    if not loan:
        return jsonify({'error': 'Loan not found'}), 404
    
    schedule = EMICalculator.get_amortization_schedule(
        loan.principal_amount,
        loan.interest_rate,
        loan.tenure_months
    )
    
    return jsonify({
        'loan': loan.loan_name,
        'schedule': schedule
    }), 200

@bp.route('/loans/<int:loan_id>/payoff-plan', methods=['GET'])
@token_required
def get_payoff_plan(loan_id):
    """Get debt payoff plan"""
    loans = Loan.query.filter_by(user_id=request.user_id, status='active').all()
    
    debt_list = [
        {
            'name': l.loan_name,
            'balance': l.remaining_amount,
            'rate': l.interest_rate,
            'min_payment': l.emi_amount
        }
        for l in loans
    ]
    
    timeline = DebtPayoffPlanner.get_payoff_timeline(debt_list)
    
    return jsonify({'payoff_timeline': timeline}), 200

# Investment Management
@bp.route('/investments', methods=['GET'])
@token_required
def get_investments():
    """Get all investments"""
    investments = Investment.query.filter_by(user_id=request.user_id).all()
    
    total_invested = sum(inv.initial_amount for inv in investments)
    total_value = sum(inv.current_value for inv in investments)
    returns = total_value - total_invested
    
    return jsonify({
        'investments': [
            {
                'id': inv.id,
                'name': inv.investment_name,
                'type': inv.investment_type,
                'initial': inv.initial_amount,
                'current_value': inv.current_value,
                'return': inv.current_value - inv.initial_amount,
                'return_percentage': ((inv.current_value - inv.initial_amount) / inv.initial_amount * 100) if inv.initial_amount > 0 else 0
            }
            for inv in investments
        ],
        'total_invested': total_invested,
        'total_value': total_value,
        'total_returns': returns,
        'return_percentage': (returns / total_invested * 100) if total_invested > 0 else 0
    }), 200

@bp.route('/investments', methods=['POST'])
@token_required
@validate_request_json()
def create_investment():
    """Create new investment"""
    data = request.get_json()
    
    required = ['investment_name', 'investment_type', 'initial_amount']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    investment = Investment(
        user_id=request.user_id,
        investment_name=data['investment_name'],
        investment_type=data['investment_type'],
        initial_amount=data['initial_amount'],
        current_value=data['initial_amount'],
        investment_date=datetime.fromisoformat(data.get('investment_date', datetime.utcnow().isoformat())),
        quantity=data.get('quantity'),
        price_per_unit=data.get('price_per_unit'),
        notes=data.get('notes')
    )
    
    db.session.add(investment)
    db.session.commit()
    
    return jsonify({
        'message': 'Investment created',
        'investment_id': investment.id
    }), 201

# SIP Calculator
@bp.route('/sip/calculate', methods=['POST'])
@token_required
@validate_request_json()
def calculate_sip():
    """Calculate SIP returns"""
    data = request.get_json()
    
    required = ['monthly_investment', 'annual_return', 'years']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    result = SIPCalculator.calculate_sip_value(
        data['monthly_investment'],
        data['annual_return'],
        data['years']
    )
    
    return jsonify(result), 200

# Subscription Management
@bp.route('/subscriptions', methods=['GET'])
@token_required
def get_subscriptions():
    """Get all subscriptions"""
    subscriptions = Subscription.query.filter_by(user_id=request.user_id).all()
    
    monthly_cost = 0
    for sub in subscriptions:
        if sub.billing_cycle == 'monthly':
            monthly_cost += sub.amount
        elif sub.billing_cycle == 'yearly':
            monthly_cost += sub.amount / 12
        elif sub.billing_cycle == 'weekly':
            monthly_cost += (sub.amount * 52) / 12
    
    return jsonify({
        'subscriptions': [
            {
                'id': sub.id,
                'name': sub.service_name,
                'amount': sub.amount,
                'cycle': sub.billing_cycle,
                'status': sub.status,
                'next_renewal': sub.renewal_date.isoformat() if sub.renewal_date else None
            }
            for sub in subscriptions
        ],
        'total_monthly_cost': monthly_cost
    }), 200

@bp.route('/subscriptions', methods=['POST'])
@token_required
@validate_request_json()
def create_subscription():
    """Create new subscription"""
    data = request.get_json()
    
    required = ['service_name', 'amount', 'billing_cycle']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    subscription = Subscription(
        user_id=request.user_id,
        service_name=data['service_name'],
        amount=data['amount'],
        billing_cycle=data['billing_cycle'],
        start_date=datetime.fromisoformat(data.get('start_date', datetime.utcnow().isoformat())),
        category=data.get('category'),
        auto_renew=data.get('auto_renew', True)
    )
    
    db.session.add(subscription)
    db.session.commit()
    
    return jsonify({
        'message': 'Subscription created',
        'subscription_id': subscription.id
    }), 201

# Goals Management
@bp.route('/goals', methods=['GET'])
@token_required
def get_goals():
    """Get all goals"""
    goals = Goal.query.filter_by(user_id=request.user_id).all()
    
    return jsonify({
        'goals': [
            {
                'id': goal.id,
                'name': goal.goal_name,
                'type': goal.goal_type,
                'target': goal.target_amount,
                'current': goal.current_amount,
                'progress': (goal.current_amount / goal.target_amount * 100) if goal.target_amount > 0 else 0,
                'target_date': goal.target_date.isoformat() if goal.target_date else None
            }
            for goal in goals
        ]
    }), 200

@bp.route('/goals', methods=['POST'])
@token_required
@validate_request_json()
def create_goal():
    """Create new financial goal"""
    data = request.get_json()
    
    required = ['goal_name', 'goal_type', 'target_amount']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400
    
    goal = Goal(
        user_id=request.user_id,
        goal_name=data['goal_name'],
        goal_type=data['goal_type'],
        target_amount=data['target_amount'],
        target_date=datetime.fromisoformat(data['target_date']) if 'target_date' in data else None,
        description=data.get('description')
    )
    
    db.session.add(goal)
    db.session.commit()
    
    return jsonify({
        'message': 'Goal created',
        'goal_id': goal.id
    }), 201

@bp.route('/net-worth', methods=['GET'])
@token_required
def get_net_worth():
    """Calculate current net worth"""
    from backend.models import Account
    
    # Get total account balance
    total_assets = 0
    accounts = Account.query.filter_by(user_id=request.user_id).all()
    for account in accounts:
        total_assets += account.balance
    
    # Get investment values
    investments = Investment.query.filter_by(user_id=request.user_id).all()
    total_assets += sum(inv.current_value for inv in investments)
    
    # Get goal savings
    goals = Goal.query.filter_by(user_id=request.user_id).all()
    total_assets += sum(goal.current_amount for goal in goals)
    
    # Get liabilities (loans)
    loans = Loan.query.filter_by(user_id=request.user_id, status='active').all()
    total_liabilities = sum(loan.remaining_amount for loan in loans)
    
    net_worth = total_assets - total_liabilities
    
    return jsonify({
        'assets': total_assets,
        'liabilities': total_liabilities,
        'net_worth': net_worth,
        'breakdown': {
            'accounts': sum(acc.balance for acc in accounts),
            'investments': sum(inv.current_value for inv in investments),
            'goals': sum(goal.current_amount for goal in goals),
            'loans': total_liabilities
        }
    }), 200
