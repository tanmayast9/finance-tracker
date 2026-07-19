"""
One-time migration: add phone_verified column to users table if it doesn't exist.
Run once: python -m database.add_phone_verified
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app, db
from sqlalchemy import text

def run():
    app = create_app()
    with app.app_context():
        try:
            db.session.execute(text(
                "ALTER TABLE users ADD COLUMN phone_verified BOOLEAN DEFAULT FALSE"
            ))
            db.session.commit()
            print("Added phone_verified column to users table.")
        except Exception as e:
            if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                print("Column phone_verified already exists.")
            else:
                raise

if __name__ == "__main__":
    run()
