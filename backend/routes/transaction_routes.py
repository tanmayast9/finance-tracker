"""
API routes for transaction management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Transaction, Category, Account
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime
from sqlalchemy import and_, or_

bp = Blueprint('transactions', __name__, url_prefix='/api/transactions')

@bp.route('/', methods=['GET'])
@token_required
def get_transactions():
    """Get all transactions for user"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    transaction_type = request.args.get('type')  # expense, income, transfer, or all
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(user_id=request.user_id)
    
    if transaction_type and transaction_type != 'all':
        query = query.filter_by(transaction_type=transaction_type)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Transaction.description.ilike(search_term),
                Transaction.notes.ilike(search_term)
            )
        )
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.transaction_date.between(start, end))
    
    transactions = query.order_by(Transaction.transaction_date.desc()).paginate(
        page=page, per_page=per_page
    )
    
    return jsonify({
        'transactions': [
            {
                'id': trans.id,
                'type': trans.transaction_type,
                'amount': trans.amount,
                'category': trans.category.name,
                'description': trans.description,
                'notes': trans.notes,
                'date': trans.transaction_date.isoformat(),
                'account': trans.account.account_name,
                'predicted_category': trans.predicted_category,
                'prediction_confidence': trans.prediction_confidence
            }
            for trans in transactions.items
        ],
        'total': transactions.total,
        'page': page,
        'per_page': per_page
    }), 200

@bp.route('/<int:transaction_id>', methods=['GET'])
@token_required
def get_transaction(transaction_id):
    """Get transaction details"""
    transaction = Transaction.query.filter_by(
        id=transaction_id,
        user_id=request.user_id
    ).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    return jsonify({
        'id': transaction.id,
        'type': transaction.transaction_type,
        'amount': transaction.amount,
        'category': transaction.category.name,
        'description': transaction.description,
        'notes': transaction.notes,
        'date': transaction.transaction_date.isoformat(),
        'account': transaction.account.account_name,
        'tags': transaction.tags,
        'receipt_url': transaction.receipt_url
    }), 200

@bp.route('/export', methods=['GET'])
@token_required
def export_transactions():
    """Export transactions as CSV"""
    import csv
    from io import StringIO
    from flask import make_response
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    query = Transaction.query.filter_by(user_id=request.user_id)
    
    if start_date and end_date:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        query = query.filter(Transaction.transaction_date.between(start, end))
    
    transactions = query.order_by(Transaction.transaction_date.desc()).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Date', 'Type', 'Amount', 'Category', 'Description', 'Account', 'Notes'
    ])
    
    for trans in transactions:
        writer.writerow([
            trans.transaction_date.isoformat(),
            trans.transaction_type,
            trans.amount,
            trans.category.name,
            trans.description,
            trans.account.account_name,
            trans.notes
        ])
    
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=transactions.csv'
    response.headers['Content-Type'] = 'text/csv'
    
    return response

@bp.route('/recurring', methods=['GET'])
@token_required
def get_recurring_transactions():
    """Get recurring transactions"""
    transactions = Transaction.query.filter_by(
        user_id=request.user_id,
        is_recurring=True
    ).all()
    
    return jsonify({
        'recurring_transactions': [
            {
                'id': trans.id,
                'amount': trans.amount,
                'category': trans.category.name,
                'frequency': trans.recurring_frequency,
                'next_date': (trans.transaction_date).isoformat()
            }
            for trans in transactions
        ]
    }), 200
