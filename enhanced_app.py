from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
import json

from enhanced_models import db, User, BankAccount, Transaction, Budget, Loan, Investment, Subscription, BudgetGoal, Calculation, ProfileType
from enhanced_forms import (
    LoginForm, SignupForm, ProfileSetupForm, BankAccountForm, TransactionForm, 
    BudgetForm, LoanForm, InvestmentForm, SubscriptionForm, BudgetGoalForm, TransactionFilterForm
)
from config import Config
from ml_models.calculators import EMICalculator, InterestCalculator, SIPCalculator

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            
            # Check if profile is complete
            if user.monthly_salary == 0:
                flash('Please complete your profile setup', 'info')
                return redirect(url_for('profile_setup'))
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = SignupForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data,
            profile_type=ProfileType[form.profile_type.data]
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please complete your profile.', 'success')
        login_user(user)
        return redirect(url_for('profile_setup'))
    
    return render_template('signup.html', form=form)

@app.route('/profile_setup', methods=['GET', 'POST'])
@login_required
def profile_setup():
    form = ProfileSetupForm(obj=current_user)
    
    if form.validate_on_submit():
        current_user.monthly_salary = form.monthly_salary.data
        current_user.profile_type = ProfileType[form.profile_type.data]
        
        if form.pin_code.data:
            current_user.set_pin(form.pin_code.data)
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('profile_setup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's accounts
    accounts = BankAccount.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Calculate monthly income and expenses
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = Transaction.query.filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.date >= current_month_start
        )
    ).all()
    
    monthly_income = sum(t.amount for t in monthly_transactions if t.transaction_type.value == 'income')
    monthly_expenses = sum(t.amount for t in monthly_transactions if t.transaction_type.value == 'expense')
    
    # Get recent transactions (last 5)
    recent_transactions = Transaction.query.filter_by(user_id=current_user.id)\
        .order_by(Transaction.date.desc()).limit(5).all()
    
    # Get budgets
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    
    # Generate notifications
    notifications = []
    
    # Check for large expenses
    for transaction in recent_transactions:
        if transaction.transaction_type.value == 'expense' and transaction.amount > 5000:
            notifications.append(f"Large expense detected: ₹{transaction.amount:.2f} on {transaction.description or transaction.category}")
    
    # Check budget limits
    for budget in budgets:
        if budget.monthly_spent > budget.monthly_limit:
            notifications.append(f"Budget exceeded for {budget.category}: ₹{budget.monthly_spent:.2f} / ₹{budget.monthly_limit:.2f}")
    
    return render_template('enhanced_dashboard.html', 
                         accounts=accounts,
                         monthly_income=monthly_income,
                         monthly_expenses=monthly_expenses,
                         recent_transactions=recent_transactions,
                         budgets=budgets,
                         notifications=notifications)

@app.route('/add_account', methods=['GET', 'POST'])
@login_required
def add_account():
    form = BankAccountForm()
    
    if form.validate_on_submit():
        account = BankAccount(
            user_id=current_user.id,
            account_name=form.account_name.data,
            account_type=AccountType[form.account_type.data],
            bank_name=form.bank_name.data,
            account_number=form.account_number.data,
            balance=form.balance.data
        )
        db.session.add(account)
        db.session.commit()
        flash('Account added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_account.html', form=form)

