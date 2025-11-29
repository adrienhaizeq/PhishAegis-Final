from app import app, db

# Create a fresh database
with app.app_context():
    db.drop_all()   # drops old tables if any
    db.create_all() # creates new tables

print("Database reset successfully!")
