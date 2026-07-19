from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from ml_models.calculators import EMICalculator, InterestCalculator, SIPCalculator, NetWorthCalculator, DebtPayoffPlanner
from models import db, User, Calculation
from forms import LoginForm, SignupForm
from config import Config
import json

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
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    
    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = SignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

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
        'schedule': schedule[:12]  # First 12 months
    }
    
    # Save calculation to database
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
    
    # Save calculation to database
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
    
    # Save calculation to database
    calculation = Calculation(
        user_id=current_user.id,
        calculator_type='interest',
        input_data=json.dumps(data),
        result_data=json.dumps(result)
    )
    db.session.add(calculation)
    db.session.commit()
    
    return jsonify(result)

@app.route('/dashboard')
@login_required
def dashboard():
    calculations = Calculation.query.filter_by(user_id=current_user.id).order_by(Calculation.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', calculations=calculations)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
