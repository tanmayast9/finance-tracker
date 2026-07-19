"""
API routes for category management
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models import Category
from backend.utils.auth import token_required
from backend.utils.helpers import validate_request_json
from datetime import datetime

bp = Blueprint('categories', __name__, url_prefix='/api/categories')

# Default categories
DEFAULT_EXPENSE_CATEGORIES = [
    {'name': 'Food & Dining', 'icon': '🍽️', 'color': '#FF6B6B'},
    {'name': 'Transportation', 'icon': '🚗', 'color': '#4ECDC4'},
    {'name': 'Shopping', 'icon': '🛍️', 'color': '#FFE66D'},
    {'name': 'Entertainment', 'icon': '🎬', 'color': '#95E1D3'},
    {'name': 'Bills & Utilities', 'icon': '💡', 'color': '#F38181'},
    {'name': 'Health & Fitness', 'icon': '💪', 'color': '#AA96DA'},
    {'name': 'Education', 'icon': '📚', 'color': '#FCBAD3'},
    {'name': 'Travel', 'icon': '✈️', 'color': '#A8E6CF'},
    {'name': 'Subscriptions', 'icon': '📺', 'color': '#FFD3B6'},
    {'name': 'Other', 'icon': '📌', 'color': '#CCCCCC'}
]

DEFAULT_INCOME_CATEGORIES = [
    {'name': 'Salary', 'icon': '💼', 'color': '#2ECC71'},
    {'name': 'Freelance', 'icon': '💻', 'color': '#3498DB'},
    {'name': 'Bonus', 'icon': '🎁', 'color': '#F39C12'},
    {'name': 'Investment Returns', 'icon': '📈', 'color': '#27AE60'},
    {'name': 'Refund', 'icon': '↩️', 'color': '#E74C3C'},
    {'name': 'Other', 'icon': '📌', 'color': '#CCCCCC'}
]

@bp.route('/expense', methods=['GET'])
@token_required
def get_expense_categories():
    """Get expense categories for user"""
    categories = Category.query.filter_by(
        user_id=request.user_id,
        category_type='expense'
    ).all()
    
    return jsonify({
        'categories': [
            {
                'id': cat.id,
                'name': cat.name,
                'icon': cat.icon,
                'color': cat.color,
                'is_custom': cat.is_custom
            }
            for cat in categories
        ]
    }), 200

@bp.route('/income', methods=['GET'])
@token_required
def get_income_categories():
    """Get income categories for user"""
    categories = Category.query.filter_by(
        user_id=request.user_id,
        category_type='income'
    ).all()
    
    return jsonify({
        'categories': [
            {
                'id': cat.id,
                'name': cat.name,
                'icon': cat.icon,
                'color': cat.color,
                'is_custom': cat.is_custom
            }
            for cat in categories
        ]
    }), 200

@bp.route('/', methods=['POST'])
@token_required
@validate_request_json()
def create_category():
    """Create custom category"""
    data = request.get_json()
    
    required_fields = ['name', 'category_type']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if category already exists
    existing = Category.query.filter_by(
        user_id=request.user_id,
        name=data['name'],
        category_type=data['category_type']
    ).first()
    
    if existing:
        return jsonify({'error': 'Category already exists'}), 409
    
    category = Category(
        user_id=request.user_id,
        name=data['name'],
        description=data.get('description', ''),
        category_type=data['category_type'],
        icon=data.get('icon', '📌'),
        color=data.get('color', '#CCCCCC'),
        is_custom=True
    )
    
    db.session.add(category)
    db.session.commit()
    
    return jsonify({
        'message': 'Category created',
        'category_id': category.id
    }), 201

@bp.route('/<int:category_id>', methods=['PUT'])
@token_required
@validate_request_json()
def update_category(category_id):
    """Update category"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=request.user_id
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    data = request.get_json()
    
    if 'name' in data:
        category.name = data['name']
    if 'description' in data:
        category.description = data['description']
    if 'icon' in data:
        category.icon = data['icon']
    if 'color' in data:
        category.color = data['color']
    
    db.session.commit()
    
    return jsonify({'message': 'Category updated'}), 200

@bp.route('/<int:category_id>', methods=['DELETE'])
@token_required
def delete_category(category_id):
    """Delete custom category"""
    category = Category.query.filter_by(
        id=category_id,
        user_id=request.user_id
    ).first()
    
    if not category:
        return jsonify({'error': 'Category not found'}), 404
    
    if not category.is_custom:
        return jsonify({'error': 'Cannot delete default category'}), 403
    
    db.session.delete(category)
    db.session.commit()
    
    return jsonify({'message': 'Category deleted'}), 200

@bp.route('/init-defaults', methods=['POST'])
@token_required
def init_default_categories():
    """Initialize default categories for user (adds missing expense/income categories)"""
    created = False
    
    # Add default expense categories if user has none
    has_expense = Category.query.filter_by(user_id=request.user_id, category_type='expense').first()
    if not has_expense:
        for cat_data in DEFAULT_EXPENSE_CATEGORIES:
            category = Category(
                user_id=request.user_id,
                name=cat_data['name'],
                category_type='expense',
                icon=cat_data['icon'],
                color=cat_data['color'],
                is_custom=False
            )
            db.session.add(category)
        created = True
    
    # Add default income categories if user has none
    has_income = Category.query.filter_by(user_id=request.user_id, category_type='income').first()
    if not has_income:
        for cat_data in DEFAULT_INCOME_CATEGORIES:
            category = Category(
                user_id=request.user_id,
                name=cat_data['name'],
                category_type='income',
                icon=cat_data['icon'],
                color=cat_data['color'],
                is_custom=False
            )
            db.session.add(category)
        created = True
    
    if created:
        db.session.commit()
        return jsonify({'message': 'Default categories initialized'}), 201
    return jsonify({'message': 'Categories already initialized'}), 200
