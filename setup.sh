#!/bin/bash
# Setup Script for Finance Application

echo "🚀 Finance Application Setup Script"
echo "===================================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv
source venv/Scripts/activate || source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env file
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your database credentials"
fi

# Initialize database
echo "🗄️  Initializing database..."
python database/init_db.py

# Run tests
echo "🧪 Running tests..."
pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/Scripts/activate"
echo "  2. Update .env file with your settings"
echo "  3. Run: python backend/app.py"
echo ""
echo "API will be available at: http://localhost:5000"
echo "API Documentation: See README.md and API_DOCUMENTATION.md"
