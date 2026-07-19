import pymysql
from sqlalchemy import create_engine, text

# Try different connection configurations
configs = [
    {'host': '127.0.0.1', 'user': 'root', 'password': 'root'},
    {'host': 'localhost', 'user': 'root', 'password': 'root'},
    {'host': '127.0.0.1', 'user': 'root', 'password': ''},
    {'host': 'localhost', 'user': 'root', 'password': ''},
]

for i, config in enumerate(configs, 1):
    try:
        print(f"Trying config {i}: {config}")
        connection = pymysql.connect(port=3306, **config)
        print("✅ Connection successful!")
        
        # Create database
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS finance")
        print("✅ Database 'finance' created/selected!")
        
        # Test SQLAlchemy
        uri = f"mysql+pymysql://{config['user']}:{config['password']}@{config['host']}:3306/finance"
        engine = create_engine(uri)
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            print("✅ SQLAlchemy connection successful!")
        
        connection.close()
        break
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        print()

print("\nIf all connections failed, please check:")
print("1. MySQL server is running (services.msc)")
print("2. MySQL installation details")
print("3. Try XAMPP/WAMP if using local development")
