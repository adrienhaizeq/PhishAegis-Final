# check_db.py
from app import app, db
import mysql.connector

def check_database():
    try:
        # First, check if we can connect to MySQL
        conn = mysql.connector.connect(
            host='localhost',
            user='root',  # change if different
            password=''   # your MySQL password
        )
        print("✅ Connected to MySQL server")
        
        # Check if database exists
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES LIKE 'phisaegish_db'")
        result = cursor.fetchone()
        
        if result:
            print("✅ Database 'phisaegish_db' exists")
        else:
            print("❌ Database 'phisaegish_db' doesn't exist")
            cursor.execute("CREATE DATABASE phisaegish_db")
            print("✅ Database 'phisaegish_db' created")
            
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ MySQL connection error: {e}")

def create_tables():
    try:
        with app.app_context():
            print("🔄 Creating tables...")
            db.create_all()
            print("✅ All tables created successfully!")
    except Exception as e:
        print(f"❌ Table creation error: {e}")

if __name__ == '__main__':
    check_database()
    create_tables()