from app import app, db
import models

with app.app_context():
    print(f"Connecting to database: {db.engine.url.render_as_string(hide_password=True)}")
    db.drop_all()
    db.create_all()
    print("Database schema successfully recreated for all OptimaTrack models!")