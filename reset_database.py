from enhanced_models import db, User, BankAccount, Transaction, Budget, Loan, Investment, Subscription, BudgetGoal, Calculation
from enhanced_app import app

def reset_database():
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped")
        
        # Create all tables with new schema
        db.create_all()
        print("All tables created with new schema")
        
        print("Database reset successfully!")

if __name__ == '__main__':
    reset_database()
