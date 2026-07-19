"""
Database Models for Finance Application
Defines all database tables and relationships
"""

from datetime import datetime
from backend.app import db
from sqlalchemy.dialects.mysql import JSON
import enum

class User(db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    phone_verified = db.Column(db.Boolean, default=False)
    profile_picture = db.Column(db.String(255))
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    theme_preference = db.Column(db.String(10), default='light')  # light or dark
    currency = db.Column(db.String(3), default='USD')
    monthly_income = db.Column(db.Float, default=0.0)
    salary_day = db.Column(db.Integer)  # 1-31, day of month salary is received
    two_factor_enabled = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    accounts = db.relationship('Account', backref='owner', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Account(db.Model):
    """Bank/Cash account model for multi-account support"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(120), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)  # bank, cash, credit_card, etc.
    balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(3), default='USD')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Account {self.account_name}>'

class Category(db.Model):
    """Expense/Income category model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_type = db.Column(db.String(20), nullable=False)  # expense, income
    icon = db.Column(db.String(50))
    color = db.Column(db.String(7))  # hex color
    is_custom = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transactions = db.relationship('Transaction', backref='category', lazy=True)
    budget = db.relationship('Budget', backref='category', uselist=False)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Transaction(db.Model):
    """Income/Expense transaction model"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # expense, income, transfer
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    receipt_url = db.Column(db.String(255))
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))  # daily, weekly, monthly, yearly
    tags = db.Column(JSON)
    predicted_category = db.Column(db.String(100))  # ML prediction
    prediction_confidence = db.Column(db.Float)
    
    def __repr__(self):
        return f'<Transaction {self.description}>'

class Budget(db.Model):
    """Monthly budget limits model"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount_limit = db.Column(db.Float, nullable=False)
    period = db.Column(db.String(20), default='monthly')  # monthly, yearly, custom
    month = db.Column(db.Integer)  # 1-12
    year = db.Column(db.Integer)
    alert_threshold = db.Column(db.Float, default=80)  # Alert at 80% spent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Budget {self.category_id}>'

class Goal(db.Model):
    """Savings goals model"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(120), nullable=False)
    goal_type = db.Column(db.String(50), nullable=False)  # savings, emergency_fund, investment, etc.
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.DateTime)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Goal {self.goal_name}>'

class Loan(db.Model):
    """Loan tracking model"""
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    loan_name = db.Column(db.String(120), nullable=False)
    loan_type = db.Column(db.String(50), nullable=False)  # personal, home, auto, education
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)  # Annual percentage
    tenure_months = db.Column(db.Integer)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    remaining_amount = db.Column(db.Float, nullable=False)
    emi_amount = db.Column(db.Float)
    emi_paid = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Loan {self.loan_name}>'

class Investment(db.Model):
    """Investment tracking model"""
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    investment_name = db.Column(db.String(120), nullable=False)
    investment_type = db.Column(db.String(50), nullable=False)  # stocks, mutual_funds, sip, crypto, bonds
    initial_amount = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, nullable=False)
    investment_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Float)
    price_per_unit = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Investment {self.investment_name}>'

class Subscription(db.Model):
    """Recurring subscription tracking model"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    service_name = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  # monthly, yearly, weekly
    start_date = db.Column(db.DateTime, nullable=False)
    renewal_date = db.Column(db.DateTime)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20), default='active')  # active, cancelled, paused
    auto_renew = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Subscription {self.service_name}>'

class FinancialHealth(db.Model):
    """Monthly financial health score model"""
    __tablename__ = 'financial_health'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    health_score = db.Column(db.Float)  # 0-100
    savings_rate = db.Column(db.Float)
    income_total = db.Column(db.Float)
    expense_total = db.Column(db.Float)
    savings_total = db.Column(db.Float)
    budget_adherence = db.Column(db.Float)  # % of budget followed
    analysis = db.Column(db.Text)  # AI analysis and recommendations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<FinancialHealth {self.user_id}>'

class Alert(db.Model):
    """Financial alerts and notifications model"""
    __tablename__ = 'alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    alert_type = db.Column(db.String(50), nullable=False)  # budget_exceeded, unusual_spending, etc.
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(20))  # low, medium, high
    is_read = db.Column(db.Boolean, default=False)
    action_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Alert {self.alert_type}>'

class AuditLog(db.Model):
    """Audit log for tracking all activities"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.Integer)
    changes = db.Column(JSON)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AuditLog {self.action}>'
