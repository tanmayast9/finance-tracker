# Database Tables Analysis & Usage Report

## Database Overview
**Database Name:** college.finance (MySQL)
**Total Tables:** 12
**Tables Status:** ✅ All tables defined, but NOT all actively used yet

---

## 📊 Table Usage Status

### ✅ ACTIVELY USED TABLES (5)

| Table | Status | Used In | Purpose |
|-------|--------|---------|---------|
| **users** | ✅ ACTIVE | Login, Signup, Profile | Stores user credentials and profile |
| **bank_accounts** | ✅ ACTIVE | Dashboard, Transactions | Stores user's bank/financial accounts |
| **transactions** | ✅ ACTIVE | Dashboard, Analytics | Income & expense records |
| **budgets** | ✅ ACTIVE | Dashboard | Monthly spending limits |
| **subscriptions** | ✅ ACTIVE | Dashboard | Recurring payments tracking |

### ⚠️ PARTIALLY USED TABLES (2)

| Table | Status | Used In | Purpose | Issue |
|-------|--------|---------|---------|-------|
| **loans** | ⚠️ PARTIAL | ML Models | Loan calculations | Data not shown in UI |
| **investments** | ⚠️ PARTIAL | ML Models | Investment tracking | No UI to add/view investments |

### ❌ NOT USED YET TABLES (5)

| Table | Status | Defined | Used | Next Steps |
|-------|--------|---------|------|------------|
| **goals** (budget_goals) | ❌ UNUSED | ✅ Yes | ❌ No | Need UI to create/view goals |
| **financial_health** | ❌ UNUSED | ✗ No | ❌ No | Need to define this table |
| **alerts** | ❌ UNUSED | ✗ No | ❌ No | Need to define alerts table |
| **audit_logs** | ❌ UNUSED | ✗ No | ❌ No | Need audit logging feature |
| **categories** | ❌ UNUSED | ✗ No | ❌ No | Partial - need to define & use |

---

## 🔐 LOGIN & SIGNUP - Where Details Are Stored

### Login Process Flow
```
User enters: username + password
              ↓
       Fetch from `users` table
              ↓
       Check password hash
              ↓
   Store session (Flask-Login)
              ↓
   Redirect to dashboard/profile setup
```

### Signup Process Flow
```
User enters: username, email, password, profile_type
              ↓
    Create new User record in `users` table
              ↓
    Hash password & store in password_hash
              ↓
    Store session & log user in
              ↓
    Redirect to profile_setup page
```

### User Data Storage in `users` Table

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    
    -- Login Credentials (filled at signup)
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile Data (filled at profile_setup)
    profile_type ENUM('PERSONAL', 'BUSINESS', 'FAMILY'),
    monthly_salary FLOAT DEFAULT 0.0,
    pin_code VARCHAR(255),  -- Optional: for extra security
    
    -- Timestamps
    created_at DATETIME DEFAULT NOW()
);
```

### Current Login/Signup Fields

**At Signup:**
- ✅ Username
- ✅ Email
- ✅ Password
- ✅ Profile Type (Personal/Business/Family)

**At Profile Setup (After Login):**
- ✅ Monthly Salary
- ✅ PIN Code (optional security feature)

---

## 📈 Active Database Relationships

```
users (1) ──── (∞) bank_accounts
  ↓
  ├── (∞) transactions
  ├── (∞) budgets
  ├── (∞) subscriptions
  ├── (∞) loans
  ├── (∞) investments
  ├── (∞) budget_goals (goals)
  └── (∞) calculations
```

---

## 🔍 Which Tables Are Connected to Login

**Direct Connection:**
- `users` - ✅ **Direct** (login credentials stored here)
- `bank_accounts` - ✅ **Linked via user_id** (accounts belong to user)
- `transactions` - ✅ **Linked via user_id** (transactions belong to user)
- `budgets` - ✅ **Linked via user_id** (budgets belong to user)

**Indirect Connection:**
- `subscriptions` - ✅ Via user_id (user subscriptions)
- `loans` - ✅ Via user_id (user loans)
- `investments` - ✅ Via user_id (user investments)
- `budget_goals` - ✅ Via user_id (user goals)

---

## 📋 Database Query Examples

### Login Query
```python
# enhanced_app.py - Login Route
user = User.query.filter_by(username=form.username.data).first()
if user and user.check_password(form.password.data):
    login_user(user)  # Session created
