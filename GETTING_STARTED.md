# Getting Started Guide - Finance Application

## 🎯 Quick Start (5 Minutes)

### Step 1: Clone/Extract the Project
```bash
cd finance
```

### Step 2: Run Setup Script
**On Windows:**
```bash
setup.bat
```

**On Linux/Mac:**
```bash
bash setup.sh
```

### Step 3: Configure Environment
Edit `.env` file with your database credentials:
```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=finance_app
FLASK_ENV=development
```

### Step 4: Create MySQL Database
```bash
mysql -u root -p
CREATE DATABASE finance_app;
EXIT;
```

### Step 5: Start the Application
```bash
python backend/app.py
```

API will run at: `http://localhost:5000`

---

## 📱 Using the Application

### 1. Register a New User
```bash
curl -X POST http://localhost:5000/api/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "myuser",
    "email": "myuser@example.com",
    "password": "password123",
    "full_name": "My Name"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "myuser@example.com",
    "password": "password123"
  }'
```

Save the returned token for subsequent requests.

### 3. Initialize Default Categories
```bash
curl -X POST http://localhost:5000/api/categories/init-defaults \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Create an Account
```bash
curl -X POST http://localhost:5000/api/users/accounts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "account_name": "My Bank Account",
    "account_type": "bank",
    "balance": 10000.00,
    "currency": "USD"
  }'
```

### 5. Add an Expense
```bash
curl -X POST http://localhost:5000/api/expenses/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 50.00,
    "category_id": 1,
    "account_id": 1,
    "description": "Lunch",
    "notes": "With colleagues"
  }'
```

### 6. View Dashboard
```bash
curl -X GET http://localhost:5000/api/analytics/dashboard \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🧪 Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_api.py -v

# With coverage report
pytest tests/ --cov=backend
```

---

## 🏗️ Project Structure Overview

```
finance/
├── backend/                      # Flask API backend
│   ├── app.py                   # Application entry point
│   ├── models.py                # Database models
│   ├── config.py                # Configuration
│   ├── routes/                  # API route handlers
│   │   ├── auth_routes.py
│   │   ├── expense_routes.py
│   │   ├── income_routes.py
│   │   ├── budget_routes.py
│   │   ├── analytics_routes.py
│   │   ├── category_routes.py
│   │   ├── transaction_routes.py
│   │   ├── user_routes.py
│   │   └── advanced_finance_routes.py
│   └── utils/                   # Utility modules
│       ├── auth.py
│       ├── helpers.py
│       └── encryption.py
├── ml_models/                   # ML/AI modules
│   ├── expense_predictor.py     # Category prediction
│   ├── anomaly_detector.py      # Fraud detection
│   └── calculators.py           # Financial calculators
├── database/                    # Database utilities
│   └── init_db.py
├── frontend/                    # Web frontend
│   ├── index.html
│   ├── style.css
│   └── script.js
├── tests/                       # Unit tests
│   ├── test_api.py
│   └── test_ml.py
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── README.md                    # Full documentation
├── API_DOCUMENTATION.md         # API reference
└── GETTING_STARTED.md          # This file
```

---

## 🔑 Key Features

### ✅ Authentication & Security
- Secure JWT-based authentication
- Password hashing with bcrypt
- Data encryption for sensitive info

### 💰 Core Finance
- Income and expense tracking
- Multi-account support
- Category management
- Daily transaction logs

### 📊 Analytics
- Dashboard with key metrics
- Spending trends and patterns
- Financial health score
- Category-wise breakdowns

### 🎯 Budgeting
- Monthly budget limits
- Budget alerts and warnings
- Budget adherence tracking

### 🏦 Advanced Finance
- Loan EMI calculation
- Investment tracking
- SIP calculator
- Debt payoff planning
- Subscription tracking
- Goals management
- Net worth calculation

### 🤖 AI/ML Features
- Automatic expense categorization
- Fraud/anomaly detection
- Smart spending insights
- Financial health scoring

---

## 🔧 Configuration

### Environment Variables (.env)
```
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=finance_app
DB_PORT=3306

# Flask
FLASK_ENV=development
FLASK_APP=backend/app.py
SECRET_KEY=your_secret_key
JWT_SECRET_KEY=your_jwt_secret

# Security
ENCRYPTION_KEY=your_encryption_key

# ML Models
MODEL_PATH=ml_models/models
DATA_PATH=ml_models/data
```

---

## 🐛 Troubleshooting

### Database Connection Error
```
Error: Access denied for user 'root'
Solution: Check DB_USER, DB_PASSWORD, and DB_HOST in .env
```

### JWT Token Error
```
Error: Invalid or expired token
Solution: Generate new token using login endpoint
```

### Port Already in Use
```
Error: Address already in use
Solution: Kill process on port 5000 or use different port:
  python backend/app.py --port=5001
```

### Database Initialization Failed
```
Solution: 
  1. Check MySQL is running
  2. Check database exists
  3. Run: python database/init_db.py
```

---

## 📚 API Documentation

See `API_DOCUMENTATION.md` for complete API reference with all endpoints.

Common endpoints:
- `POST /api/auth/login` - User login
- `POST /api/expenses/` - Add expense
- `POST /api/income/` - Add income
- `GET /api/analytics/dashboard` - Get dashboard
- `POST /api/advanced/loans` - Add loan
- `GET /api/advanced/net-worth` - Calculate net worth

---

## 🚀 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:create_app()
```

### Using Docker (Optional)
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:create_app()"]
```

---

## 💡 Tips & Best Practices

1. **Always use HTTPS in production**
2. **Keep SECRET_KEY and JWT_SECRET_KEY secure**
3. **Regular database backups**
4. **Monitor API usage and implement rate limiting**
5. **Use environment variables for sensitive data**
6. **Test thoroughly before deployment**
7. **Keep ML models updated with new data**

---

## 📞 Support

For issues or questions:
1. Check README.md and API_DOCUMENTATION.md
2. Review error messages carefully
3. Check database connectivity
4. Verify environment variables

---

## 🎓 Learning Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- Scikit-learn ML: https://scikit-learn.org/
- JWT Authentication: https://jwt.io/

---

Happy coding! 🎉
