"""
One-time migration: add monthly_income and salary_day columns to users table if missing.
Run once: python -m database.add_salary_fields
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app import create_app, db
from sqlalchemy import text

def run():
    app = create_app()
    with app.app_context():
        for col, sql in [
            ("monthly_income", "ALTER TABLE users ADD COLUMN monthly_income DOUBLE DEFAULT 0"),
            ("salary_day", "ALTER TABLE users ADD COLUMN salary_day INT NULL"),
        ]:
            try:
                db.session.execute(text(sql))
                db.session.commit()
                print(f"Added {col} column to users table.")
            except Exception as e:
                if "Duplicate column" in str(e) or "already exists" in str(e).lower():
                    print(f"Column {col} already exists.")
                else:
                    raise

if __name__ == "__main__":
    run()
