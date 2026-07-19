# Finance Application Documentation

## 🚀 Finance App - Complete Personal Finance Management System

A comprehensive Python-based personal finance application with advanced ML/AI capabilities for smart expense tracking, budgeting, and financial analytics.

## 📋 Features

### Core Features
- **User Authentication**: Secure login/signup with JWT tokens
- **Multi-Account Support**: Track multiple bank/cash accounts
- **Income & Expense Tracking**: Record all financial transactions
- **Category Management**: Customizable expense and income categories
- **Daily Logs**: Track daily spending patterns
- **Transaction History**: Complete transaction records with notes and tags

### 📊 Analytics & Insights
- **Dashboard**: Real-time financial overview
- **Spending Analysis**: Category-wise spending breakdown
- **Monthly Summaries**: Income vs expense reports
- **Trend Analysis**: 12-month spending trends
- **Financial Health Score**: AI-calculated financial wellness metric
- **Pie Charts & Graphs**: Visual spending patterns
- **Budget Adherence**: Track budget vs actual spending

### 🎯 Budgeting
- **Monthly Budgets**: Set spending limits per category
- **Budget Alerts**: Get notified when approaching limits
- **Custom Goals**: Emergency funds, savings targets
- **Budget Tracking**: Monitor budget adherence monthly

### 🏦 Advanced Finance
- **Loan Management**: Track multiple loans with EMI calculations
- **EMI Calculator**: Calculate monthly installments
- **Investment Tracking**: Monitor stocks, mutual funds, SIPs
- **SIP Calculator**: Calculate SIP returns
- **Net Worth Calculator**: Track total financial position
- **Subscription Tracker**: Monitor recurring payments
- **Debt Payoff Planner**: Optimize loan repayment strategy

### 🤖 AI/ML Features
- **Expense Prediction**: ML model predicts transaction categories
- **Smart Categorization**: Automatic category suggestion for new transactions
- **Anomaly Detection**: Detect unusual spending (fraud detection)
- **Savings Recommendations**: AI-powered spending insights
- **Financial Health Score**: Monthly financial wellness assessment
- **Spending Patterns Analysis**: Identify trends and patterns

### 🔐 Security
- **Password Encryption**: Bcrypt hashing
- **JWT Authentication**: Secure token-based auth
- **Data Encryption**: Sensitive data encryption
- **Biometric Lock**: PIN/biometric support (frontend)
- **Two-Factor Authentication**: Additional security layer

### 📱 User Experience
- **Dark/Light Mode**: Theme preferences
- **CSV Export**: Export transaction data
- **Multiple Currencies**: Support for different currencies
- **Cloud Backup**: Data backup functionality
- **Offline Support**: Work offline with sync capability
- **Responsive Design**: Works on all devices

## 🏗️ Project Structure

```
finance/
├── backend/
│   ├── app.py                 # Flask application factory
│   ├── models.py              # Database models
│   ├── config.py              # Configuration settings
│   ├── routes/
│   │   ├── auth_routes.py     # Authentication endpoints
│   │   ├── expense_routes.py  # Expense management
│   │   ├── income_routes.py   # Income management
│   │   ├── budget_routes.py   # Budget management
│   │   ├── category_routes.py # Category management
│   │   ├── transaction_routes.py # Transaction management
│   │   ├── analytics_routes.py # Analytics & insights
│   │   ├── user_routes.py     # User management
│   │   └── advanced_finance_routes.py # Advanced features
│   └── utils/
│       ├── auth.py            # Authentication utilities
│       ├── helpers.py         # Helper functions
│       └── encryption.py      # Encryption utilities
├── ml_models/
│   ├── expense_predictor.py   # ML category prediction
│   ├── anomaly_detector.py    # Fraud detection
│   └── calculators.py         # Financial calculators
├── database/
│   └── init_db.py             # Database initialization
├── frontend/                   # Frontend templates (HTML/CSS/JS)
├── tests/                     # Unit tests
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file

```

## 🔧 Installation

### Prerequisites
- Python 3.8+
- MySQL 5.7+
- pip

### Setup

1. **Clone/Extract the project**
```bash
cd finance
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Setup MySQL Database**
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE finance_app;"
```

5. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your database credentials and API keys
```

6. **Initialize database**
```bash
python database/init_db.py
```

7. **Run the application**
```bash
python backend/app.py
```

The API will run on `http://localhost:5000`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/change-password` - Change password

