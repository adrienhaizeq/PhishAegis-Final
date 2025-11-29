# simple_check.py
from app import app, db

print("🔍 Checking database connection...")

try:
    with app.app_context():
        # Try to create all tables
        db.create_all()
        print("✅ SUCCESS: Database tables created!")
        print("🎉 Your app should work now!")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\n💡 Let's try to force create tables...")
    
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("✅ FORCE SUCCESS: Tables recreated!")
    except Exception as e2:
        print(f"❌ FORCE FAILED: {e2}")