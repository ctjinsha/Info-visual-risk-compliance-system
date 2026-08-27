from app import app, db
from models import User

with app.app_context():
    # Check if user already exists to avoid duplicates
    if not User.query.first():
        new_user = User(name="Alex Johnson", occupation="Software Engineer", age=32)
        db.session.add(new_user)
        db.session.commit()
        print(f"Success! User '{new_user.name}' created with ID: {new_user.id}")
    else:
        print("A user already exists in the database.")