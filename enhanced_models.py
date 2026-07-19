from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum

db = SQLAlchemy()

class ProfileType(Enum):
    PERSONAL = "personal"
    BUSINESS = "business"
    FAMILY = "family"

class AccountType(Enum):
    SAVINGS = "savings"
    CURRENT = "current"
    CREDIT_CARD = "credit_card"
    INVESTMENT = "investment"

class TransactionType(Enum):
    INCOME = "income"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class PaymentMode(Enum):
    CASH = "cash"
    DEBIT_CARD = "debit_card"
    CREDIT_CARD = "credit_card"
    UPI = "upi"
    NET_BANKING = "net_banking"
    CHEQUE = "cheque"
    OTHER = "other"

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Profile Information
    profile_type = db.Column(db.Enum(ProfileType), default=ProfileType.PERSONAL)
    monthly_salary = db.Column(db.Float, default=0.0)
    pin_code = db.Column(db.String(4))  # For PIN lock
    
    # Relationships
    accounts = db.relationship('BankAccount', backref='user', lazy=True, cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', backref='user', lazy=True, cascade='all, delete-orphan')
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade='all, delete-orphan')
    loans = db.relationship('Loan', backref='user', lazy=True, cascade='all, delete-orphan')
    investments = db.relationship('Investment', backref='user', lazy=True, cascade='all, delete-orphan')
    subscriptions = db.relationship('Subscription', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('BudgetGoal', backref='user', lazy=True, cascade='all, delete-orphan')
    calculations = db.relationship('Calculation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_pin(self, pin):
        self.pin_code = generate_password_hash(str(pin))
    
    def check_pin(self, pin):
        if not self.pin_code:
            return False
        return check_password_hash(self.pin_code, str(pin))

class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(50), nullable=False)
    balance = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    transactions = db.relationship('Transaction', foreign_keys='Transaction.account_id', backref='account', lazy=True)

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=False)
    
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    payment_mode = db.Column(db.Enum(PaymentMode), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # For transfers
    to_account_id = db.Column(db.Integer, db.ForeignKey('bank_accounts.id'), nullable=True)
    
    def __repr__(self):
        return f'<Transaction {self.transaction_type.value}: ₹{self.amount}>'

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    # Limits
    daily_limit = db.Column(db.Float, default=0.0)
    monthly_limit = db.Column(db.Float, default=0.0)
    
    # Current spending
    daily_spent = db.Column(db.Float, default=0.0)
    monthly_spent = db.Column(db.Float, default=0.0)
    
    # Reset tracking
    last_daily_reset = db.Column(db.DateTime, default=datetime.utcnow)
    last_monthly_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    loan_name = db.Column(db.String(100), nullable=False)
    principal_amount = db.Column(db.Float, nullable=False)
    interest_rate = db.Column(db.Float, nullable=False)
    tenure_months = db.Column(db.Integer, nullable=False)
    
    # Current status
    remaining_balance = db.Column(db.Float, nullable=False)
    emi_amount = db.Column(db.Float, nullable=False)
    next_payment_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InvestmentType(Enum):
    STOCKS = "stocks"
    MUTUAL_FUNDS = "mutual_funds"
    CRYPTO = "crypto"
    FIXED_DEPOSIT = "fixed_deposit"
    OTHER = "other"

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    investment_name = db.Column(db.String(100), nullable=False)
    investment_type = db.Column(db.Enum(InvestmentType), nullable=False)
    
    # Financial data
    invested_amount = db.Column(db.Float, nullable=False)
    current_value = db.Column(db.Float, default=0.0)
    quantity = db.Column(db.Float, default=0.0)
    
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    subscription_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(20), nullable=False)  # monthly, yearly, etc.
    
    next_payment_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class BudgetGoal(db.Model):
    __tablename__ = 'budget_goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    
    target_date = db.Column(db.DateTime, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Calculation(db.Model):
    __tablename__ = 'calculations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    calculator_type = db.Column(db.String(50), nullable=False)
    input_data = db.Column(db.Text, nullable=False)
    result_data = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
