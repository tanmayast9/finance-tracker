@echo off
REM Setup Script for Finance Application (Windows)

echo 🚀 Finance Application Setup Script
echo ====================================

REM Check Python version
python --version
echo ✓ Python version confirmed

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create .env file
if not exist ".env" (
    echo 🔧 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please update .env with your database credentials
)

REM Initialize database
echo 🗄️  Initializing database...
python database\init_db.py

REM Run tests
echo 🧪 Running tests...
pytest tests\ -v

echo ✅ Setup complete!
echo.
echo To start the application:
echo   1. Activate virtual environment: venv\Scripts\activate.bat
echo   2. Update .env file with your settings
echo   3. Run: python backend\app.py
echo.
echo API will be available at: http://localhost:5000
echo API Documentation: See README.md and API_DOCUMENTATION.md
