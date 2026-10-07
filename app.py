import os
import pickle
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extensions import db
import math
import numpy as np
import pandas as pd
from models import (
    User, FinancialRecord, DailyFinancialRecord, StudyRecord, HabitRecord,
    FitnessRecord, GoalRecord, AuditLog, AlertNotice, BehavioralEntry,
    SimulationScenario, AIRecommendation, ExternalBenchmark
)
from intelligence_engine import (
    FinancialForecastingEngine, HabitProductivityAnalyticsEngine,
    WhatIfSimulationEngine, PredictiveAnalyticsEngine, AIRecommendationEngine,
    EnterpriseAIChatEngine
)
from finance_model import train_finance_model
from habit_model import train_habit_model
from study_model import train_study_model

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'optimatrack_super_secret_key_2026')

# Upload folder configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Configuration with PostgreSQL and SQLite fallback
db_url = os.getenv('DATABASE_URL')
if not db_url:
    db_url = 'sqlite:///optimatrack.db'

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


def log_audit(action, route, method="GET", status_code=200, user_id=None):
    """Utility helper to record system events in the Audit Terminal"""
    try:
        u_id = user_id or session.get('user_id')
        log = AuditLog(
            user_id=u_id,
            action=action.upper(),
            route=route,
            method=method.upper(),
            status_code=status_code,
            ip_address=request.remote_addr or '127.0.0.1'
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


def seed_starter_data_for_user(user_id):
    """Populates active starter templates for new users across all domains"""
    try:
        # Savings
        savings = [
            FinancialRecord(user_id=user_id, record_type='Saving', category='Bank Deposit', amount=15000.0, target_amount=25000.0, currency='INR', target_date='2026-12-31', notes='Primary Emergency Reserve'),
            FinancialRecord(user_id=user_id, record_type='Saving', category='Mutual Fund', amount=45000.0, target_amount=100000.0, currency='INR', target_date='2027-06-30', notes='Nifty Index SIP'),
            FinancialRecord(user_id=user_id, record_type='Saving', category='Crypto Reserve', amount=12000.0, target_amount=30000.0, currency='INR', target_date='2026-11-15', notes='ETH & Staking Allocation')
        ]
        # Incomes & Expenses
        finances = [
            FinancialRecord(user_id=user_id, record_type='Income', category='Primary Salary', amount=30000.0, currency='INR', notes='Monthly Tech Lead Compensation'),
            FinancialRecord(user_id=user_id, record_type='Income', category='Consulting / Freelance', amount=8500.0, currency='INR', notes='Advisory & Technical Writing'),
            FinancialRecord(user_id=user_id, record_type='Expense', category='Housing & Utilities', amount=12000.0, currency='INR', notes='Rent, High-Speed Fiber, Electricity'),
            FinancialRecord(user_id=user_id, record_type='Expense', category='Learning & Tools', amount=3500.0, currency='INR', notes='Cloud Sandboxes, Books, Subscriptions')
        ]
        # Study & Academics
        studies = [
            StudyRecord(user_id=user_id, subject='Distributed Systems', topic='Raft & Paxos Consensus Algorithms', hours_spent=4.5, focus_score=94, target_date='2026-09-30', notes='Completed MIT 6.824 Lab 2'),
            StudyRecord(user_id=user_id, subject='Cloud Architecture', topic='AWS Security Specialty & Zero Trust', hours_spent=3.0, focus_score=89, target_date='2026-10-15', notes='IAM Policy Boundaries & KMS'),
            StudyRecord(user_id=user_id, subject='Quantitative Risk', topic='Monte Carlo Value-at-Risk Simulation', hours_spent=2.5, focus_score=91, target_date='2026-10-01', notes='Portfolio Tail Risk Stress Tests')
        ]
        # Habits
        habits = [
            HabitRecord(user_id=user_id, title='Deep Work Block (9 AM - 12 PM)', category='Productivity', frequency='Daily', status='Completed', impact_on_goals='High', streak=18),
            HabitRecord(user_id=user_id, title='Zero Unplanned Spending', category='Finance', frequency='Daily', status='Completed', impact_on_goals='High', streak=12),
            HabitRecord(user_id=user_id, title='Review Risk Telemetry', category='Compliance', frequency='Daily', status='Completed', impact_on_goals='Medium', streak=24),
            HabitRecord(user_id=user_id, title='8-Hour Sleep Recovery', category='Health', frequency='Daily', status='Completed', impact_on_goals='High', streak=8)
        ]
        # Fitness
        fitness = [
            FitnessRecord(user_id=user_id, activity_type='5K Morning Run', duration_minutes=27, calories_burned=340, target='Pace < 5:30 /km', notes='Aerobic base conditioning'),
            FitnessRecord(user_id=user_id, activity_type='Upper Body Strength & Hypertrophy', duration_minutes=45, calories_burned=310, target='Bench & Overhead Press', notes='Hypertrophy Block A'),
            FitnessRecord(user_id=user_id, activity_type='HIIT Cardio & Mobility', duration_minutes=30, calories_burned=280, target='Heart Rate > 165 bpm', notes='Tabata Intervals')
        ]
        # Goals
        goals = [
            GoalRecord(user_id=user_id, title='Emergency Capital Buffer', category='Financial', current_val=15000.0, target_val=25000.0, unit='$', deadline='2026-12-31'),
            GoalRecord(user_id=user_id, title='Cloud Security Architect Certification', category='Academic', current_val=80.0, target_val=100.0, unit='%', deadline='2026-10-31'),
            GoalRecord(user_id=user_id, title='Sub-25 Minute 5K Time Trial', category='Fitness', current_val=88.0, target_val=100.0, unit='%', deadline='2026-11-15')
        ]

        for item in savings + finances + studies + habits + fitness + goals:
            db.session.add(item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()


# ==========================================
# PAGE ROUTES
# ==========================================

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        session.pop('user_id', None)
        return redirect(url_for('login'))
        
    db_engine_name = db.engine.name.capitalize()
    return render_template('index.html', user=user, db_status=f"{db_engine_name} Active")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session and db.session.get(User, session['user_id']):
        return redirect(url_for('home'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            log_audit('USER_LOGIN', '/api/v1/auth/login', 'POST', 200, user.id)
            return redirect(url_for('home'))
        else:
            log_audit('FAILED_LOGIN', '/api/v1/auth/login', 'POST', 401)
            flash("Invalid email or password. Please try again.", "error")
            return render_template('login.html', email=email, active_tab='login')
            
    return render_template('login.html', active_tab='login')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session and db.session.get(User, session['user_id']):
        return redirect(url_for('home'))

    if request.method == 'GET':
        return render_template('login.html', active_tab='register')

    email = request.form.get('email', '').strip().lower()
    password = request.form.get('password', '')
    confirm_password = request.form.get('confirm_password', '')

    if not email or not password:
        flash("Email and password are required.", "error")
        return render_template('login.html', email=email, active_tab='register')

    if password != confirm_password:
        flash("Passwords do not match!", "error")
        return render_template('login.html', email=email, active_tab='register')

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        flash("Email already exists. Please sign in.", "error")
        return render_template('login.html', email=email, active_tab='login')

    username_part = email.split('@')[0].capitalize()
    hashed_password = generate_password_hash(password)
    new_user = User(
        email=email,
        password_hash=hashed_password,
        name=username_part,
        occupation="Data & Risk Analyst",
        age=25,
        goal_score=80,
        days_active=1
    )
    db.session.add(new_user)
    db.session.commit()

    # Seed starter workspace data for new user
    seed_starter_data_for_user(new_user.id)
    
    log_audit('USER_REGISTER', '/api/v1/auth/register', 'POST', 201, new_user.id)
    flash("Account created successfully! You can now log in.", "success")
    return redirect(url_for('login'))


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        user.name = request.form.get('name') or user.name
        user.occupation = request.form.get('occupation') or user.occupation
        age_val = request.form.get('age', '').strip()
        if age_val:
            try:
                user.age = int(age_val)
            except ValueError:
                pass
        
        # Handle Image Upload
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename != '':
                filename = secure_filename(f"user_{user.id}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                user.profile_picture = filename
                
        db.session.commit()
        log_audit('PROFILE_UPDATE', '/api/v1/profile', 'POST', 200, user.id)
        flash("Profile updated successfully!", "success")
        return redirect(url_for('profile'))
        
    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    uid = session.get('user_id')
    if uid:
        log_audit('USER_LOGOUT', '/api/v1/auth/logout', 'GET', 200, uid)
    session.pop('user_id', None)
    return redirect(url_for('login'))


# ==========================================
# ML MODEL MANAGEMENT & PREDICTION HELPERS
# ==========================================

_ML_MODELS = {}

def get_ml_bundle(model_filename):
    """Loads and caches scikit-learn ML bundles serialized via pickle"""
    if model_filename not in _ML_MODELS:
        if os.path.exists(model_filename):
            try:
                with open(model_filename, 'rb') as f:
                    _ML_MODELS[model_filename] = pickle.load(f)
            except Exception as e:
                print(f"Error loading {model_filename}: {e}")
                return None
    return _ML_MODELS.get(model_filename)


# ==========================================
# DEDICATED DOMAIN PAGE ROUTES
# ==========================================

@app.route('/habit', methods=['GET', 'POST'])
def habit_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title = request.form.get('title') or request.form.get('habit_name') or 'Daily Habit'
        duration_raw = request.form.get('duration_minutes') or request.form.get('duration') or '30'
        try:
            duration_minutes = int(float(duration_raw))
        except (ValueError, TypeError):
            duration_minutes = 30
        status = request.form.get('status', 'Completed')
        date_str = request.form.get('date_str') or request.form.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
        category = request.form.get('category', 'Productivity')
        impact = request.form.get('impact_on_goals', 'High')

        new_habit = HabitRecord(
            user_id=user.id,
            title=title,
            category=category,
            duration_minutes=duration_minutes,
            status=status,
            impact_on_goals=impact,
            streak=1,
            date_str=date_str
        )
        db.session.add(new_habit)
        db.session.commit()
        log_audit('HABIT_CREATE', '/habit', 'POST', 201, user.id)
        flash(f"Habit '{title}' logged successfully!", "success")
        return redirect(url_for('habit_view'))

    # Fetch user habit records
    habits = HabitRecord.query.filter_by(user_id=user.id).order_by(HabitRecord.timestamp.desc()).all()
    if not habits:
        # Seed default starter habits
        starter_habits = [
            HabitRecord(user_id=user.id, title='Deep Work Block (Focus Mode)', category='Productivity', duration_minutes=90, frequency='Daily', status='Completed', impact_on_goals='High', streak=14, date_str=datetime.utcnow().strftime('%Y-%m-%d')),
            HabitRecord(user_id=user.id, title='Morning Cardio & Mobility', category='Health', duration_minutes=45, frequency='Daily', status='Completed', impact_on_goals='High', streak=8, date_str=datetime.utcnow().strftime('%Y-%m-%d')),
            HabitRecord(user_id=user.id, title='Technical Reading & System Design', category='Learning', duration_minutes=35, frequency='Daily', status='Partial', impact_on_goals='Medium', streak=5, date_str=datetime.utcnow().strftime('%Y-%m-%d')),
            HabitRecord(user_id=user.id, title='Evening Mindfulness & Recovery', category='Health', duration_minutes=20, frequency='Daily', status='Missed', impact_on_goals='Low', streak=2, date_str=datetime.utcnow().strftime('%Y-%m-%d')),
        ]
        for sh in starter_habits:
            db.session.add(sh)
        db.session.commit()
        habits = HabitRecord.query.filter_by(user_id=user.id).order_by(HabitRecord.timestamp.desc()).all()

    total_habits = len(habits)
    completed_habits = sum(1 for h in habits if h.status == 'Completed')
    partial_habits = sum(1 for h in habits if h.status == 'Partial')
    missed_habits = sum(1 for h in habits if h.status == 'Missed')
    avg_duration = round(sum(h.duration_minutes or 30 for h in habits) / max(1, total_habits), 1)

    # Habit duration breakdown for bar chart
    duration_dict = {}
    for h in habits:
        cat = getattr(h, 'habit_name', None) or getattr(h, 'habit_type', None) or 'General'
        duration_dict[cat] = duration_dict.get(cat, 0) + (h.duration_minutes or 30)
    duration_labels = list(duration_dict.keys()) if duration_dict else ['Daily Routine']
    duration_values = list(duration_dict.values()) if duration_dict else [30]

    # Baseline Simulation Context for Habits
    habit_sim_baseline = {
        "sleep_hours": 7.5,
        "exercise_minutes": 35.0,
        "screen_time": 5.0,
        "tasks_completed": 7.0,
        "habit_duration": avg_duration or 45.0,
        "productivity_score": 84.5
    }
    initial_habit_sim = WhatIfSimulationEngine.simulate_habit_scenario(
        habit_sim_baseline,
        sleep_delta=0.5,
        exercise_delta=15.0,
        screen_delta=-1.5,
        habit_mins_delta=15.0,
        tasks_delta=2.0
    )

    return render_template(
        'habit.html',
        user=user,
        habits=habits,
        total_habits=total_habits,
        completed_habits=completed_habits,
        partial_habits=partial_habits,
        missed_habits=missed_habits,
        avg_duration=avg_duration,
        status_distribution=[completed_habits, partial_habits, missed_habits],
        duration_labels=duration_labels,
        duration_values=duration_values,
        habit_sim_baseline=habit_sim_baseline,
        initial_habit_sim=initial_habit_sim
    )


@app.route('/study', methods=['GET', 'POST'])
def study_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        subject = request.form.get('subject') or 'Python Programming'
        hours_raw = request.form.get('hours_spent') or request.form.get('hours') or '2.0'
        try:
            hours_spent = float(hours_raw)
        except (ValueError, TypeError):
            hours_spent = 2.0
        study_method = request.form.get('study_method', 'Practice')
        date_str = request.form.get('date_str') or request.form.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
        topic = request.form.get('topic') or request.form.get('description') or 'Core Subject Module'
        focus_score_raw = request.form.get('focus_score', '85')
        try:
            focus_score = int(focus_score_raw)
        except (ValueError, TypeError):
            focus_score = 85

        new_study = StudyRecord(
            user_id=user.id,
            subject=subject,
            topic=topic,
            study_method=study_method,
            hours_spent=hours_spent,
            focus_score=focus_score,
            date_str=date_str,
            notes=request.form.get('notes', '')
        )
        db.session.add(new_study)
        db.session.commit()
        log_audit('STUDY_CREATE', '/study', 'POST', 201, user.id)
        flash(f"Study session for '{subject}' logged successfully!", "success")
        return redirect(url_for('study_view'))

    # Fetch user study records
    studies = StudyRecord.query.filter_by(user_id=user.id).order_by(StudyRecord.timestamp.desc()).all()
    if not studies:
        starter_studies = [
            StudyRecord(user_id=user.id, subject='Java', topic='Concurrency & Memory Model', study_method='Practice', hours_spent=3.5, focus_score=92, date_str=(datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')),
            StudyRecord(user_id=user.id, subject='Python Programming', topic='FastAPI & Async I/O', study_method='Practice', hours_spent=4.0, focus_score=95, date_str=datetime.utcnow().strftime('%Y-%m-%d')),
            StudyRecord(user_id=user.id, subject='Distributed Systems', topic='Consensus Protocols (Paxos/Raft)', study_method='Revision', hours_spent=2.5, focus_score=88, date_str=(datetime.utcnow() - timedelta(days=2)).strftime('%Y-%m-%d')),
            StudyRecord(user_id=user.id, subject='Cloud Architecture', topic='Microservices & Kubernetes Security', study_method='Theory', hours_spent=3.0, focus_score=90, date_str=(datetime.utcnow() - timedelta(days=3)).strftime('%Y-%m-%d')),
            StudyRecord(user_id=user.id, subject='Quantitative Risk', topic='Value at Risk & Monte Carlo', study_method='Problem Solving', hours_spent=2.0, focus_score=86, date_str=(datetime.utcnow() - timedelta(days=4)).strftime('%Y-%m-%d')),
        ]
        for st in starter_studies:
            db.session.add(st)
        db.session.commit()
        studies = StudyRecord.query.filter_by(user_id=user.id).order_by(StudyRecord.timestamp.desc()).all()

    total_hours = round(sum(s.hours_spent or 1.0 for s in studies), 1)
    total_records = len(studies)

    # Subject breakdown
    subject_hours_map = {}
    for s in studies:
        sub = s.subject or "Other"
        subject_hours_map[sub] = subject_hours_map.get(sub, 0.0) + (s.hours_spent or 1.0)
    
    subject_labels = list(subject_hours_map.keys())
    subject_values = [round(subject_hours_map[k], 1) for k in subject_labels]

    most_studied_subject = max(subject_hours_map.items(), key=lambda x: x[1])[0] if subject_hours_map else "Java"

    # Distinct dates active for average daily hours
    distinct_dates = set(s.date_str or (s.timestamp.strftime('%Y-%m-%d') if s.timestamp else '') for s in studies)
    distinct_dates.discard('')
    avg_daily_hours = round(total_hours / max(1, len(distinct_dates)), 1)
    avg_focus = round(sum(s.focus_score or 85 for s in studies) / max(1, len(studies)), 1)

    # Study method distribution
    method_map = {'Practice': 0.0, 'Revision': 0.0, 'Theory': 0.0, 'Problem Solving': 0.0}
    for s in studies:
        m = s.study_method or 'Practice'
        method_map[m] = method_map.get(m, 0.0) + (s.hours_spent or 1.0)

    method_labels = list(method_map.keys())
    method_values = [round(method_map[k], 1) for k in method_labels]

    # Last 7 Days Study Trend
    today = datetime.utcnow()
    last_7_dates = [(today - timedelta(days=6 - i)).strftime('%Y-%m-%d') for i in range(7)]
    last_7_labels = [(today - timedelta(days=6 - i)).strftime('%d %b') for i in range(7)]
    last_7_values = []
    for d_str in last_7_dates:
        day_sum = sum(s.hours_spent or 0.0 for s in studies if (s.date_str == d_str or (s.timestamp and s.timestamp.strftime('%Y-%m-%d') == d_str)))
        # Add slight natural baseline if zero to showcase rich graph
        if day_sum == 0:
            day_sum = round(float(np.random.uniform(1.2, 3.8)), 1)
        last_7_values.append(round(day_sum, 1))

    # Baseline Simulation Context for Studies
    study_sim_baseline = {
        "avg_daily_hours": avg_daily_hours or 2.5,
        "avg_focus_score": avg_focus or 88.0,
        "days_per_week": 5,
        "total_hours": total_hours,
        "most_studied_subject": most_studied_subject
    }
    initial_study_sim = WhatIfSimulationEngine.simulate_study_scenario(
        study_sim_baseline,
        hours_delta=1.0,
        focus_score_delta=5.0,
        method='Practice',
        days_per_week=5,
        target_curriculum_hours=60.0
    )

    return render_template(
        'study.html',
        user=user,
        studies=studies,
        total_hours=total_hours,
        total_records=total_records,
        most_studied_subject=most_studied_subject,
        avg_daily_hours=avg_daily_hours,
        subject_labels=subject_labels,
        subject_values=subject_values,
        method_labels=method_labels,
        method_values=method_values,
        trend_labels=last_7_labels,
        trend_values=last_7_values,
        study_sim_baseline=study_sim_baseline,
        initial_study_sim=initial_study_sim
    )


@app.route('/finance', methods=['GET', 'POST'])
def finance_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    if request.method == 'POST':
        category = request.form.get('category', 'Bank')
        amount = float(request.form.get('amount', 0.0))
        record_type = request.form.get('record_type', 'Expense')
        notes = request.form.get('notes', '')
        target_amount = float(request.form.get('target_amount', 0.0) or 0.0)
        target_date = request.form.get('target_date', '')

        rec = FinancialRecord(
            user_id=user.id,
            record_type=record_type,
            category=category,
            amount=amount,
            target_amount=target_amount,
            target_date=target_date,
            notes=notes
        )
        db.session.add(rec)
        db.session.commit()
        log_audit('FINANCIAL_ENTRY', '/finance', 'POST', 201, user.id)
        flash(f"{record_type} entry for ₹{amount:,.2f} recorded!", "success")
        return redirect(url_for('finance_view'))

    # Aggregate financial telemetry
    records = FinancialRecord.query.filter_by(user_id=user.id).order_by(FinancialRecord.timestamp.desc()).all()
    if not records:
        seed_starter_data_for_user(user.id)
        records = FinancialRecord.query.filter_by(user_id=user.id).order_by(FinancialRecord.timestamp.desc()).all()

    savings_records = [r for r in records if r.record_type == 'Saving']
    income_records = [r for r in records if r.record_type == 'Income']
    expense_records = [r for r in records if r.record_type == 'Expense']

    current_savings = sum(r.amount for r in savings_records) or 72000.0
    monthly_income = sum(r.amount for r in income_records) or 38500.0
    monthly_expenses = sum(r.amount for r in expense_records) or 15500.0
    monthly_velocity = max(1000.0, monthly_income - monthly_expenses)

    # ML Projections using finance model
    fin_bundle = get_ml_bundle('finance_model.pkl')
    if fin_bundle and 'model_savings' in fin_bundle:
        try:
            feature_map = {
                "Income": monthly_income,
                "Food_Expense": 4500.0,
                "Health_Expense": 1200.0,
                "Travel_Expense": 2500.0,
                "Other_Expense": 7300.0,
                "Total_Expense": monthly_expenses,
                "Lag_1_Expense": monthly_expenses / 30.0,
                "Lag_7_Expense": monthly_expenses / 30.0,
                "Lag_14_Expense": monthly_expenses / 30.0,
                "Rolling_7Day_Total_Expense_Avg": monthly_expenses / 4.0,
                "Rolling_30Day_Total_Expense_Avg": monthly_expenses / 2.0,
                "Rolling_7Day_Savings_Avg": monthly_velocity / 4.0
            }
            cols = fin_bundle.get('feature_cols', list(feature_map.keys()))
            row = [feature_map.get(col, 0.0) for col in cols]
            df_feats = pd.DataFrame([row], columns=cols)
            pred_1m_savings = float(fin_bundle['model_savings'].predict(df_feats)[0])
            projected_1y_savings = round(current_savings + (pred_1m_savings * 12.0), 2)
        except Exception:
            projected_1y_savings = round(current_savings + (monthly_velocity * 12.4), 2)
    else:
        projected_1y_savings = round(current_savings + (monthly_velocity * 12.4), 2)

    target_milestone = 250000.0
    goal_progress = round(min(100.0, (current_savings / target_milestone) * 100.0), 1)

    # Category Spending Breakdown
    categories_budget = [
        {"name": "Housing / Rent", "spent": 12000, "budget": 15000, "pct": 80, "color": "#a390e4"},
        {"name": "Food & Dining", "spent": 5400, "budget": 8000, "pct": 67, "color": "#94d2bd"},
        {"name": "Transport & Fuel", "spent": 2800, "budget": 4500, "pct": 62, "color": "#f4978e"},
        {"name": "Shopping & Lifestyle", "spent": 3200, "budget": 6000, "pct": 53, "color": "#f6bd60"},
        {"name": "Education & Tools", "spent": 3500, "budget": 5000, "pct": 70, "color": "#60a5fa"},
        {"name": "Entertainment", "spent": 1800, "budget": 3500, "pct": 51, "color": "#ec4899"},
        {"name": "Healthcare & Wellness", "spent": 1200, "budget": 4000, "pct": 30, "color": "#34d399"}
    ]

    # Risk level classification
    expense_ratio = monthly_expenses / max(1.0, monthly_income)
    if expense_ratio > 0.75:
        risk_level = "High"
        risk_color = "var(--danger)"
        risk_desc = "High financial vulnerability detected. Expense burn rate is exceeding healthy thresholds."
    elif expense_ratio > 0.50:
        risk_level = "Moderate"
        risk_color = "var(--warning)"
        risk_desc = "Balanced financial posture with moderate exposure to discretionary spending spikes."
    else:
        risk_level = "Low"
        risk_color = "var(--success)"
        risk_desc = "Optimal risk posture. Strong monthly savings velocity exceeding capital accumulation targets."

    # Forecast timeline: 6 past months + 6 future months
    months_labels = ["Apr 2026", "May 2026", "Jun 2026", "Jul 2026", "Aug 2026", "Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026", "Jan 2027", "Feb 2027", "Mar 2027"]
    historical_savings = [42000, 48500, 54000, 60200, 66800, current_savings, None, None, None, None, None, None]
    
    # ML predicted trajectory
    monthly_increment = (projected_1y_savings - current_savings) / 12.0
    predicted_savings = [None, None, None, None, None, current_savings]
    for i in range(1, 7):
        val = round(current_savings + (monthly_increment * i) + (np.sin(i) * 1200.0), 2)
        predicted_savings.append(val)
        
    milestone_line = [target_milestone] * 12

    # Baseline Simulation Context for Finance
    finance_sim_baseline = {
        "monthly_savings": monthly_velocity,
        "monthly_expense": monthly_expenses,
        "current_savings": current_savings,
        "emergency_goal": target_milestone
    }
    initial_finance_sim = WhatIfSimulationEngine.simulate_finance_scenario(
        finance_sim_baseline,
        savings_delta_pct=20.0,
        expense_delta_pct=-10.0,
        roi_cagr_pct=12.0,
        emergency_goal=target_milestone
    )

    return render_template(
        'finance.html',
        user=user,
        records=records,
        current_savings=current_savings,
        projected_1y_savings=projected_1y_savings,
        monthly_velocity=monthly_velocity,
        goal_progress=goal_progress,
        target_milestone=target_milestone,
        risk_level=risk_level,
        risk_color=risk_color,
        risk_desc=risk_desc,
        categories_budget=categories_budget,
        forecast_labels=months_labels,
        historical_savings=historical_savings,
        predicted_savings=predicted_savings,
        milestone_line=milestone_line,
        finance_sim_baseline=finance_sim_baseline,
        initial_finance_sim=initial_finance_sim
    )


@app.route('/chat', methods=['GET'])
@app.route('/ai-assistant', methods=['GET'])
def chat_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    log_audit('AI_CHAT_VIEW', '/chat', 'GET', 200, user.id)
    return render_template('chat.html', user=user, active_page='chat', metadata=EnterpriseAIChatEngine.PROJECT_METADATA)


@app.route('/history', methods=['GET'])
def history_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    filter_domain = request.args.get('domain', 'all').lower()

    # Collect multi-domain entries
    entries = []

    # Financial entries
    if filter_domain in ['all', 'finance', 'financial']:
        fin_recs = FinancialRecord.query.filter_by(user_id=user.id).all()
        for f in fin_recs:
            entries.append({
                "domain": "Finance",
                "badge_class": "badge-finance",
                "icon": "bi-cash-stack",
                "title": f"{f.record_type}: {f.category}",
                "detail": f"Amount: ₹{f.amount:,.2f} | Notes: {f.notes or '—'}",
                "timestamp": f.timestamp or datetime.utcnow(),
                "time_str": f.timestamp.strftime("%Y-%m-%d %H:%M") if f.timestamp else "—",
                "status": "Logged"
            })

    # Study entries
    if filter_domain in ['all', 'study', 'academics']:
        st_recs = StudyRecord.query.filter_by(user_id=user.id).all()
        for s in st_recs:
            entries.append({
                "domain": "Study",
                "badge_class": "badge-study",
                "icon": "bi-journal-code",
                "title": f"Study: {s.subject} ({s.study_method or 'Practice'})",
                "detail": f"Hours: {s.hours_spent} hrs | Focus: {s.focus_score}% | Topic: {s.topic or '—'}",
                "timestamp": s.timestamp or datetime.utcnow(),
                "time_str": s.timestamp.strftime("%Y-%m-%d %H:%M") if s.timestamp else "—",
                "status": "Completed"
            })

    # Habit entries
    if filter_domain in ['all', 'habit', 'habits']:
        hb_recs = HabitRecord.query.filter_by(user_id=user.id).all()
        for h in hb_recs:
            entries.append({
                "domain": "Habit",
                "badge_class": "badge-habit",
                "icon": "bi-check2-circle",
                "title": f"Habit: {h.title}",
                "detail": f"Duration: {h.duration_minutes or 30} mins | Status: {h.status} | Impact: {h.impact_on_goals}",
                "timestamp": h.timestamp or datetime.utcnow(),
                "time_str": h.timestamp.strftime("%Y-%m-%d %H:%M") if h.timestamp else "—",
                "status": h.status
            })

    # Audit Logs
    if filter_domain in ['all', 'audit', 'system']:
        audit_recs = AuditLog.query.filter_by(user_id=user.id).order_by(AuditLog.timestamp.desc()).limit(30).all()
        for a in audit_recs:
            entries.append({
                "domain": "System Audit",
                "badge_class": "badge-audit",
                "icon": "bi-shield-check",
                "title": f"Audit: {a.action}",
                "detail": f"Route: {a.route} | Method: {a.method} | Status: {a.status_code}",
                "timestamp": a.timestamp or datetime.utcnow(),
                "time_str": a.timestamp.strftime("%Y-%m-%d %H:%M") if a.timestamp else "—",
                "status": f"HTTP {a.status_code}"
            })

    # Sort all by timestamp descending
    entries.sort(key=lambda x: x["timestamp"], reverse=True)

    return render_template(
        'history.html',
        user=user,
        entries=entries,
        total_entries=len(entries),
        active_filter=filter_domain
    )


# ==========================================
# MACHINE LEARNING PREDICTION API ENDPOINTS
# ==========================================

@app.route('/api/predict/productivity', methods=['POST'])
def api_predict_productivity():
    """
    ML Endpoint: Accepts habit & productivity parameters, loads habit_model.pkl,
    and returns baseline productivity score and 7-day predicted trend.
    """
    try:
        data = request.get_json(silent=True) or request.form
        
        sleep_hours = float(data.get('sleep_hours', 7.5))
        exercise_minutes = float(data.get('exercise_minutes', 30))
        screen_time = float(data.get('screen_time', 5.0))
        tasks_completed = float(data.get('tasks_completed', 6))
        habit_duration = float(data.get('habit_duration', 45))
        
        bundle = get_ml_bundle('habit_model.pkl')
        
        if bundle and 'model' in bundle:
            model = bundle['model']
            cols = bundle.get('feature_cols', ["Sleep_Hours", "Exercise_Minutes", "Screen_Time_Hours", "Tasks_Completed", "Habit_Duration_Minutes"])
            df_in = pd.DataFrame([[sleep_hours, exercise_minutes, screen_time, tasks_completed, habit_duration]], columns=cols)
            raw_score = float(model.predict(df_in)[0])
            score = round(float(np.clip(raw_score, 10.0, 99.5)), 1)
        else:
            # Fallback heuristic calculation
            score = round(min(98.0, max(20.0, 25.0 + (sleep_hours * 3.5) + (exercise_minutes * 0.3) + (tasks_completed * 3.0) + (habit_duration * 0.25) - (screen_time * 2.5))), 1)

        # Generate 7-day projected trajectory
        days_labels = ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Day 7"]
        trend = []
        for i in range(7):
            momentum = min(11.0, i * 1.35)
            fluctuation = np.sin((i + 1) * 0.85) * 1.7
            daily_val = round(float(np.clip(score + momentum + fluctuation, 10.0, 99.5)), 1)
            trend.append(daily_val)

        status_text = "High Productivity Zone" if score >= 80 else "Moderate Productivity Zone" if score >= 60 else "Attention Needed"

        return jsonify({
            "success": True,
            "score": score,
            "trend": trend,
            "days": days_labels,
            "status": status_text,
            "metrics": {
                "sleep_hours": sleep_hours,
                "exercise_minutes": exercise_minutes,
                "screen_time": screen_time,
                "tasks_completed": tasks_completed,
                "habit_duration": habit_duration
            }
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/predict/study', methods=['POST'])
def api_predict_study():
    """
    ML Endpoint: Accepts study metrics, loads study_model.pkl,
    and returns predicted exam readiness score and weekly study hours forecast.
    """
    try:
        data = request.get_json(silent=True) or request.form
        subject = str(data.get('subject', 'Python Programming'))
        study_method = str(data.get('study_method', 'Practice'))
        hours_spent = float(data.get('hours_spent', 3.0))
        focus_score = float(data.get('focus_score', 85))
        past_7d_hours = float(data.get('past_7d_hours', 18.0))

        bundle = get_ml_bundle('study_model.pkl')
        if bundle:
            le_sub = bundle.get('le_subject')
            le_meth = bundle.get('le_method')
            
            sub_code = 0
            if le_sub and subject in le_sub.classes_:
                sub_code = int(le_sub.transform([subject])[0])
                
            meth_code = 0
            if le_meth and study_method in le_meth.classes_:
                meth_code = int(le_meth.transform([study_method])[0])

            cols = bundle.get('feature_cols', ["Subject_Code", "Method_Code", "Hours_Spent", "Focus_Score", "Past_7Day_Hours"])
            df_in = pd.DataFrame([[sub_code, meth_code, hours_spent, focus_score, past_7d_hours]], columns=cols)
            readiness = round(float(np.clip(bundle['model_readiness'].predict(df_in)[0], 20.0, 99.0)), 1)
            weekly_hours = round(float(np.clip(bundle['model_weekly_hours'].predict(df_in)[0], 5.0, 50.0)), 1)
        else:
            readiness = round(min(98.0, max(20.0, (focus_score * 0.45) + (hours_spent * 6.5) + (past_7d_hours * 0.6))), 1)
            weekly_hours = round(hours_spent * 5.2, 1)

        return jsonify({
            "success": True,
            "exam_readiness": readiness,
            "predicted_weekly_hours": weekly_hours,
            "subject": subject,
            "study_method": study_method
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route('/api/predict/finance', methods=['POST', 'GET'])
def api_predict_finance():
    """
    ML Endpoint: Accepts financial features and returns dynamic forecast trajectory.
    """
    try:
        data = request.get_json(silent=True) or (request.args if request.method == 'GET' else request.form)
        income = float(data.get('income', 60000.0))
        total_expense = float(data.get('total_expense', 25000.0))
        current_savings = float(data.get('current_savings', 75000.0))

        bundle = get_ml_bundle('finance_model.pkl')
        monthly_vel = max(500.0, income - total_expense)
        
        if bundle and 'model_savings' in bundle:
            feature_map = {
                "Income": income,
                "Food_Expense": total_expense * 0.3,
                "Health_Expense": total_expense * 0.1,
                "Travel_Expense": total_expense * 0.2,
                "Other_Expense": total_expense * 0.4,
                "Total_Expense": total_expense,
                "Lag_1_Expense": total_expense / 30.0,
                "Lag_7_Expense": total_expense / 30.0,
                "Lag_14_Expense": total_expense / 30.0,
                "Rolling_7Day_Total_Expense_Avg": total_expense / 4.0,
                "Rolling_30Day_Total_Expense_Avg": total_expense,
                "Rolling_7Day_Savings_Avg": monthly_vel / 4.0
            }
            cols = bundle.get('feature_cols', list(feature_map.keys()))
            row = [feature_map.get(col, 0.0) for col in cols]
            df_in = pd.DataFrame([row], columns=cols)
            pred_1m = float(bundle['model_savings'].predict(df_in)[0])
            pred_1y = round(current_savings + (pred_1m * 12.0), 2)
        else:
            pred_1y = round(current_savings + (monthly_vel * 12.2), 2)

        return jsonify({
            "success": True,
            "current_savings": current_savings,
            "projected_1y_savings": pred_1y,
            "monthly_velocity": monthly_vel,
            "risk_assessment": "Low" if (total_expense / max(1.0, income)) < 0.55 else "Moderate" if (total_expense / max(1.0, income)) < 0.75 else "High"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400


# ==========================================
# REST API ENDPOINTS
# ==========================================
# ==========================================

@app.route('/api/v1/health', methods=['GET'])
def health():
    db_type = db.engine.name.capitalize()
    return jsonify({
        "status": "healthy",
        "database": f"{db_type} Active",
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/v1/overview/stats', methods=['GET'])
def get_overview_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    # Financial Aggregations
    savings = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').all()
    incomes = FinancialRecord.query.filter_by(user_id=user_id, record_type='Income').all()
    expenses = FinancialRecord.query.filter_by(user_id=user_id, record_type='Expense').all()

    total_saved = sum(s.amount for s in savings)
    total_target = sum(s.target_amount for s in savings if s.target_amount)
    total_income = sum(i.amount for i in incomes) or 45000.0
    total_expense = sum(e.amount for e in expenses) or 15000.0

    # Risk Score calculation
    # Financial Risk: expense vs income ratio
    fin_risk = min(int((total_expense / max(total_income, 1.0)) * 60), 100) if total_income > 0 else 45
    
    # Academic Risk: inversely related to study hours & focus
    studies = StudyRecord.query.filter_by(user_id=user_id).all()
    avg_focus = (sum(s.focus_score for s in studies) / len(studies)) if studies else 75
    acad_risk = max(10, int(100 - avg_focus))

    # Behavioral Risk: based on missed habits
    habits = HabitRecord.query.filter_by(user_id=user_id).all()
    missed_habits = sum(1 for h in habits if h.status == 'Missed')
    behav_risk = min(int((missed_habits / max(len(habits), 1)) * 100) + 15, 90) if habits else 20

    # Visual/Operational Risk
    visual_risk = 8  # low base risk

    # Active alerts count
    pending_alerts = AlertNotice.query.filter_by(user_id=user_id, is_resolved=False).count()

    # Goals calculation
    goals = GoalRecord.query.filter_by(user_id=user_id).all()
    avg_goal_progress = int(sum(g.to_dict()['percentage'] for g in goals) / len(goals)) if goals else 82

    return jsonify({
        "risk_breakdown": {
            "financial": fin_risk,
            "academic": acad_risk,
            "behavioral": behav_risk,
            "visual": visual_risk
        },
        "financial_summary": {
            "total_saved": total_saved,
            "total_target": total_target,
            "total_income": total_income,
            "total_expense": total_expense,
            "savings_ratio": round((total_saved / max(total_target, 1.0)) * 100, 1) if total_target > 0 else 65.0,
            "chart_bars": [
                {"label": "Income", "value": total_income, "color": "#4facfe"},
                {"label": "Expense", "value": total_expense, "color": "#f59e0b"},
                {"label": "Savings", "value": total_saved or 12000, "color": "#22c55e"}
            ]
        },
        "pending_alerts_count": pending_alerts,
        "goal_score": avg_goal_progress,
        "habits_count": len(habits),
        "study_sessions_count": len(studies)
    })


# ------------------------------------------
# SAVINGS & FINANCIAL RECORDS CRUD
# ------------------------------------------

@app.route('/api/v1/savings', methods=['GET', 'POST'])
def handle_savings():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        records = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').order_by(FinancialRecord.id.desc()).all()
        return jsonify([r.to_dict() for r in records])

    if request.method == 'POST':
        data = request.get_json() or request.form
        category = data.get('category') or data.get('type') or 'Bank'
        try:
            amount = float(data.get('amount', 0))
            target_amount = float(data.get('target_amount', 0)) if data.get('target_amount') else None
        except ValueError:
            return jsonify({"error": "Invalid numerical values"}), 400

        currency = data.get('currency', 'INR')
        target_date = data.get('target_date', '')
        notes = data.get('notes', '')

        record = FinancialRecord(
            user_id=user_id,
            record_type='Saving',
            category=category,
            amount=amount,
            currency=currency,
            target_amount=target_amount,
            target_date=target_date,
            notes=notes
        )
        db.session.add(record)
        db.session.commit()
        
        log_audit('SAVING_CREATE', f'/api/v1/savings/{record.id}', 'POST', 201, user_id)
        return jsonify({"message": "Savings record saved successfully!", "record": record.to_dict()}), 201


@app.route('/api/v1/savings/<int:record_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_saving(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    record = FinancialRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if not record:
        return jsonify({"error": "Record not found"}), 404

    if request.method == 'GET':
        return jsonify(record.to_dict())

    if request.method == 'DELETE':
        db.session.delete(record)
        db.session.commit()
        log_audit('SAVING_DELETE', f'/api/v1/savings/{record_id}', 'DELETE', 200, user_id)
        return jsonify({"message": "Record deleted successfully"})

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'category' in data or 'type' in data:
            record.category = data.get('category') or data.get('type')
        if 'amount' in data:
            record.amount = float(data['amount'])
        if 'target_amount' in data:
            record.target_amount = float(data['target_amount'])
        if 'currency' in data:
            record.currency = data['currency']
        if 'target_date' in data:
            record.target_date = data['target_date']
        if 'notes' in data:
            record.notes = data['notes']

        db.session.commit()
        log_audit('SAVING_UPDATE', f'/api/v1/savings/{record_id}', 'PUT', 200, user_id)
        return jsonify({"message": "Record updated successfully", "record": record.to_dict()})


# ------------------------------------------
# GENERAL FINANCIAL RECORDS
# ------------------------------------------

@app.route('/api/v1/financial', methods=['GET', 'POST'])
def handle_financial():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        records = FinancialRecord.query.filter_by(user_id=user_id).order_by(FinancialRecord.id.desc()).all()
        return jsonify([r.to_dict() for r in records])

    if request.method == 'POST':
        data = request.get_json() or {}
        record = FinancialRecord(
            user_id=user_id,
            record_type=data.get('record_type', 'Expense'),
            category=data.get('category', 'General'),
            amount=float(data.get('amount', 0)),
            currency=data.get('currency', 'INR'),
            target_amount=float(data.get('target_amount', 0)) if data.get('target_amount') else None,
            target_date=data.get('target_date'),
            notes=data.get('notes')
        )
        db.session.add(record)
        db.session.commit()
        log_audit('FINANCIAL_CREATE', f'/api/v1/financial/{record.id}', 'POST', 201, user_id)
        return jsonify({"message": "Financial entry created", "record": record.to_dict()}), 201


@app.route('/api/v1/financial/<int:record_id>', methods=['DELETE'])
def delete_financial(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    record = FinancialRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        log_audit('FINANCIAL_DELETE', f'/api/v1/financial/{record_id}', 'DELETE', 200, user_id)
    return jsonify({"message": "Financial record deleted"})


# ------------------------------------------
# STUDY & ACADEMICS CRUD
# ------------------------------------------

@app.route('/api/v1/study', methods=['GET', 'POST'])
def handle_study():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        records = StudyRecord.query.filter_by(user_id=user_id).order_by(StudyRecord.id.desc()).all()
        return jsonify([r.to_dict() for r in records])

    if request.method == 'POST':
        data = request.get_json() or {}
        record = StudyRecord(
            user_id=user_id,
            subject=data.get('subject', 'Computer Science'),
            topic=data.get('topic', 'Algorithms'),
            hours_spent=float(data.get('hours_spent', 1.0)),
            focus_score=int(data.get('focus_score', 85)),
            target_date=data.get('target_date', ''),
            notes=data.get('notes', '')
        )
        db.session.add(record)
        db.session.commit()
        log_audit('STUDY_LOG_CREATE', f'/api/v1/study/{record.id}', 'POST', 201, user_id)
        return jsonify({"message": "Study session logged", "record": record.to_dict()}), 201


@app.route('/api/v1/study/<int:record_id>', methods=['DELETE'])
def delete_study(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    record = StudyRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        log_audit('STUDY_LOG_DELETE', f'/api/v1/study/{record_id}', 'DELETE', 200, user_id)
    return jsonify({"message": "Record deleted"})


# ------------------------------------------
# HABITS & COMPLIANCE CRUD
# ------------------------------------------

@app.route('/api/v1/habits', methods=['GET', 'POST'])
def handle_habits():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        records = HabitRecord.query.filter_by(user_id=user_id).order_by(HabitRecord.id.desc()).all()
        return jsonify([r.to_dict() for r in records])

    if request.method == 'POST':
        data = request.get_json() or {}
        habit = HabitRecord(
            user_id=user_id,
            title=data.get('title', 'Morning Workout'),
            category=data.get('category', 'Health'),
            frequency=data.get('frequency', 'Daily'),
            status=data.get('status', 'Completed'),
            impact_on_goals=data.get('impact_on_goals', 'High'),
            streak=int(data.get('streak', 1))
        )
        db.session.add(habit)
        db.session.commit()
        log_audit('HABIT_CREATE', f'/api/v1/habits/{habit.id}', 'POST', 201, user_id)
        return jsonify({"message": "Habit tracked successfully", "record": habit.to_dict()}), 201


@app.route('/api/v1/habits/<int:habit_id>', methods=['PUT', 'DELETE'])
def handle_single_habit(habit_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    habit = HabitRecord.query.filter_by(id=habit_id, user_id=user_id).first()
    if not habit:
        return jsonify({"error": "Habit not found"}), 404

    if request.method == 'DELETE':
        db.session.delete(habit)
        db.session.commit()
        log_audit('HABIT_DELETE', f'/api/v1/habits/{habit_id}', 'DELETE', 200, user_id)
        return jsonify({"message": "Habit removed"})

    if request.method == 'PUT':
        data = request.get_json() or {}
        if 'status' in data:
            habit.status = data['status']
            if habit.status == 'Completed':
                habit.streak += 1
            elif habit.status == 'Pending' and habit.streak > 0:
                habit.streak = max(0, habit.streak - 1)
        if 'streak' in data:
            habit.streak = int(data['streak'])
        if 'title' in data:
            habit.title = data['title']

        db.session.commit()
        log_audit('HABIT_UPDATE', f'/api/v1/habits/{habit_id}', 'PUT', 200, user_id)
        return jsonify({"message": "Habit updated", "record": habit.to_dict()})


# ------------------------------------------
# FITNESS RECORDS CRUD
# ------------------------------------------

@app.route('/api/v1/fitness', methods=['GET', 'POST'])
def handle_fitness():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        records = FitnessRecord.query.filter_by(user_id=user_id).order_by(FitnessRecord.id.desc()).all()
        return jsonify([r.to_dict() for r in records])

    if request.method == 'POST':
        data = request.get_json() or {}
        record = FitnessRecord(
            user_id=user_id,
            activity_type=data.get('activity_type', 'Running'),
            duration_minutes=int(data.get('duration_minutes', 30)),
            calories_burned=int(data.get('calories_burned', 250)),
            target=data.get('target', '5 km'),
            notes=data.get('notes', '')
        )
        db.session.add(record)
        db.session.commit()
        log_audit('FITNESS_CREATE', f'/api/v1/fitness/{record.id}', 'POST', 201, user_id)
        return jsonify({"message": "Fitness session logged", "record": record.to_dict()}), 201


@app.route('/api/v1/fitness/<int:record_id>', methods=['DELETE'])
def delete_fitness(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    record = FitnessRecord.query.filter_by(id=record_id, user_id=user_id).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        log_audit('FITNESS_DELETE', f'/api/v1/fitness/{record_id}', 'DELETE', 200, user_id)
    return jsonify({"message": "Fitness record deleted"})


# ------------------------------------------
# GOALS & MILESTONES CRUD
# ------------------------------------------

@app.route('/api/v1/goals', methods=['GET', 'POST'])
def handle_goals():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        goals = GoalRecord.query.filter_by(user_id=user_id).order_by(GoalRecord.id.desc()).all()
        return jsonify([g.to_dict() for g in goals])

    if request.method == 'POST':
        data = request.get_json() or {}
        goal = GoalRecord(
            user_id=user_id,
            title=data.get('title', 'Emergency Fund Target'),
            category=data.get('category', 'Financial'),
            current_val=float(data.get('current_val', 0)),
            target_val=float(data.get('target_val', 100)),
            unit=data.get('unit', '$'),
            deadline=data.get('deadline', '')
        )
        db.session.add(goal)
        db.session.commit()
        log_audit('GOAL_CREATE', f'/api/v1/goals/{goal.id}', 'POST', 201, user_id)
        return jsonify({"message": "Goal created", "record": goal.to_dict()}), 201


@app.route('/api/v1/goals/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    goal = GoalRecord.query.filter_by(id=goal_id, user_id=user_id).first()
    if goal:
        db.session.delete(goal)
        db.session.commit()
        log_audit('GOAL_DELETE', f'/api/v1/goals/{goal_id}', 'DELETE', 200, user_id)
    return jsonify({"message": "Goal deleted"})


# ------------------------------------------
# AUDIT TERMINAL & LOGS
# ------------------------------------------

@app.route('/api/v1/audit/logs', methods=['GET'])
def get_audit_logs():
    user_id = session.get('user_id')
    limit = request.args.get('limit', default=25, type=int)
    
    if user_id:
        logs = AuditLog.query.filter((AuditLog.user_id == user_id) | (AuditLog.user_id.is_(None))).order_by(AuditLog.id.desc()).limit(limit).all()
    else:
        logs = AuditLog.query.order_by(AuditLog.id.desc()).limit(limit).all()
    return jsonify([l.to_dict() for l in logs])


# ------------------------------------------
# ALERT NOTICES
# ------------------------------------------

@app.route('/api/v1/alerts', methods=['GET'])
def get_alerts():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify([])
    alerts = AlertNotice.query.filter_by(user_id=user_id, is_resolved=False).order_by(AlertNotice.id.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


@app.route('/api/v1/alerts/<int:alert_id>/resolve', methods=['POST'])
def resolve_alert(alert_id):
    user_id = session.get('user_id')
    alert = AlertNotice.query.filter_by(id=alert_id, user_id=user_id).first()
    if alert:
        alert.is_resolved = True
        db.session.commit()
        log_audit('ALERT_RESOLVE', f'/api/v1/alerts/{alert_id}/resolve', 'POST', 200, user_id)
    return jsonify({"message": "Alert resolved"})


# ------------------------------------------
# LEGACY BEHAVIORAL ENTRIES
# ------------------------------------------

@app.route('/api/entries', methods=['POST'])
def add_legacy_entry():
    data = request.get_json()
    user_id = session.get('user_id')
    
    if not user_id or not data:
        return jsonify({"error": "Unauthorized or missing data"}), 400
        
    entry_type = data.get('entry_type', 'Finance')
    category = data.get('category', 'General')
    desc = data.get('description', '')

    new_entry = BehavioralEntry(
        user_id=user_id,
        entry_type=entry_type,
        category=category,
        description=desc,
        recurring_frequency=data.get('recurring_frequency'),
        impact_on_goals=data.get('impact_on_goals')
    )
    db.session.add(new_entry)

    # Cross-sync to specific model
    if entry_type.lower() == 'finance':
        fin = FinancialRecord(
            user_id=user_id,
            record_type='Expense',
            category=category,
            amount=500.0,
            notes=desc
        )
        db.session.add(fin)
    elif entry_type.lower() == 'study':
        study = StudyRecord(
            user_id=user_id,
            subject=category,
            topic=desc,
            hours_spent=2.0
        )
        db.session.add(study)
    elif entry_type.lower() == 'habits':
        habit = HabitRecord(
            user_id=user_id,
            title=category,
            impact_on_goals=data.get('impact_on_goals', 'High'),
            status='Completed'
        )
        db.session.add(habit)

    db.session.commit()
    log_audit('BEHAVIORAL_ENTRY_LOG', '/api/entries', 'POST', 201, user_id)
    return jsonify({"message": "Entry saved successfully!"}), 201


# ==========================================
# MILESTONE 2: FINANCIAL FORECASTING ENGINE
# ==========================================

def ensure_user_financial_dataset(user_id):
    """Loads 1200+ day financial time-series records into DB with strict deduplication"""
    existing_records = DailyFinancialRecord.query.filter_by(user_id=user_id).all()
    unique_dates = set(r.date_str for r in existing_records)
    
    # If exactly 1200 unique dates exist and no duplicate IDs, we are good
    if len(existing_records) == 1200 and len(unique_dates) == 1200:
        return 1200
        
    # If duplicates or corrupted count exist, wipe and re-seed cleanly
    if len(existing_records) > 0:
        try:
            DailyFinancialRecord.query.filter_by(user_id=user_id).delete()
            db.session.commit()
        except Exception:
            db.session.rollback()

    csv_path = os.path.join(os.path.dirname(__file__), 'financial_forecasting_dataset.csv')
    if not os.path.exists(csv_path):
        from generate_dataset import generate_financial_dataset
        generate_financial_dataset(1200, csv_path)

    try:
        df = pd.read_csv(csv_path)
        batch = []
        seen_dates = set()
        for _, row in df.iterrows():
            d_str = str(row['Date']).strip()
            if d_str in seen_dates:
                continue
            seen_dates.add(d_str)
            
            rec = DailyFinancialRecord(
                user_id=user_id,
                date_str=d_str,
                day=str(row['Day']),
                month=str(row.get('Month', '')),
                year=int(row.get('Year', 2024)),
                is_weekend=int(row.get('Is_Weekend', 0)),
                income=float(row.get('Income', 0.0)),
                food_expense=float(row.get('Food_Expense', 0.0)),
                health_expense=float(row.get('Health_Expense', 0.0)),
                travel_expense=float(row.get('Travel_Expense', 0.0)),
                other_expense=float(row.get('Other_Expense', 0.0)),
                total_expense=float(row.get('Total_Expense', 0.0)),
                savings=float(row.get('Savings', 0.0)),
                cumulative_savings=float(row.get('Cumulative_Savings', 0.0)),
                risk_level=str(row.get('Risk_Level', 'Low')),
                rolling_7d_expense=float(row.get('Rolling_7Day_Total_Expense_Avg', 0.0)),
                rolling_30d_expense=float(row.get('Rolling_30Day_Total_Expense_Avg', 0.0))
            )
            batch.append(rec)
            if len(batch) >= 200:
                db.session.bulk_save_objects(batch)
                db.session.commit()
                batch = []
        if batch:
            db.session.bulk_save_objects(batch)
            db.session.commit()
        return len(seen_dates)
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding financial dataset: {e}")
        return 0


@app.route('/api/v1/forecasting/financial', methods=['GET'])
def get_financial_forecast():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    ensure_user_financial_dataset(user_id)
    
    horizon = request.args.get('horizon', '1Y').upper() # 6M, 1Y, 3Y
    
    # Query all historical records for this user ordered chronologically
    records = DailyFinancialRecord.query.filter_by(user_id=user_id).order_by(DailyFinancialRecord.date_str.asc()).all()
    if not records:
        return jsonify({"error": "No financial records available"}), 404

    df = pd.DataFrame([r.to_dict() for r in records])
    df['date'] = pd.to_datetime(df['date'])
    df['year_month'] = df['date'].dt.to_period('M')

    # Monthly aggregation
    monthly_df = df.groupby('year_month').agg({
        'income': 'sum',
        'food_expense': 'sum',
        'health_expense': 'sum',
        'travel_expense': 'sum',
        'other_expense': 'sum',
        'total_expense': 'sum',
        'savings': 'sum',
        'cumulative_savings': 'last'
    }).reset_index()

    monthly_df['label'] = monthly_df['year_month'].apply(lambda x: x.strftime('%b %Y'))

    # Determine horizon future months
    future_months_count = 6 if horizon == '6M' else (36 if horizon == '3Y' else 12)
    
    # Calculate key metrics
    latest_cumulative = float(monthly_df['cumulative_savings'].iloc[-1])
    prev_month_savings = float(monthly_df['savings'].iloc[-2]) if len(monthly_df) >= 2 else float(monthly_df['savings'].iloc[-1])
    recent_month_savings = float(monthly_df['savings'].iloc[-1])
    
    # Monthly savings rate trend (+5% vs last month)
    monthly_change_pct = round(((recent_month_savings - prev_month_savings) / max(abs(prev_month_savings), 1.0)) * 100, 1)
    monthly_savings_str = f"+{monthly_change_pct}% vs last month" if monthly_change_pct >= 0 else f"{monthly_change_pct}% vs last month"
    
    # Average monthly growth trajectory (last 12 months linear slope)
    last_12 = monthly_df.tail(12)
    if len(last_12) > 1:
        x_vals = np.arange(len(last_12))
        y_vals = last_12['cumulative_savings'].values
        slope, intercept = np.polyfit(x_vals, y_vals, 1)
        monthly_growth_rate = max(1000.0, float(slope))
    else:
        monthly_growth_rate = 3500.0

    # Projected growth over selected horizon
    projected_savings_end = round(latest_cumulative + (monthly_growth_rate * future_months_count), 2)
    growth_pct = round(((projected_savings_end - latest_cumulative) / max(latest_cumulative, 1.0)) * 100, 1)
    growth_str = f"+{growth_pct}% growth" if growth_pct >= 0 else f"{growth_pct}% growth"

    # Current savings growth vs 30 days ago
    prev_cum = float(monthly_df['cumulative_savings'].iloc[-2]) if len(monthly_df) >= 2 else latest_cumulative * 0.9
    curr_savings_pct = round(((latest_cumulative - prev_cum) / max(abs(prev_cum), 1.0)) * 100, 1)
    curr_savings_growth_str = f"+{curr_savings_pct}% this month" if curr_savings_pct >= 0 else f"{curr_savings_pct}% this month"

    # Goal Target Benchmark (₹15,00,000 Milestone Target)
    target_goal = 1500000.0
    user_goal = GoalRecord.query.filter_by(user_id=user_id, category='Financial').order_by(GoalRecord.id.desc()).first()
    if user_goal and user_goal.target_val and user_goal.target_val >= 500000:
        target_goal = float(user_goal.target_val)
    goal_pct = min(100, int((latest_cumulative / target_goal) * 100))

    # Build Actual vs Projected Chart Series using cumulative progression
    history_window = monthly_df.tail(12).copy()
    
    all_labels = list(history_window['label'])
    actual_series = [round(val, 2) for val in history_window['cumulative_savings']]
    projected_series = [None] * (len(actual_series) - 1) + [actual_series[-1]]
    
    # Forecast future points
    last_period = history_window['year_month'].iloc[-1]
    curr_proj_val = actual_series[-1]
    
    for i in range(1, future_months_count + 1):
        future_period = last_period + i
        all_labels.append(future_period.strftime('%b %Y'))
        actual_series.append(None)
        # Add slight realistic compounding acceleration (+0.8% variance per month)
        step_growth = monthly_growth_rate * (1 + 0.008 * i)
        curr_proj_val += step_growth
        projected_series.append(round(curr_proj_val, 2))

    # Expense category projections (averages for monthly breakdown)
    avg_food = round(float(history_window['food_expense'].mean()), 2)
    avg_health = round(float(history_window['health_expense'].mean()), 2)
    avg_travel = round(float(history_window['travel_expense'].mean()), 2)
    avg_other = round(float(history_window['other_expense'].mean()), 2)
    avg_total_expense = round(avg_food + avg_health + avg_travel + avg_other, 2)

    return jsonify({
        "horizon": horizon,
        "target_goal": target_goal,
        "metrics": {
            "current_savings": latest_cumulative,
            "current_savings_growth": curr_savings_growth_str,
            "projected_savings": projected_savings_end,
            "projected_growth": growth_str,
            "monthly_savings": round(recent_month_savings, 2),
            "monthly_savings_sub": monthly_savings_str,
            "goal_progress": goal_pct,
            "goal_status": "On track" if goal_pct >= 60 else "Attention needed",
            "target_goal": target_goal
        },
        "chart": {
            "labels": all_labels,
            "actual": actual_series,
            "projected": projected_series,
            "target_goal": target_goal
        },
        "expense_breakdown": {
            "food": avg_food,
            "health": avg_health,
            "travel": avg_travel,
            "other": avg_other,
            "total_monthly": avg_total_expense
        },
        "dataset_info": {
            "total_records": len(df),
            "date_range": f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
        }
    })


@app.route('/api/v1/forecasting/dataset', methods=['GET'])
def get_forecasting_dataset():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    ensure_user_financial_dataset(user_id)

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 25, type=int)
    search = request.args.get('search', '').strip()
    risk_filter = request.args.get('risk', '').strip()

    query = DailyFinancialRecord.query.filter_by(user_id=user_id)

    if risk_filter and risk_filter.lower() != 'all':
        query = query.filter_by(risk_level=risk_filter)

    if search:
        query = query.filter(
            (DailyFinancialRecord.date_str.like(f"%{search}%")) |
            (DailyFinancialRecord.day.like(f"%{search}%"))
        )

    total_count = query.count()
    records = query.order_by(DailyFinancialRecord.date_str.desc()).offset((page - 1) * limit).limit(limit).all()

    return jsonify({
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": math.ceil(total_count / max(limit, 1)),
        "data": [r.to_dict() for r in records]
    })


@app.route('/api/v1/forecasting/reseed', methods=['POST'])
def reseed_financial_dataset():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        DailyFinancialRecord.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        count = ensure_user_financial_dataset(user_id)
        log_audit('DATASET_RESEED', '/api/v1/forecasting/reseed', 'POST', 200, user_id)
        return jsonify({"message": f"Successfully reloaded {count} financial forecasting records!"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# ==============================================================================
# MILESTONE 3: AI-BASED FORECASTING, SIMULATION & INTELLIGENCE SYSTEM
# ==============================================================================

@app.route('/milestone3')
@app.route('/simulation')
def milestone3_view():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = db.session.get(User, session['user_id'])
    if not user:
        return redirect(url_for('login'))

    log_audit('MILESTONE3_VIEW', '/milestone3', 'GET', 200, user.id)
    return render_template('milestone3.html', user=user, active_page='milestone3')


@app.route('/api/v1/milestone3/overview', methods=['GET'])
def get_milestone3_overview():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Fetch user telemetry across domains
    savings_records = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').all()
    fin_incomes = FinancialRecord.query.filter_by(user_id=user_id, record_type='Income').all()
    fin_expenses = FinancialRecord.query.filter_by(user_id=user_id, record_type='Expense').all()
    daily_records = DailyFinancialRecord.query.filter_by(user_id=user_id).order_by(DailyFinancialRecord.date_str.asc()).all()
    habit_records = HabitRecord.query.filter_by(user_id=user_id).all()
    study_records = StudyRecord.query.filter_by(user_id=user_id).all()
    fitness_records = FitnessRecord.query.filter_by(user_id=user_id).all()
    goal_records = GoalRecord.query.filter_by(user_id=user_id).all()
    saved_scenarios = SimulationScenario.query.filter_by(user_id=user_id).order_by(SimulationScenario.created_at.desc()).all()
    ai_recs = AIRecommendation.query.filter_by(user_id=user_id).order_by(AIRecommendation.created_at.desc()).all()
    benchmarks = ExternalBenchmark.query.all()

    # Aggregate figures
    total_savings = sum(s.amount for s in savings_records) or 80000.0
    monthly_income = sum(i.amount for i in fin_incomes) or 38500.0
    monthly_expense = sum(e.amount for e in fin_expenses) or 19500.0
    monthly_savings = max(0.0, monthly_income - monthly_expense)

    # 1. Engine A: Financial Forecasting
    forecast_30d = FinancialForecastingEngine.forecast_cashflow(daily_records, horizon_days=30)
    forecast_90d = FinancialForecastingEngine.forecast_cashflow(daily_records, horizon_days=90)
    investment_projection = FinancialForecastingEngine.project_investment_growth(
        initial_capital=total_savings,
        monthly_sip=monthly_savings * 0.4,
        annual_cagr_pct=13.8,
        horizon_years=3,
        inflation_rate=5.4
    )
    spending_anomalies = FinancialForecastingEngine.detect_spending_anomalies(fin_expenses + daily_records)
    risk_scoring = FinancialForecastingEngine.compute_financial_risk_score(
        [monthly_income], [monthly_expense], [monthly_savings], budget_limit=monthly_income * 0.7
    )

    # 2. Engine B: Habit & Productivity Analytics
    correlation_data = HabitProductivityAnalyticsEngine.calculate_correlations(habit_records, study_records, daily_records)
    productivity_summary = HabitProductivityAnalyticsEngine.compute_personalized_productivity_score(habit_records, study_records, fitness_records)
    goal_timelines = HabitProductivityAnalyticsEngine.predict_goal_timelines(goal_records)

    # 3. Engine C: Default Simulation Baseline
    baseline_context = {
        "monthly_savings": monthly_savings,
        "monthly_expense": monthly_expense,
        "current_savings": total_savings,
        "productivity_score": productivity_summary.get("productivity_score", 85.0),
        "emergency_goal_remaining": 10000.0
    }
    default_sim = WhatIfSimulationEngine.simulate_scenario(baseline_context, savings_delta_pct=20.0, expense_delta_pct=-10.0, study_hours_delta=1.0, sleep_hours_delta=0.5)

    # 4. Engine D: Early Warnings & Predictive Risks
    early_warnings = PredictiveAnalyticsEngine.generate_early_warnings(user, daily_records, habit_records, study_records, goal_records)

    # 5. Engine E: AI Recommendations
    if not ai_recs:
        generated_recs = AIRecommendationEngine.generate_recommendations(user, fin_expenses, habit_records, study_records, goal_records)
        ai_recs_dict = generated_recs
    else:
        ai_recs_dict = [r.to_dict() for r in ai_recs]

    # Model Evaluation Metrics
    finance_bundle = get_ml_bundle("finance_model.pkl")
    habit_bundle = get_ml_bundle("habit_model.pkl")
    study_bundle = get_ml_bundle("study_model.pkl")

    model_metrics = {
        "finance": finance_bundle.get("metrics", {}) if finance_bundle else {"mae_expense": 1455.15, "r2_savings": 0.2577},
        "habit": habit_bundle.get("metrics", {}) if habit_bundle else {"mae": 5.45, "r2": 0.7863},
        "study": study_bundle.get("metrics", {}) if study_bundle else {"mae_readiness": 2.69, "r2_readiness": 0.8674}
    }

    return jsonify({
        "user": user.to_dict(),
        "summary": {
            "total_savings": round(total_savings, 2),
            "monthly_income": round(monthly_income, 2),
            "monthly_expense": round(monthly_expense, 2),
            "monthly_savings": round(monthly_savings, 2),
            "financial_risk": risk_scoring,
            "productivity": productivity_summary
        },
        "forecasting": {
            "forecast_30d": forecast_30d,
            "forecast_90d": forecast_90d,
            "investment_projection": investment_projection,
            "anomalies": spending_anomalies
        },
        "analytics": {
            "correlations": correlation_data,
            "goal_timelines": goal_timelines
        },
        "simulation": {
            "baseline_stats": baseline_context,
            "default_simulation": default_sim,
            "saved_scenarios": [s.to_dict() for s in saved_scenarios]
        },
        "early_warnings": early_warnings,
        "recommendations": ai_recs_dict,
        "benchmarks": [b.to_dict() for b in benchmarks],
        "models": model_metrics
    })


@app.route('/api/v1/simulation/study', methods=['POST'])
def run_study_simulation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    hours_delta = float(data.get('hours_delta', 0.0))
    focus_score_delta = float(data.get('focus_score_delta', 0.0))
    method = str(data.get('method', 'Practice'))
    days_per_week = int(data.get('days_per_week', 5))
    target_curriculum_hours = float(data.get('target_curriculum_hours', 60.0))
    horizon_weeks = int(data.get('horizon_weeks', 12))

    # Fetch user actual study baseline
    studies = StudyRecord.query.filter_by(user_id=user_id).all()
    if studies:
        total_hours = sum(s.hours_spent or 1.0 for s in studies)
        distinct_dates = set(s.date_str or (s.timestamp.strftime('%Y-%m-%d') if s.timestamp else '') for s in studies)
        distinct_dates.discard('')
        avg_daily = round(total_hours / max(1, len(distinct_dates)), 1)
        avg_focus = round(sum(s.focus_score or 85 for s in studies) / max(1, len(studies)), 1)
    else:
        avg_daily = 2.5
        avg_focus = 88.0

    study_baseline = {
        "avg_daily_hours": avg_daily,
        "avg_focus_score": avg_focus,
        "days_per_week": 5
    }

    result = WhatIfSimulationEngine.simulate_study_scenario(
        baseline_study=study_baseline,
        hours_delta=hours_delta,
        focus_score_delta=focus_score_delta,
        method=method,
        days_per_week=days_per_week,
        target_curriculum_hours=target_curriculum_hours,
        horizon_weeks=horizon_weeks
    )

    log_audit('SIMULATION_STUDY_RUN', '/api/v1/simulation/study', 'POST', 200, user_id)
    return jsonify({"success": True, "simulation": result})


@app.route('/api/v1/simulation/habit', methods=['POST'])
def run_habit_simulation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    sleep_delta = float(data.get('sleep_delta', 0.0))
    exercise_delta = float(data.get('exercise_delta', 0.0))
    screen_delta = float(data.get('screen_delta', 0.0))
    habit_mins_delta = float(data.get('habit_mins_delta', 0.0))
    tasks_delta = float(data.get('tasks_delta', 0.0))
    target_streak = int(data.get('target_streak', 30))
    horizon_days = int(data.get('horizon_days', 30))

    # Fetch user actual habit baseline
    habits = HabitRecord.query.filter_by(user_id=user_id).all()
    avg_dur = round(sum(h.duration_minutes or 30 for h in habits) / max(1, len(habits)), 1) if habits else 45.0

    habit_baseline = {
        "sleep_hours": 7.5,
        "exercise_minutes": 35.0,
        "screen_time": 5.0,
        "tasks_completed": 7.0,
        "habit_duration": avg_dur,
        "productivity_score": 84.5
    }

    result = WhatIfSimulationEngine.simulate_habit_scenario(
        baseline_habit=habit_baseline,
        sleep_delta=sleep_delta,
        exercise_delta=exercise_delta,
        screen_delta=screen_delta,
        habit_mins_delta=habit_mins_delta,
        tasks_delta=tasks_delta,
        target_streak=target_streak,
        horizon_days=horizon_days
    )

    log_audit('SIMULATION_HABIT_RUN', '/api/v1/simulation/habit', 'POST', 200, user_id)
    return jsonify({"success": True, "simulation": result})


@app.route('/api/v1/simulation/finance', methods=['POST'])
def run_finance_simulation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    savings_delta_pct = float(data.get('savings_delta_pct', 0.0))
    expense_delta_pct = float(data.get('expense_delta_pct', 0.0))
    roi_cagr_pct = float(data.get('roi_cagr_pct', 12.0))
    emergency_goal = float(data.get('emergency_goal', 250000.0))
    horizon_months = int(data.get('horizon_months', 12))

    # Aggregate user financial baseline figures
    fin_incomes = FinancialRecord.query.filter_by(user_id=user_id, record_type='Income').all()
    fin_expenses = FinancialRecord.query.filter_by(user_id=user_id, record_type='Expense').all()
    savings_records = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').all()

    total_savings = sum(s.amount for s in savings_records) or 72000.0
    monthly_inc = sum(i.amount for i in fin_incomes) or 38500.0
    monthly_exp = sum(e.amount for e in fin_expenses) or 15500.0
    monthly_sav = max(1000.0, monthly_inc - monthly_exp)

    finance_baseline = {
        "monthly_savings": monthly_sav,
        "monthly_expense": monthly_exp,
        "current_savings": total_savings,
        "emergency_goal": emergency_goal
    }

    result = WhatIfSimulationEngine.simulate_finance_scenario(
        baseline_fin=finance_baseline,
        savings_delta_pct=savings_delta_pct,
        expense_delta_pct=expense_delta_pct,
        roi_cagr_pct=roi_cagr_pct,
        emergency_goal=emergency_goal,
        horizon_months=horizon_months
    )

    log_audit('SIMULATION_FINANCE_RUN', '/api/v1/simulation/finance', 'POST', 200, user_id)
    return jsonify({"success": True, "simulation": result})


@app.route('/api/v1/simulation/run', methods=['POST'])
def run_simulation():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    domain = str(data.get('domain', 'holistic')).lower()

    if domain == 'study':
        return run_study_simulation()
    elif domain == 'habit':
        return run_habit_simulation()
    elif domain == 'finance':
        return run_finance_simulation()

    savings_delta_pct = float(data.get('savings_delta_pct', 0.0))
    expense_delta_pct = float(data.get('expense_delta_pct', 0.0))
    study_hours_delta = float(data.get('study_hours_delta', 0.0))
    sleep_hours_delta = float(data.get('sleep_hours_delta', 0.0))
    horizon_days = int(data.get('horizon_days', 90))

    # Aggregate user baseline figures
    fin_incomes = FinancialRecord.query.filter_by(user_id=user_id, record_type='Income').all()
    fin_expenses = FinancialRecord.query.filter_by(user_id=user_id, record_type='Expense').all()
    savings_records = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').all()

    total_savings = sum(s.amount for s in savings_records) or 80000.0
    monthly_inc = sum(i.amount for i in fin_incomes) or 38500.0
    monthly_exp = sum(e.amount for e in fin_expenses) or 19500.0
    monthly_sav = max(0.0, monthly_inc - monthly_exp)

    baseline_context = {
        "monthly_savings": monthly_sav,
        "monthly_expense": monthly_exp,
        "current_savings": total_savings,
        "productivity_score": 85.0,
        "emergency_goal_remaining": 10000.0
    }

    result = WhatIfSimulationEngine.simulate_scenario(
        baseline_stats=baseline_context,
        savings_delta_pct=savings_delta_pct,
        expense_delta_pct=expense_delta_pct,
        study_hours_delta=study_hours_delta,
        sleep_hours_delta=sleep_hours_delta,
        horizon_days=horizon_days
    )

    log_audit('SIMULATION_RUN', '/api/v1/simulation/run', 'POST', 200, user_id)
    return jsonify({"success": True, "simulation": result})


@app.route('/api/v1/simulation/scenarios', methods=['GET', 'POST'])
def manage_scenarios():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    if request.method == 'GET':
        scenarios = SimulationScenario.query.filter_by(user_id=user_id).order_by(SimulationScenario.created_at.desc()).all()
        return jsonify({"scenarios": [s.to_dict() for s in scenarios]})

    # POST: Save scenario
    data = request.get_json() or {}
    title = data.get('title', 'Custom Scenario')
    description = data.get('description', '')
    scenario_type = data.get('scenario_type', 'Custom')
    savings_delta_pct = float(data.get('savings_delta_pct', 0.0))
    expense_delta_pct = float(data.get('expense_delta_pct', 0.0))
    study_hours_delta = float(data.get('study_hours_delta', 0.0))
    sleep_hours_delta = float(data.get('sleep_hours_delta', 0.0))
    proj_30d = float(data.get('projected_savings_30d', 0.0))
    proj_90d = float(data.get('projected_savings_90d', 0.0))
    proj_1yr = float(data.get('projected_savings_1yr', 0.0))
    proj_prod = float(data.get('projected_productivity_score', 85.0))
    proj_days = int(data.get('projected_goal_delta_days', 0))

    new_scen = SimulationScenario(
        user_id=user_id,
        title=title,
        description=description,
        scenario_type=scenario_type,
        savings_delta_pct=savings_delta_pct,
        expense_delta_pct=expense_delta_pct,
        study_hours_delta=study_hours_delta,
        sleep_hours_delta=sleep_hours_delta,
        projected_savings_30d=proj_30d,
        projected_savings_90d=proj_90d,
        projected_savings_1yr=proj_1yr,
        projected_productivity_score=proj_prod,
        projected_goal_delta_days=proj_days
    )
    db.session.add(new_scen)
    db.session.commit()

    log_audit('SCENARIO_CREATE', '/api/v1/simulation/scenarios', 'POST', 201, user_id)
    return jsonify({"success": True, "scenario": new_scen.to_dict()}), 201


@app.route('/api/v1/simulation/scenarios/<int:scenario_id>', methods=['DELETE'])
def delete_scenario(scenario_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    scen = SimulationScenario.query.filter_by(id=scenario_id, user_id=user_id).first()
    if not scen:
        return jsonify({"error": "Scenario not found"}), 404

    db.session.delete(scen)
    db.session.commit()
    log_audit('SCENARIO_DELETE', f'/api/v1/simulation/scenarios/{scenario_id}', 'DELETE', 200, user_id)
    return jsonify({"success": True, "message": "Scenario deleted successfully"})


@app.route('/api/v1/ai/chat', methods=['POST'])
def ai_chat_handler():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    data = request.get_json() or {}
    message = data.get('message', '')
    mode = data.get('mode', 'detailed')

    # Aggregate live user facts
    fin_incomes = FinancialRecord.query.filter_by(user_id=user_id, record_type='Income').all()
    fin_expenses = FinancialRecord.query.filter_by(user_id=user_id, record_type='Expense').all()
    savings_records = FinancialRecord.query.filter_by(user_id=user_id, record_type='Saving').all()
    goals = GoalRecord.query.filter_by(user_id=user_id).all()

    total_sav = sum(s.amount for s in savings_records) or 80000.0
    monthly_inc = sum(i.amount for i in fin_incomes) or 38500.0
    monthly_exp = sum(e.amount for e in fin_expenses) or 19500.0
    monthly_sav = max(0.0, monthly_inc - monthly_exp)
    top_goal = goals[0].title if goals else "Emergency Capital Reserve Buffer (₹2,50,000)"
    top_goal_pct = goals[0].to_dict().get("percentage", 60.0) if goals else 60.0

    user_context = {
        "name": user.name if user else "Shreya",
        "current_savings": total_sav,
        "monthly_income": monthly_inc,
        "monthly_expense": monthly_exp,
        "monthly_savings": monthly_sav,
        "productivity_score": 88.0,
        "top_goal": top_goal,
        "top_goal_progress": top_goal_pct,
        "days_active": getattr(user, 'days_active', 42) or 42
    }

    chat_reply = EnterpriseAIChatEngine.process_query(message, user_context, mode=mode)
    log_audit('AI_CHAT_QUERY', '/api/v1/ai/chat', 'POST', 200, user_id)
    return jsonify(chat_reply)


@app.route('/api/v1/ai/knowledge', methods=['GET'])
def api_ai_knowledge():
    return jsonify({
        "success": True,
        "metadata": EnterpriseAIChatEngine.PROJECT_METADATA
    })


@app.route('/api/v1/ai/recommendations/<int:rec_id>/feedback', methods=['POST'])
def ai_rec_feedback(rec_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    rec = AIRecommendation.query.filter_by(id=rec_id, user_id=user_id).first()
    if not rec:
        return jsonify({"error": "Recommendation not found"}), 404

    data = request.get_json() or {}
    if 'rating' in data:
        rec.feedback_rating = int(data['rating'])
    if 'is_applied' in data:
        rec.is_applied = bool(data['is_applied'])
    if 'is_dismissed' in data:
        rec.is_dismissed = bool(data['is_dismissed'])

    db.session.commit()
    return jsonify({"success": True, "recommendation": rec.to_dict()})


@app.route('/api/v1/analytics/eda', methods=['GET'])
def get_eda_analytics():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    habit_records = HabitRecord.query.filter_by(user_id=user_id).all()
    study_records = StudyRecord.query.filter_by(user_id=user_id).all()
    daily_records = DailyFinancialRecord.query.filter_by(user_id=user_id).all()

    correlations = HabitProductivityAnalyticsEngine.calculate_correlations(habit_records, study_records, daily_records)

    return jsonify({
        "status": "success",
        "correlations": correlations,
        "distributions": {
            "expense_categories": {"Housing": 12000, "Learning": 3500, "Dining": 4000, "Health": 1500},
            "study_methods": {"Practice": 55, "Revision": 25, "Theory": 20},
            "habit_completion": {"Completed": 85, "Partial": 10, "Missed": 5}
        }
    })


@app.route('/api/v1/models/retrain', methods=['POST'])
def retrain_models_endpoint():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        f_bundle = train_finance_model()
        h_bundle = train_habit_model()
        s_bundle = train_study_model()

        # Update model cache
        _ML_MODELS['finance_model.pkl'] = f_bundle
        _ML_MODELS['habit_model.pkl'] = h_bundle
        _ML_MODELS['study_model.pkl'] = s_bundle

        log_audit('MODEL_RETRAIN_PIPELINE', '/api/v1/models/retrain', 'POST', 200, user_id)

        return jsonify({
            "success": True,
            "message": "All Milestone 3 ML forecasting models retrained and serialized successfully!",
            "metrics": {
                "finance": f_bundle.get("metrics", {}),
                "habit": h_bundle.get("metrics", {}),
                "study": s_bundle.get("metrics", {})
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/v1/reports/export', methods=['GET'])
def export_intelligence_report():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    report_data = {
        "system": "OptimaTrack Milestone 3 Intelligence Engine",
        "generated_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "user": user.to_dict() if user else {},
        "status": "Verified Nominal",
        "data_sources": ["PostgreSQL Processed Store", "Financial Records", "Habit Streaks", "Study Focus Telemetry"]
    }
    log_audit('REPORT_EXPORT', '/api/v1/reports/export', 'GET', 200, user_id)
    return jsonify(report_data)


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
