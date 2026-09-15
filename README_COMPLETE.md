# 💰 Finance Tracker - Complete Documentation

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Database Schema](#database-schema)
4. [Installation & Setup](#installation--setup)
5. [Configuration](#configuration)
6. [Running the Application](#running-the-application)
7. [API Endpoints](#api-endpoints)
8. [User Workflows](#user-workflows)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**Finance Tracker** is a comprehensive financial management application built with Flask, SQLAlchemy, and MySQL. It provides multi-account support, transaction tracking, budget management, loan calculations, investment tracking, and advanced analytics.

**Technology Stack:**
- Backend: Flask 2.3.3
- Database: MySQL with PyMySQL
- Frontend: Jinja2 Templates + Tailwind CSS
- ORM: SQLAlchemy 3.0.5
- Authentication: Flask-Login + Google OAuth 2.0
- Security: bcrypt password hashing + OTP verification

---

## ✨ Features

### ✅ **Implemented & Active Features**

#### **1. User Management**
- ✅ User Registration (Signup) with validation
- ✅ Secure Login with password hashing
- ✅ Google OAuth 2.0 authentication
- ✅ Email & Phone OTP verification
- ✅ User profile management
- ✅ Secure logout functionality
- ✅ Session management with Flask-Login

#### **2. Multi-Account Management**
- ✅ Create multiple bank/financial accounts
- ✅ Account types: Savings, Current, Credit Card, Investment
- ✅ Real-time balance tracking
- ✅ Account visibility on Dashboard & Profile
- ✅ Account-wise transaction history
- ✅ Quick account switching

#### **3. Transaction Management**
- ✅ Record income & expenses
- ✅ Transaction categories (with custom categories support)
- ✅ Multiple payment modes: Cash, Debit Card, Credit Card, UPI, Net Banking, Cheque
- ✅ Transaction descriptions and dates
- ✅ Transfer between accounts
- ✅ Recent transaction view (last 5)
- ✅ Transaction filtering by account/category/date

#### **4. Budget Management**
- ✅ Set monthly spending limits
- ✅ Category-wise budgets
- ✅ Real-time spending tracking
- ✅ Budget vs actual spending visualization
- ✅ Budget alerts when near limit
- ✅ Daily & monthly budget limits

#### **5. Financial Goals**
- ✅ Create savings goals with target amounts
- ✅ Track goal progress
- ✅ Goal categories (emergency fund, vacation, education, etc.)
- ✅ Target dates and milestones

#### **6. Subscriptions & Recurring Payments**
- ✅ Track monthly/yearly subscriptions
- ✅ Payment due date reminders
- ✅ Subscription categories (Netflix, Gym, Insurance, etc.)
- ✅ Active/inactive subscription status

#### **7. Loan Management**
- ✅ Record loans with details
- ✅ EMI (Equated Monthly Installment) calculation
- ✅ Interest calculation
- ✅ Loan amortization schedule
- ✅ Next payment tracking

#### **8. Investment Tracking**
- ✅ Track stock investments
- ✅ Mutual fund tracking
- ✅ Cryptocurrency holdings
- ✅ Fixed deposits
- ✅ Purchase date & current value
- ✅ Return on Investment (ROI) calculation

#### **9. Financial Health Dashboard**
- ✅ Net worth calculation
- ✅ Total assets vs liabilities
- ✅ Savings rate percentage
- ✅ Expense ratio analysis
- ✅ Financial health score

#### **10. Alerts & Notifications**
- ✅ Budget exceeded alerts
- ✅ Subscription payment due alerts
- ✅ Loan payment reminders
- ✅ Large transaction alerts
- ✅ Alert severity levels (info, warning, danger)
- ✅ Mark alerts as read

#### **11. Audit Logging**
- ✅ Track all user actions
- ✅ Login/logout logging
- ✅ Transaction change history
- ✅ Before/after values for updates
- ✅ IP address & user agent logging
- ✅ Compliance & security audit trail

#### **12. Categories Management**
- ✅ Pre-defined expense categories
- ✅ Income categories
- ✅ Custom category creation
- ✅ Category icons and colors
- ✅ Category-wise analytics

#### **13. Dashboard & Analytics**
- ✅ Overview of all accounts
- ✅ Monthly income & expenses
- ✅ Lifetime statistics
- ✅ Recent transactions list
- ✅ Budget status visualization
- ✅ Notifications panel

#### **14. Financial Calculators**
- ✅ EMI Calculator (Loan calculations)
- ✅ SIP Calculator (Investment planning)
- ✅ Net Worth Calculator
- ✅ Interest Calculator
- ✅ Debt Payoff Planner

#### **15. Security Features**
- ✅ Password hashing with bcrypt
- ✅ Email OTP verification
- ✅ Phone OTP verification
- ✅ PIN lock option
- ✅ Session security
- ✅ HTTPS support ready
- ✅ Audit logs for compliance

---

## 📊 Database Schema

### **Core Tables (12 Total)**

```
college (Database)
├── users
├── bank_accounts
├── transactions
├── budgets
├── loans
├── investments
├── subscriptions
├── budget_goals (Financial Goals)
├── categories
├── financial_health
├── alerts
├── audit_logs
├── verifications
└── calculations
```

### **Table Descriptions**

#### **1. users**
Stores user authentication & profile data
```sql
- id (PK)
- username (unique)
- email (unique)
- phone
- password_hash (bcrypt encrypted)
- google_id (for OAuth)
- profile_type (PERSONAL, BUSINESS, FAMILY)
- monthly_salary
- pin_code (hashed)
- email_verified (boolean)
- phone_verified (boolean)
- created_at
```

#### **2. bank_accounts**
User's financial accounts
```sql
- id (PK)
- user_id (FK)
- account_name
- account_type (SAVINGS, CURRENT, CREDIT_CARD, INVESTMENT)
- bank_name
- account_number
- balance
- is_active
- created_at
```

#### **3. transactions**
Income/expense records
```sql
- id (PK)
- user_id (FK)
- account_id (FK)
- amount
- transaction_type (INCOME, EXPENSE, TRANSFER)
- category
- description
- payment_mode (CASH, DEBIT_CARD, UPI, etc.)
- date
- to_account_id (for transfers)
```

#### **4. budgets**
Spending limits per category
```sql
- id (PK)
- user_id (FK)
- category
- monthly_limit
- daily_limit
- monthly_spent
- daily_spent
- last_monthly_reset
- last_daily_reset
- created_at
```

#### **5. loans**
Loan records with EMI details
```sql
- id (PK)
- user_id (FK)
- loan_name
- principal_amount
- interest_rate
- tenure_months
- remaining_balance
- emi_amount
- next_payment_date
- created_at
```

#### **6. investments**
Investment portfolio tracking
```sql
- id (PK)
- user_id (FK)
- investment_name
- investment_type (STOCKS, MUTUAL_FUNDS, CRYPTO, FIXED_DEPOSIT)
- invested_amount
- current_value
- quantity
- purchase_date
- last_updated
```

#### **7. subscriptions**
Recurring payments
```sql
- id (PK)
- user_id (FK)
- subscription_name
- category (Netflix, Gym, etc.)
- amount
- billing_cycle (monthly, yearly)
- next_payment_date
- is_active
- created_at
```

#### **8. budget_goals** (Financial Goals)
Savings goals
```sql
- id (PK)
- user_id (FK)
- goal_name
- target_amount
- current_amount
- target_date
- category
- created_at
```

#### **9. categories**
Transaction categories
```sql
- id (PK)
- user_id (FK)
- name
- category_type (income, expense)
- icon
- color
- is_custom
- created_at
```

#### **10. financial_health**
Overall financial metrics
```sql
- id (PK)
- user_id (FK, unique)
- total_assets
- total_liabilities
- net_worth
- credit_score
- savings_rate (%)
- expense_ratio (%)
- last_updated
- created_at
```

#### **11. alerts**
Notifications & alerts
```sql
- id (PK)
- user_id (FK)
- alert_type (budget_exceeded, payment_due, etc.)
- title
- message
- severity (info, warning, danger)
- is_read
- related_id & related_type (for linking)
- created_at
- expires_at
```

#### **12. audit_logs**
Action tracking for compliance
```sql
- id (PK)
- user_id (FK)
- action (login, logout, add_transaction, etc.)
- action_type (CREATE, READ, UPDATE, DELETE)
- table_name
- record_id
- old_values (JSON)
- new_values (JSON)
- ip_address
- user_agent
- created_at
```

#### **13. verifications**
OTP & verification tracking
```sql
- id (PK)
- user_id (FK)
- verification_type (email, phone)
- contact_value
- otp_code
- is_verified
- attempts & max_attempts
- otp_sent_at
- verified_at
- expires_at
- created_at
```

---

## 🚀 Installation & Setup

### **Prerequisites**
- Python 3.8+
- MySQL Server 5.7+
- pip (Python package manager)
- Virtual Environment (recommended)

### **Step 1: Clone the Repository**
```bash
cd c:\Users\asus\OneDrive\Desktop\coding\python\projects123\finance
```

### **Step 2: Create Virtual Environment**
```bash
python -m venv .venv-1

# On Windows
.venv-1\Scripts\activate

# On Mac/Linux
source .venv-1/bin/activate
```

### **Step 3: Install Dependencies**
```bash
pip install -r requirements.txt
```

### **Step 4: Configure Environment**
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```
MYSQL_USER=root
MYSQL_PASS=your_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DB=college

FLASK_ENV=development
SECRET_KEY=your-super-secret-key

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-secret

TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=+1234567890
```

### **Step 5: Create MySQL Database**
```bash
mysql -u root -p
CREATE DATABASE college;
USE college;
```

### **Step 6: Initialize Database**
```bash
python
>>> from enhanced_app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

---

## ⚙️ Configuration

### **MySQL Configuration**
Edit `config.py`:
```python
# Option 1: Environment variables (recommended)
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:password@localhost:3306/college'

# Option 2: Direct configuration
MYSQL_USER = 'root'
MYSQL_PASS = 'your_password'
MYSQL_HOST = 'localhost'
MYSQL_PORT = '3306'
MYSQL_DB = 'college'
```

### **Google OAuth Setup**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create OAuth 2.0 credentials (Web application)
3. Add authorized redirect URIs:
   - `http://localhost:5000/callback`
   - `http://your-domain.com/callback`
4. Copy Client ID & Secret to `.env`

### **Twilio Setup (for SMS OTP)**
1. Sign up at [Twilio.com](https://www.twilio.com/)
2. Get Account SID, Auth Token, and Phone Number
3. Add to `.env`:
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

## ▶️ Running the Application

### **Development Server**
```bash
# Make sure virtual environment is activated
python enhanced_app.py
```

Server runs on: `http://127.0.0.1:5000`

### **Production with Gunicorn**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 enhanced_app:app
```

### **Using Flask Development Server**
```bash
flask run
```

---

## 🔗 API Endpoints

### **Authentication**
- `POST /signup` - User registration
- `POST /login` - User login  
- `POST /logout` - User logout
- `POST /verify-otp` - Verify OTP
- `GET /auth/google` - Google OAuth login

### **User Profile**
- `GET /profile` - View user profile
- `POST /profile_setup` - Complete profile setup
- `PUT /api/users/profile` - Update profile
- `GET /api/users/profile` - Get profile data

### **Accounts**
- `GET /api/users/accounts` - List user accounts
- `POST /api/users/accounts` - Create account
- `DELETE /api/users/accounts/<id>` - Delete account

### **Transactions**
- `GET /transactions` - View transactions
- `POST /add_transaction` - Add transaction
- `GET /api/transactions` - Get transactions (API)
- `PUT /api/transactions/<id>` - Update transaction

### **Budgets**
- `POST /set_budget` - Create budget
- `GET /budgets` - View budgets
- `PUT /api/budgets/<id>` - Update budget

### **Goals**
- `POST /add_goal` - Create financial goal
- `GET /goals` - View goals
- `PUT /api/goals/<id>` - Update goal progress

### **Subscriptions**
- `POST /add_subscription` - Add subscription
- `GET /subscriptions` - View subscriptions
- `DELETE /api/subscriptions/<id>` - Cancel subscription

### **Loans**
- `POST /add_loan` - Add loan
- `GET /loans` - View loans
- `GET /api/loans/<id>` - Get loan details with EMI

### **Dashboard**
- `GET /dashboard` - Main dashboard
- `GET /analytics` - Analytics page

---

## 👤 User Workflows

### **Workflow 1: New User Signup**
```
1. User clicks "Sign Up"
2. Enters: username, email, password, profile type
3. System validates & creates user in 'users' table
4. Sends OTP to email for verification
5. User enters OTP to confirm email
6. Sends OTP to phone (optional)
7. User enters phone OTP
8. Redirects to profile setup page
9. User enters monthly salary, PIN
10. System creates financial_health record
11. User completes dashboard access
```

### **Workflow 2: Google OAuth Login**
```
1. User clicks "Login with Google"
2. Redirected to Google consent screen
3. User authorizes app
4. Google returns user info
5. System checks if email exists
6. If new: creates user with google_id
7. If existing: logs in
8. Checks if email verified (yes, from Google)
9. Redirects to dashboard
```

### **Workflow 3: Add Account & Transaction**
```
1. User on Dashboard clicks "+ Add Account"
2. Enters account name, type, bank name, account number
3. Sets initial balance
4. Account created in bank_accounts table
5. User sees account card with balance
6. Clicks "📝 Add Transaction"
7. Enters amount, category, description, payment mode
8. Transaction saved to transactions table
9. Account balance updates automatically
10. Transaction appears in recent list
```

### **Workflow 4: Set Budget & Track**
```
1. User clicks "📊 Set Budget"
2. Enters category, monthly limit
3. Budget created in budgets table
4. User adds transactions in this category
5. Budget spending tracked in real-time
6. When 80% spent: yellow alert
7. When limit exceeded: red alert created
8. Alert appears on dashboard
9. User can view budget progress on dashboard
```

### **Workflow 5: Logout**
```
1. User clicks "🚪 Logout" button (visible in navbar & profile)
2. Action logged to audit_logs table
3. Session cleared
4. User redirected to login page
5. Previous data not accessible
```

---

## 📦 Deployment

### **With Gunicorn + Supervisor (Linux/VPS)**
See `DEPLOYMENT_GUIDE.md` for complete setup

### **With Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "enhanced_app:app"]
```

### **With Heroku**
```bash
heroku create your-app-name
heroku addons:create cleardb:ignite
git push heroku main
```

### **With Railway/Render**
- Connect GitHub repository
- Set environment variables
- Deploy automatically

---

## 🐛 Troubleshooting

### **Issue: Database Connection Failed**
```
Error: Can't connect to MySQL server
```

**Solution:**
1. Check MySQL server is running: `mysqld --version`
2. Verify credentials in `.env`
3. Test connection: `mysql -u root -p -h localhost`
4. Ensure database exists: `CREATE DATABASE college;`

### **Issue: Data Not Saving to Database**
```
Error: User created but not in database
```

**Solution:**
1. Check config.py is using MySQL (not SQLite)
2. Ensure `db.session.commit()` is called
3. Check MySQL connection string in `.env`
4. Run `db.create_all()` to initialize tables

### **Issue: Logout Not Visible**
```
Solution: Logout button appears in TWO places:
1. Top navigation bar (🚪 Logout button)
2. Left sidebar on profile page (full-width red button)
Both are visible and functional.
```

### **Issue: Multi-Account Not Showing**
```
Solution: Multi-accounts visible in THREE places:
1. Dashboard: "💳 Your Accounts" grid section
2. Profile page: "Your Accounts Overview" at top
3. Profile page: "💼 Account Management" section below
All accounts shown as cards with balances.
```

### **Issue: OTP Not Received**
```
Solution:
1. Check phone number format: +91XXXXX or +1XXXXX
2. Verify Twilio credentials in .env
3. Check SMS doesn't go to spam
4. Verify email delivery in spam folder
5. Check OTP expiry (5 minutes default)
```

### **Issue: Google OAuth Not Working**
```
Solution:
1. Verify Google Client ID in .env
2. Check redirect URI matches in Google Console
3. Ensure redirect URI is registered
4. Clear browser cache and cookies
5. Test on localhost:5000 (not 127.0.0.1)
```

### **Port 5000 Already in Use**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID <PID> /F

# Or use different port
python -c "from enhanced_app import app; app.run(port=5001)"
```

---

## 📝 Features Summary

| Feature | Status | Tables Used | Active |
|---------|--------|------------|--------|
| User Registration | ✅ | users, verifications | Yes |
| Google OAuth | ✅ | users | Yes |
| Email/Phone OTP | ✅ | verifications | Yes |
| Multi-Account | ✅ | bank_accounts | Yes |
| Transactions | ✅ | transactions, categories | Yes |
| Budgets | ✅ | budgets, alerts | Yes |
| Financial Goals | ✅ | budget_goals | Yes |
| Subscriptions | ✅ | subscriptions, alerts | Yes |
| Loans | ✅ | loans | Yes |
| Investments | ✅ | investments | Yes |
| Categories | ✅ | categories | Yes |
| Financial Health | ✅ | financial_health | Yes |
| Alerts | ✅ | alerts | Yes |
| Audit Logs | ✅ | audit_logs | Yes |
| Dashboard | ✅ | All | Yes |
| Analytics | ✅ | transactions, budgets | Yes |
| Logout | ✅ | audit_logs | Yes |

---

## 📚 Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://www.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)
- [Google OAuth Documentation](https://developers.google.com/identity)
- [Twilio Documentation](https://www.twilio.com/docs/)

---

## 📞 Support

For issues or feature requests:
1. Check troubleshooting section
2. Review logs in `audit_logs` table
3. Check browser console for errors
4. Enable debug mode: `FLASK_ENV=development`

---

**Version:** 1.0.0  
**Last Updated:** 2026-07-21  
**Maintainer:** Your Finance Tracker Team
 wq   +
 