@app.route('/add_transaction', methods=['GET', 'POST'])
@login_required
def add_transaction():
    form = TransactionForm()
    accounts = BankAccount.query.filter_by(user_id=current_user.id, is_active=True).all()
    
    # Set account choices
    if len(accounts) == 0:
        flash('Please add a bank account first!', 'error')
        return redirect(url_for('add_account'))
    elif len(accounts) == 1:
        # Auto-select the only account
        form.account_id.choices = [(accounts[0].id, f"{accounts[0].account_name} - {accounts[0].bank_name}")]
        form.account_id.data = accounts[0].id
    else:
        # Multiple accounts - let user choose
        form.account_id.choices = [(a.id, f"{a.account_name} - {a.bank_name}") for a in accounts]
    
    if form.validate_on_submit():
        # Use selected account or default account
        account_id = form.account_id.data or (accounts[0].id if accounts else None)
        
        transaction = Transaction(
            user_id=current_user.id,
            account_id=account_id,
            amount=form.amount.data,
            transaction_type=TransactionType[form.transaction_type.data],
            category=form.category.data,
            description=form.description.data,
            payment_mode=PaymentMode[form.payment_mode.data],
            date=datetime.combine(form.date.data, datetime.min.time())
        )
        
        # Update account balance
        account = BankAccount.query.get(account_id)
        if form.transaction_type.data == 'income':
            account.balance += form.amount.data
        else:
            account.balance -= form.amount.data
        
        # Update budget
        budget = Budget.query.filter_by(user_id=current_user.id, category=form.category.data).first()
        if budget and form.transaction_type.data == 'expense':
            budget.monthly_spent += form.amount.data
            budget.daily_spent += form.amount.data
        
        db.session.add(transaction)
        db.session.commit()
        flash('Transaction added successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('add_transaction.html', form=form)

@app.route('/transactions')
@login_required
def transactions():
    page = request.args.get('page', 1, type=int)
    filter_form = TransactionFilterForm()
    filter_form.account_id.choices = [(0, 'All Accounts')] + [(a.id, f"{a.account_name} - {a.bank_name}") for a in BankAccount.query.filter_by(user_id=current_user.id, is_active=True).all()]
    
    query = Transaction.query.filter_by(user_id=current_user.id)
    
    # Apply filters
    if request.args.get('start_date'):
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        query = query.filter(Transaction.date >= start_date)
    
    if request.args.get('end_date'):
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        query = query.filter(Transaction.date <= end_date)
    
    if request.args.get('category'):
        query = query.filter(Transaction.category == request.args.get('category'))
    
    if request.args.get('min_amount'):
        query = query.filter(Transaction.amount >= float(request.args.get('min_amount')))
    
    if request.args.get('max_amount'):
        query = query.filter(Transaction.amount <= float(request.args.get('max_amount')))
    
    if request.args.get('account_id') and request.args.get('account_id') != '0':
        query = query.filter(Transaction.account_id == int(request.args.get('account_id')))
    
    if request.args.get('transaction_type'):
        query = query.filter(Transaction.transaction_type == request.args.get('transaction_type'))
    
    transactions = query.order_by(Transaction.date.desc()).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('transactions.html', transactions=transactions, filter_form=filter_form)

@app.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    form = BudgetForm()
    
    if form.validate_on_submit():
        budget = Budget.query.filter_by(user_id=current_user.id, category=form.category.data).first()
        
        if budget:
            budget.daily_limit = form.daily_limit.data
            budget.monthly_limit = form.monthly_limit.data
        else:
            budget = Budget(
                user_id=current_user.id,
                category=form.category.data,
                daily_limit=form.daily_limit.data,
                monthly_limit=form.monthly_limit.data
            )
            db.session.add(budget)
        
        db.session.commit()
        flash('Budget set successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('set_budget.html', form=form)

@app.route('/analytics')
@login_required
def analytics():
    # Get spending by category
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    category_spending = db.session.query(
        Transaction.category,
        func.sum(Transaction.amount).label('total')
    ).filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == 'expense',
            Transaction.date >= current_month_start
        )
    ).group_by(Transaction.category).all()
    
    # Get income growth (last 6 months)
    income_growth = []
    for i in range(6):
        month_start = (datetime.utcnow().replace(day=1) - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        monthly_income = db.session.query(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == current_user.id,
                Transaction.transaction_type == 'income',
                Transaction.date >= month_start,
                Transaction.date <= month_end
            )
        ).scalar() or 0
        
        income_growth.append({
            'month': month_start.strftime('%Y-%m'),
            'income': monthly_income
        })
    
    # Get biggest expense
    biggest_expense = Transaction.query.filter(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == 'expense'
        )
    ).order_by(Transaction.amount.desc()).first()
    
    return render_template('analytics.html', 
                         category_spending=category_spending,
                         income_growth=income_growth,
                         biggest_expense=biggest_expense)

# Calculator endpoints (keeping existing functionality)
@app.route('/calculate_emi', methods=['POST'])
@login_required
def calculate_emi():
    data = request.get_json()
    principal = float(data['principal'])
    annual_rate = float(data['rate'])
    tenure_months = int(data['tenure'])
    
    emi = EMICalculator.calculate_emi(principal, annual_rate, tenure_months)
    total_interest = EMICalculator.calculate_total_interest(principal, annual_rate, tenure_months)
    schedule = EMICalculator.get_amortization_schedule(principal, annual_rate, tenure_months)
    
    result = {
        'emi': emi,
        'total_interest': total_interest,
        'total_amount': principal + total_interest,
        'schedule': schedule[:12]
    }
    
    calculation = Calculation(
        user_id=current_user.id,
        calculator_type='emi',
        input_data=json.dumps(data),
        result_data=json.dumps(result)
    )
    db.session.add(calculation)
    db.session.commit()
    
    return jsonify(result)

@app.route('/calculate_sip', methods=['POST'])
@login_required
def calculate_sip():
    data = request.get_json()
    monthly_investment = float(data['monthly'])
    annual_return = float(data['return'])
    years = int(data['years'])
    
    result = SIPCalculator.calculate_sip_value(monthly_investment, annual_return, years)
    
    calculation = Calculation(
        user_id=current_user.id,
        calculator_type='sip',
        input_data=json.dumps(data),
        result_data=json.dumps(result)
    )
    db.session.add(calculation)
    db.session.commit()
    
    return jsonify(result)

@app.route('/calculate_interest', methods=['POST'])
@login_required
def calculate_interest():
    data = request.get_json()
    principal = float(data['principal'])
    rate = float(data['rate'])
    years = int(data['years'])
    compounds_per_year = int(data.get('compounds', 12))
    
    result = InterestCalculator.compound_interest(principal, rate, years, compounds_per_year)
    
    calculation = Calculation(
        user_id=current_user.id,
        calculator_type='interest',
        input_data=json.dumps(data),
        result_data=json.dumps(result)
    )
    db.session.add(calculation)
    db.session.commit()
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