### Expenses
- `GET /api/expenses/` - Get all expenses
- `POST /api/expenses/` - Create expense
- `PUT /api/expenses/<id>` - Update expense
- `DELETE /api/expenses/<id>` - Delete expense
- `GET /api/expenses/daily-log` - Get daily log

### Income
- `GET /api/income/` - Get all income
- `POST /api/income/` - Add income
- `GET /api/income/summary` - Income summary

### Budgets
- `GET /api/budgets/` - Get budgets
- `POST /api/budgets/` - Create budget
- `PUT /api/budgets/<id>` - Update budget
- `DELETE /api/budgets/<id>` - Delete budget

### Categories
- `GET /api/categories/expense` - Get expense categories
- `GET /api/categories/income` - Get income categories
- `POST /api/categories/` - Create custom category
- `POST /api/categories/init-defaults` - Initialize default categories

### Analytics
- `GET /api/analytics/dashboard` - Dashboard summary
- `GET /api/analytics/monthly-summary` - Monthly summary
- `GET /api/analytics/category-analysis` - Category breakdown
- `GET /api/analytics/trends` - Spending trends
- `GET /api/analytics/health-score` - Financial health

### Advanced Finance
- `GET /api/advanced/loans` - Get loans
- `POST /api/advanced/loans` - Create loan
- `GET /api/advanced/loans/<id>/emi-schedule` - EMI schedule
- `GET /api/advanced/investments` - Get investments
- `GET /api/advanced/subscriptions` - Get subscriptions
- `GET /api/advanced/goals` - Get goals
- `GET /api/advanced/net-worth` - Calculate net worth

### Transactions
- `GET /api/transactions/` - Get transactions
- `GET /api/transactions/export` - Export as CSV
- `GET /api/transactions/recurring` - Get recurring transactions

### Users
- `GET /api/users/profile` - Get profile
- `PUT /api/users/profile` - Update profile
- `GET /api/users/preferences` - Get preferences
- `PUT /api/users/preferences` - Update preferences

## 🗄️ Database Schema

### Key Tables
- **users** - User accounts
- **accounts** - Bank/Cash accounts
- **transactions** - All income/expense transactions
- **categories** - Transaction categories
- **budgets** - Monthly budget limits
- **loans** - Loan tracking
- **investments** - Investment tracking
- **subscriptions** - Recurring subscriptions
- **goals** - Savings goals
- **financial_health** - Monthly health metrics
- **alerts** - Notifications and alerts
- **audit_logs** - Activity logs

## 🤖 ML/AI Models

### 1. Expense Prediction
- Random Forest classifier for category prediction
- Learns from user's transaction patterns
- Auto-suggests category for new transactions

### 2. Anomaly Detection
- Isolation Forest for fraud detection
- Detects unusual spending patterns
- Alerts on suspicious transactions

### 3. Financial Calculators
- **EMI Calculator**: Loan EMI calculation
- **SIP Calculator**: Investment return projection
- **Interest Calculator**: Compound/Simple interest
- **Net Worth Calculator**: Asset-Liability tracking
- **Debt Payoff Planner**: Optimal repayment strategy

## 🔐 Security Features

- Password hashing with bcrypt (12 rounds)
- JWT token-based authentication
- Data encryption for sensitive information
- CORS protection
- SQL injection prevention (ORM)
- Input validation and sanitization
- Activity audit logging
- Rate limiting (recommended for production)

## 📊 Sample API Calls

### Create an Expense
```bash
curl -X POST http://localhost:5000/api/expenses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50,
    "category_id": 1,
    "account_id": 1,
    "description": "Lunch",
    "notes": "With colleagues"
  }'
```

### Get Dashboard
```bash
curl -X GET http://localhost:5000/api/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Calculate SIP Returns
```bash
curl -X POST http://localhost:5000/api/advanced/sip/calculate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "monthly_investment": 5000,
    "annual_return": 12,
    "years": 10
  }'
```

## 🚀 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:create_app()
```

### Using Docker (optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
```

## 📈 Future Enhancements

- [ ] Mobile app (React Native/Flutter)
- [ ] Real-time notifications
- [ ] Advanced charting library
- [ ] Currency conversion API integration
- [ ] Bank account integration (API)
- [ ] OCR for receipt scanning
- [ ] Advanced ML models
- [ ] Goal-based savings automation
- [ ] Financial advisor chatbot

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📄 License

MIT License

## 📞 Support

For support, email support@financeapp.com or open an issue on GitHub.

---

Built with ❤️ using Python, Flask, and Machine Learning
