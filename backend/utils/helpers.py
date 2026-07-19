"""
General utility functions
"""

import json
from datetime import datetime, date
from functools import wraps
from flask import request, jsonify

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

def validate_request_json(schema=None):
    """
    Decorator to validate JSON request against a schema
    
    Args:
        schema (dict, optional): Schema to validate against. If None, only checks if request is JSON.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request is JSON
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
                
            # If no schema provided, just continue
            if schema is None:
                return f(*args, **kwargs)
                
            # Get JSON data
            data = request.get_json()
            
            # Validate required fields
            for field, config in schema.items():
                is_required = config.get('required', False)
                field_type = config.get('type')
                default = config.get('default')
                
                # Check required fields
                if is_required and field not in data:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
                    
                # Set default values if field is missing but not required
                if field not in data and not is_required and default is not None:
                    data[field] = default
                    
                # Skip validation if field is not in data and not required
                if field not in data:
                    continue
                    
                # Type checking
                if field_type and not isinstance(data[field], {
                    'string': str,
                    'number': (int, float),
                    'integer': int,
                    'boolean': bool,
                    'array': list,
                    'object': dict
                }.get(field_type, object)):
                    return jsonify({
                        'error': f'Field {field} must be of type {field_type}'
                    }), 400
                    
                # Regex validation
                if 'regex' in config and field_type == 'string':
                    import re
                    if not re.match(config['regex'], str(data[field])):
                        return jsonify({
                            'error': f'Field {field} has invalid format'
                        }), 400
                        
                # Min length validation
                if 'min_length' in config and field_type == 'string':
                    if len(str(data[field])) < config['min_length']:
                        return jsonify({
                            'error': f'Field {field} must be at least {config["min_length"]} characters long'
                        }), 400
            
            # Add validated data to kwargs
            kwargs['validated_data'] = data
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator

def paginate_query(query, page=1, per_page=20):
    """Paginate database query"""
    total = query.count()
    items = query.paginate(page=page, per_page=per_page, error_out=False).items
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    }

def calculate_savings_rate(income, expense):
    """Calculate savings rate percentage"""
    if income == 0:
        return 0
    return ((income - expense) / income) * 100

def format_currency(amount, currency='USD'):
    """Format amount as currency"""
    currency_symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'INR': '₹',
        'JPY': '¥',
        'CAD': '$',
        'AUD': '$',
        'CHF': 'Fr',
        'CNY': '¥',
        'SGD': '$',
        'AED': 'د.إ',
        'ZAR': 'R',
        'BRL': 'R$',
        'MXN': '$',
        'KRW': '₩',
        'PLN': 'zł',
        'SEK': 'kr',
        'NOK': 'kr',
        'DKK': 'kr',
        'THB': '฿',
        'PHP': '₱',
        'IDR': 'Rp',
    }
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def get_month_name(month):
    """Get month name from number"""
    months = ['', 'January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    return months[month] if 1 <= month <= 12 else ''

def get_date_range_for_period(period_type, year=None, month=None):
    """Get start and end dates for a period"""
    from datetime import datetime, timedelta
    
    today = datetime.now().date()
    
    if period_type == 'monthly':
        if month is None:
            month = today.month
        if year is None:
            year = today.year
        
        start = date(year, month, 1)
        if month == 12:
            end = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end = date(year, month + 1, 1) - timedelta(days=1)
    
    elif period_type == 'yearly':
        if year is None:
            year = today.year
        start = date(year, 1, 1)
        end = date(year, 12, 31)
    
    elif period_type == 'weekly':
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    
    elif period_type == 'daily':
        start = end = today
    
    else:
        start = end = today
    
    return start, end
