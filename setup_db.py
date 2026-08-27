from app import app, db
import models

with app.app_context():
    db.drop_all() # This deletes the old tables
    db.create_all() # This creates the new tables with email/passwords
    print("Database completely reset with new User columns!")