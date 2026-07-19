from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField, SelectField, TextAreaField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional
from datetime import datetime
from enhanced_models import User, ProfileType, AccountType, TransactionType, PaymentMode, InvestmentType

class LoginForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', [DataRequired()])
    submit = SubmitField('Login')

class SignupForm(FlaskForm):
    username = StringField('Username', [DataRequired(), Length(min=4, max=20)])
    email = StringField('Email', [DataRequired(), Email()])
    password = PasswordField('Password', [DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', [
        DataRequired(), 
        EqualTo('password', message='Passwords must match')
    ])
    profile_type = SelectField('Profile Type', choices=[(t.name, t.value.title()) for t in ProfileType], default=ProfileType.PERSONAL.name)
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValueError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValueError('Email already registered. Please use a different one.')

class ProfileSetupForm(FlaskForm):
    monthly_salary = FloatField('Monthly Salary (₹)', [DataRequired(), NumberRange(min=0)])
    profile_type = SelectField('Profile Type', choices=[(t.name, t.value.title()) for t in ProfileType])
    pin_code = StringField('PIN Code (4 digits)', [Length(min=4, max=4)], description='Optional 4-digit PIN for security')
    submit = SubmitField('Save Profile')

class BankAccountForm(FlaskForm):
    account_name = StringField('Account Name', [DataRequired(), Length(max=100)])
    account_type = SelectField('Account Type', choices=[(t.name, t.value.title().replace('_', ' ')) for t in AccountType])
    bank_name = StringField('Bank Name', [DataRequired(), Length(max=100)])
    account_number = StringField('Account Number', [DataRequired(), Length(max=50)])
    balance = FloatField('Initial Balance', [DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Account')

class TransactionForm(FlaskForm):
    amount = FloatField('Amount', [DataRequired(), NumberRange(min=0.01)])
    transaction_type = SelectField('Type', choices=[(t.name, t.value.title()) for t in TransactionType])
    category = StringField('Category', [DataRequired(), Length(max=50)])
    description = TextAreaField('Description', [Optional()])
    payment_mode = SelectField('Payment Mode', choices=[(m.name, m.value.title().replace('_', ' ')) for m in PaymentMode])
    account_id = SelectField('Account', coerce=int, validators=[Optional()])
    date = DateField('Date', [DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Add Transaction')

class BudgetForm(FlaskForm):
    category = StringField('Category', [DataRequired(), Length(max=50)])
    daily_limit = FloatField('Daily Limit (₹)', [DataRequired(), NumberRange(min=0)])
    monthly_limit = FloatField('Monthly Limit (₹)', [DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Set Budget')

class LoanForm(FlaskForm):
    loan_name = StringField('Loan Name', [DataRequired(), Length(max=100)])
    principal_amount = FloatField('Principal Amount', [DataRequired(), NumberRange(min=0)])
    interest_rate = FloatField('Interest Rate (%)', [DataRequired(), NumberRange(min=0, max=100)])
    tenure_months = IntegerField('Tenure (Months)', [DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Add Loan')

class InvestmentForm(FlaskForm):
    investment_name = StringField('Investment Name', [DataRequired(), Length(max=100)])
    investment_type = SelectField('Type', choices=[(t.value, t.value.title()) for t in InvestmentType])
    invested_amount = FloatField('Invested Amount', [DataRequired(), NumberRange(min=0)])
    current_value = FloatField('Current Value', [NumberRange(min=0)])
    quantity = FloatField('Quantity', [NumberRange(min=0)])
    purchase_date = DateField('Purchase Date', [DataRequired()])
    submit = SubmitField('Add Investment')

class SubscriptionForm(FlaskForm):
    subscription_name = StringField('Subscription Name', [DataRequired(), Length(max=100)])
    category = StringField('Category', [DataRequired(), Length(max=50)])
    amount = FloatField('Amount', [DataRequired(), NumberRange(min=0)])
    billing_cycle = SelectField('Billing Cycle', choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('quarterly', 'Quarterly'),
        ('weekly', 'Weekly')
    ])
    next_payment_date = DateField('Next Payment Date', [DataRequired()])
    submit = SubmitField('Add Subscription')

class BudgetGoalForm(FlaskForm):
    goal_name = StringField('Goal Name', [DataRequired(), Length(max=100)])
    target_amount = FloatField('Target Amount', [DataRequired(), NumberRange(min=0)])
    category = StringField('Category', [DataRequired(), Length(max=50)])
    target_date = DateField('Target Date', [DataRequired()])
    submit = SubmitField('Add Goal')

class TransactionFilterForm(FlaskForm):
    start_date = DateField('Start Date', [Optional()])
    end_date = DateField('End Date', [Optional()])
    category = StringField('Category', [Optional()])
    min_amount = FloatField('Min Amount', [Optional(), NumberRange(min=0)])
    max_amount = FloatField('Max Amount', [Optional(), NumberRange(min=0)])
    account_id = SelectField('Account', coerce=int, validators=[Optional()])
    transaction_type = SelectField('Type', choices=[('', 'All')] + [(t.value, t.value.title()) for t in TransactionType])
    submit = SubmitField('Filter')
