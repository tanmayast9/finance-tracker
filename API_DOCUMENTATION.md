"""
Comprehensive API Documentation
"""

API_DOCUMENTATION = """
# Finance Application API Documentation

## Base URL
http://localhost:5000/api

## Authentication
All endpoints require JWT token in Authorization header:
```
Authorization: Bearer {token}
```

## Health Check
GET /health
- Returns: {"status": "healthy", "message": "Finance API is running"}

---

## 1. AUTHENTICATION ENDPOINTS

### Sign Up
POST /auth/signup
Body: {
    "username": "string",
    "email": "string",
    "password": "string",
    "full_name": "string",
    "currency": "USD"
}
Returns: {user_data, token}

### Login
POST /auth/login
Body: {"email": "string", "password": "string"}
Returns: {user_data, token}

### Change Password
POST /auth/change-password
Body: {"old_password": "string", "new_password": "string"}
Requires: Auth token

### Refresh Token
POST /auth/refresh
Returns: {token}
Requires: Auth token

---

## 2. USER ENDPOINTS

### Get Profile
GET /users/profile
Returns: User profile data
Requires: Auth token

### Update Profile
PUT /users/profile
Body: {"full_name": "string", "phone": "string", "currency": "string", "bio": "string"}
Requires: Auth token

### Get Accounts
GET /users/accounts
Returns: List of user accounts
Requires: Auth token

### Create Account
POST /users/accounts
Body: {"account_name": "string", "account_type": "string", "balance": float}
Requires: Auth token

### Delete Account
DELETE /users/accounts/{account_id}
Requires: Auth token

### Get Preferences
GET /users/preferences
Returns: User preferences (theme, currency, 2FA)
Requires: Auth token

### Update Preferences
PUT /users/preferences
Body: {"theme_preference": "light|dark", "currency": "string", "two_factor_enabled": boolean}
Requires: Auth token

### Activity Log
GET /users/activity-log?page=1&per_page=20
Returns: User activity history
Requires: Auth token

---

## 3. EXPENSE ENDPOINTS

### Get Expenses
GET /expenses/?page=1&per_page=20&category_id=X&account_id=Y&start_date=ISO&end_date=ISO
Returns: Paginated list of expenses
Requires: Auth token

### Create Expense
POST /expenses/
Body: {
    "amount": float,
    "category_id": int,
    "account_id": int,
    "description": "string",
    "notes": "string",
    "transaction_date": "ISO datetime"
}
Requires: Auth token

### Update Expense
PUT /expenses/{expense_id}
Body: {amount, description, notes, category_id}
Requires: Auth token

### Delete Expense
DELETE /expenses/{expense_id}
Requires: Auth token

### Daily Expense Log
GET /expenses/daily-log?date=YYYY-MM-DD
Returns: Expenses for specific day
Requires: Auth token

---

## 4. INCOME ENDPOINTS

### Get Income
GET /income/?page=1&per_page=20&category_id=X&start_date=ISO&end_date=ISO
Returns: Paginated income list
Requires: Auth token

### Add Income
POST /income/
Body: {
    "amount": float,
    "category_id": int,
    "account_id": int,
    "description": "string",
    "notes": "string"
}
Requires: Auth token

### Update Income
PUT /income/{income_id}
Body: {amount, description, notes, category_id}
Requires: Auth token

### Delete Income
DELETE /income/{income_id}
Requires: Auth token

### Income Summary
GET /income/summary?period=monthly|yearly&year=YYYY&month=MM
Returns: Income breakdown by category
Requires: Auth token

---

## 5. BUDGET ENDPOINTS

### Get Budgets
GET /budgets/?period=monthly&year=YYYY&month=MM
Returns: Budgets with spending status
Requires: Auth token

### Create Budget
POST /budgets/
Body: {
    "category_id": int,
    "amount_limit": float,
    "alert_threshold": 80,
    "period": "monthly"
}
Requires: Auth token

### Update Budget
PUT /budgets/{budget_id}
Body: {amount_limit, alert_threshold}
Requires: Auth token

### Delete Budget
DELETE /budgets/{budget_id}
Requires: Auth token

---

## 6. CATEGORY ENDPOINTS

### Get Expense Categories
GET /categories/expense
Returns: All expense categories
Requires: Auth token

### Get Income Categories
GET /categories/income
Returns: All income categories
Requires: Auth token

### Create Custom Category
POST /categories/
Body: {
    "name": "string",
    "category_type": "expense|income",
    "description": "string",
    "icon": "emoji",
    "color": "#RRGGBB"
}
Requires: Auth token

### Update Category
PUT /categories/{category_id}
Body: {name, description, icon, color}
Requires: Auth token

### Delete Category
DELETE /categories/{category_id}
Requires: Auth token (only custom categories)

### Initialize Default Categories
POST /categories/init-defaults
Requires: Auth token

---

## 7. TRANSACTION ENDPOINTS

### Get Transactions
GET /transactions/?page=1&per_page=20&type=expense|income|all&search=TEXT&start_date=ISO&end_date=ISO
Returns: Paginated transactions
Requires: Auth token

### Get Transaction Details
GET /transactions/{transaction_id}
Returns: Single transaction with all details
Requires: Auth token

### Export Transactions as CSV
GET /transactions/export?start_date=ISO&end_date=ISO
Returns: CSV file
Requires: Auth token

### Get Recurring Transactions
GET /transactions/recurring
Returns: All recurring transactions
Requires: Auth token

---

## 8. ANALYTICS ENDPOINTS

### Dashboard Summary
GET /analytics/dashboard
Returns: {income, expenses, savings, savings_rate, account_balance, net_worth, latest_transactions}
Requires: Auth token

### Monthly Summary
GET /analytics/monthly-summary?year=YYYY&month=MM
Returns: Income and expense breakdown by category
Requires: Auth token

### Category Analysis
GET /analytics/category-analysis?month=MM&year=YYYY
Returns: Detailed category-wise spending with percentages
Requires: Auth token

### Spending Trends
GET /analytics/trends?months=12
Returns: Last N months income, expense, and savings
Requires: Auth token

### Financial Health Score
GET /analytics/health-score
Returns: {health_score (0-100), savings_rate, expense_ratio, insights}
Requires: Auth token

---

## 9. ADVANCED FINANCE ENDPOINTS

### Get Loans
GET /advanced/loans
Returns: List of all loans
Requires: Auth token

### Create Loan
POST /advanced/loans
Body: {
    "loan_name": "string",
    "loan_type": "personal|home|auto|education",
    "principal_amount": float,
    "interest_rate": float,
    "tenure_months": int,
    "start_date": "ISO"
}
Returns: {loan_id, emi}
Requires: Auth token

### Get EMI Schedule
GET /advanced/loans/{loan_id}/emi-schedule
Returns: Month-by-month amortization schedule
Requires: Auth token

### Get Debt Payoff Plan
GET /advanced/loans/{loan_id}/payoff-plan
Returns: Optimal payoff strategy for all debts
Requires: Auth token

### Get Investments
GET /advanced/investments
Returns: All investments with total returns
Requires: Auth token

### Create Investment
POST /advanced/investments
Body: {
    "investment_name": "string",
    "investment_type": "stocks|mutual_funds|sip|crypto|bonds",
    "initial_amount": float,
    "quantity": float,
    "price_per_unit": float,
    "investment_date": "ISO"
}
Requires: Auth token

### Calculate SIP Returns
POST /advanced/sip/calculate
Body: {
    "monthly_investment": float,
    "annual_return": float,
    "years": int
}
Returns: {total_invested, returns, future_value}
Requires: Auth token

### Get Subscriptions
GET /advanced/subscriptions
Returns: All subscriptions with monthly cost
Requires: Auth token

### Create Subscription
POST /advanced/subscriptions
Body: {
    "service_name": "string",
    "amount": float,
    "billing_cycle": "weekly|monthly|yearly",
    "category": "string"
}
Requires: Auth token

### Get Goals
GET /advanced/goals
Returns: All savings goals with progress
Requires: Auth token

### Create Goal
POST /advanced/goals
Body: {
    "goal_name": "string",
    "goal_type": "savings|emergency_fund|investment",
    "target_amount": float,
    "target_date": "ISO"
}
Requires: Auth token

### Get Net Worth
GET /advanced/net-worth
Returns: {total_assets, total_liabilities, net_worth, breakdown}
Requires: Auth token

---

## ERROR RESPONSES

### 400 Bad Request
```json
{"error": "Missing required fields"}
```

### 401 Unauthorized
```json
{"error": "Invalid or expired token"}
```

### 403 Forbidden
```json
{"error": "Access denied"}
```

### 404 Not Found
```json
{"error": "Resource not found"}
```

### 409 Conflict
```json
{"error": "Resource already exists"}
```

### 500 Internal Server Error
```json
{"error": "Internal server error"}
```

---

## EXAMPLE REQUESTS

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Add Expense
```bash
curl -X POST http://localhost:5000/api/expenses/ \\
  -H "Authorization: Bearer TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "amount": 50,
    "category_id": 1,
    "account_id": 1,
    "description": "Lunch"
  }'
```

### Get Dashboard
```bash
curl -X GET http://localhost:5000/api/analytics/dashboard \\
  -H "Authorization: Bearer TOKEN"
```

### Calculate Net Worth
```bash
curl -X GET http://localhost:5000/api/advanced/net-worth \\
  -H "Authorization: Bearer TOKEN"
```

---

## RATE LIMITING
Recommended for production: 100 requests per minute per user

## VERSIONING
Current version: v1
Future: /api/v2/

## PAGINATION
Default page size: 20 items
Max page size: 100 items
"""

print(API_DOCUMENTATION)