```

### Signup Query
```python
# enhanced_app.py - Signup Route
user = User(
    username=form.username.data, 
    email=form.email.data,
    profile_type=ProfileType[form.profile_type.data]
)
user.set_password(form.password.data)
db.session.add(user)
db.session.commit()  # User saved to 'users' table
```

### Dashboard Data Query
```python
# After login - all user data is fetched
accounts = BankAccount.query.filter_by(user_id=current_user.id).all()
transactions = Transaction.query.filter_by(user_id=current_user.id).all()
budgets = Budget.query.filter_by(user_id=current_user.id).all()
```

---

## 🎯 Implementation Status

| Feature | Status | Table Used | Visible In |
|---------|--------|------------|-----------|
| **User Registration** | ✅ Complete | `users` | Login/Signup pages |
| **User Login** | ✅ Complete | `users` | Login page |
| **User Profile** | ✅ Complete | `users` | Profile page |
| **Multi-Accounts** | ✅ Complete | `bank_accounts` | Dashboard/Profile |
| **Add Transaction** | ✅ Complete | `transactions` | Dashboard/Add Transaction |
| **Budget Management** | ✅ Complete | `budgets` | Dashboard/Set Budget |
| **Subscriptions** | ✅ Complete | `subscriptions` | Dashboard |
| **Loans** | ⚠️ Partial | `loans` | ML Calculations only |
| **Investments** | ⚠️ Partial | `investments` | ML Calculations only |
| **Financial Goals** | ❌ Not Done | `budget_goals` | Not yet implemented |
| **Alerts** | ❌ Not Done | Not defined | Not yet implemented |
| **Audit Logs** | ❌ Not Done | Not defined | Not yet implemented |

---

## 📍 Files Where Each Table Is Used

### `enhanced_app.py`
- ✅ Users (login, signup, profile)
- ✅ BankAccounts (dashboard, add account)
- ✅ Transactions (add transaction, dashboard)
- ✅ Budgets (set budget, dashboard)
- ✅ Subscriptions (dashboard)

### `enhanced_models.py`
- Defines all 12+ table structures

### `backend/models.py`
- Alternative User model (older version)

### `ml_models/`
- Uses Loans for EMI calculations
- Uses Investments for SIP calculations
- Uses BankAccounts for financial health

### Templates
- `enhanced_dashboard.html` - Displays accounts, transactions, budgets
- `user_profile.html` - Shows user info, accounts
- Login/Signup pages - Create users

---

## 🚀 Next Steps to Use All Tables

### ⚠️ PARTIALLY USED - Need UI
1. **Loans** - Add page to create/view loans with EMI tracking
2. **Investments** - Add page to track portfolio

### ❌ NOT USED - Need Implementation
1. **Financial Goals** (budget_goals)
   - Create page to set savings goals
   - Track progress towards goals
   - Show goal cards on dashboard

2. **Alerts** (needs table definition)
   - Budget exceeded alerts
   - Subscription payment reminders
   - Loan payment due alerts

3. **Audit Logs** (needs table definition)
   - Log all user transactions
   - Track profile changes
   - Security audit trail

4. **Categories**
   - Pre-defined expense categories
   - Link to transactions
   - Custom categories per user

---

## 💡 Summary

**Current State:**
- ✅ 5 out of 12 tables are **actively used** in UI
- ⚠️ 2 tables are **partially used** (backend only)
- ❌ 5 tables are **not yet implemented** in UI

**Login/Signup Details:**
- Stored in → `users` table
- Fields: username, email, password_hash, profile_type, monthly_salary, pin_code
- Additional data linked via user_id to other tables

**Recommendations:**
1. Keep active tables as-is (working well)
2. Add UI for Loans & Investments
3. Implement Financial Goals feature
4. Add alert system
5. Optional: Add audit logging for security
