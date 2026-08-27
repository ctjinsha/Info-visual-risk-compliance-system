import os
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = 'super_secret_development_key' 

# NEW: Tell Flask where to save uploaded profile pictures
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Creates the folder if it doesn't exist

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import User, BehavioralEntry

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the logged-in user's data to display on the dashboard
    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id  
            return redirect(url_for('home')) 
        else:
            flash("Invalid email or password. Please try again.", "error")
            
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return redirect(url_for('login'))

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already exists. Please sign in.", "error")
        return redirect(url_for('login'))

    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    
    flash("Account created successfully! You can now log in.", "success")
    return redirect(url_for('login'))

# NEW: Profile Page Route
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    
    if request.method == 'POST':
        user.name = request.form.get('name')
        user.age = request.form.get('age')
        
        # Handle Image Upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename # Save the file name to the database
                
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
        
    return render_template('profile.html', user=user)

@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    return redirect(url_for('login'))

@app.route('/api/entries', methods=['POST'])
def add_entry():
    data = request.get_json()
    user_id = session.get('user_id') 
    
    if not user_id or not data:
        return jsonify({"error": "Unauthorized or missing data"}), 400
        
    new_entry = BehavioralEntry(
        user_id=user_id,
        entry_type=data.get('entry_type'),
        category=data.get('category'),
        description=data.get('description'),
        recurring_frequency=data.get('recurring_frequency'),
        impact_on_goals=data.get('impact_on_goals')
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({"message": "Entry saved successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)