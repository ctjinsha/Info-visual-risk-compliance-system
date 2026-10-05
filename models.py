from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    
    # Login details
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile information
    profile_picture = db.Column(db.String(255), default="default.png")
    name = db.Column(db.String(100), default="Shreya")
    occupation = db.Column(db.String(100), default="Risk & Data Analyst")
    age = db.Column(db.Integer, default=26)
    goal_score = db.Column(db.Integer, default=85)
    days_active = db.Column(db.Integer, default=42)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    entries = db.relationship('BehavioralEntry', backref='user', lazy=True, cascade="all, delete-orphan")
    financial_records = db.relationship('FinancialRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    daily_financial_records = db.relationship('DailyFinancialRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    study_records = db.relationship('StudyRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    habit_records = db.relationship('HabitRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    fitness_records = db.relationship('FitnessRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    goal_records = db.relationship('GoalRecord', backref='user', lazy=True, cascade="all, delete-orphan")
    audit_logs = db.relationship('AuditLog', backref='user', lazy=True, cascade="all, delete-orphan")
    alert_notices = db.relationship('AlertNotice', backref='user', lazy=True, cascade="all, delete-orphan")
    simulation_scenarios = db.relationship('SimulationScenario', backref='user', lazy=True, cascade="all, delete-orphan")
    ai_recommendations = db.relationship('AIRecommendation', backref='user', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "occupation": self.occupation,
            "age": self.age,
            "goal_score": self.goal_score,
            "days_active": self.days_active,
            "profile_picture": self.profile_picture,
            "created_at": self.created_at.strftime("%Y-%m-%d") if self.created_at else None
        }


class FinancialRecord(db.Model):
    __tablename__ = 'financial_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # 'Saving', 'Income', 'Expense'
    record_type = db.Column(db.String(50), nullable=False, default='Saving')
    category = db.Column(db.String(100), nullable=False, default='Bank')
    amount = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(10), default='INR')
    target_amount = db.Column(db.Float, nullable=True, default=0.0)
    target_date = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "record_type": self.record_type,
            "category": self.category,
            "amount": self.amount,
            "currency": self.currency or "INR",
            "target_amount": self.target_amount or 0.0,
            "target_date": self.target_date or "—",
            "notes": self.notes or "",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class StudyRecord(db.Model):
    __tablename__ = 'study_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    subject = db.Column(db.String(100), nullable=False)
    topic = db.Column(db.String(150), nullable=True)
    study_method = db.Column(db.String(50), default='Practice') # Practice, Revision, Theory, Problem Solving
    hours_spent = db.Column(db.Float, default=1.0)
    focus_score = db.Column(db.Integer, default=80) # 1 to 100
    date_str = db.Column(db.String(50), nullable=True)
    target_date = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        date_display = self.date_str or (self.timestamp.strftime("%Y-%m-%d") if self.timestamp else "—")
        return {
            "id": self.id,
            "subject": self.subject,
            "topic": self.topic or "",
            "study_method": self.study_method or "Practice",
            "hours_spent": self.hours_spent or 1.0,
            "focus_score": self.focus_score or 80,
            "date": date_display,
            "target_date": self.target_date or "—",
            "notes": self.notes or "",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class HabitRecord(db.Model):
    __tablename__ = 'habit_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), default='Productivity')
    duration_minutes = db.Column(db.Integer, default=30)
    frequency = db.Column(db.String(50), default='Daily') # Daily, Weekly, Monthly
    status = db.Column(db.String(50), default='Completed') # Completed, Partial, Missed
    impact_on_goals = db.Column(db.String(50), default='High') # High, Medium, Low
    streak = db.Column(db.Integer, default=1)
    date_str = db.Column(db.String(50), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        date_display = self.date_str or (self.timestamp.strftime("%Y-%m-%d") if self.timestamp else "—")
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category or "Productivity",
            "duration_minutes": self.duration_minutes or 30,
            "frequency": self.frequency or "Daily",
            "status": self.status or "Completed",
            "impact_on_goals": self.impact_on_goals or "High",
            "streak": self.streak or 1,
            "date": date_display,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class FitnessRecord(db.Model):
    __tablename__ = 'fitness_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    activity_type = db.Column(db.String(100), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    calories_burned = db.Column(db.Integer, default=200)
    target = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "activity_type": self.activity_type,
            "duration_minutes": self.duration_minutes,
            "calories_burned": self.calories_burned,
            "target": self.target or "",
            "notes": self.notes or "",
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class GoalRecord(db.Model):
    __tablename__ = 'goal_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), default='Financial') # Financial, Academic, Habits, Fitness
    current_val = db.Column(db.Float, default=0.0)
    target_val = db.Column(db.Float, default=100.0)
    unit = db.Column(db.String(20), default='%')
    deadline = db.Column(db.String(50), nullable=True)
    status = db.Column(db.String(50), default='In Progress')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        pct = round((self.current_val / self.target_val * 100), 1) if self.target_val > 0 else 0
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "current_val": self.current_val,
            "target_val": self.target_val,
            "unit": self.unit,
            "percentage": min(pct, 100.0),
            "deadline": self.deadline or "—",
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    action = db.Column(db.String(100), nullable=False)
    route = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(20), default='GET')
    status_code = db.Column(db.Integer, default=200)
    ip_address = db.Column(db.String(50), default='127.0.0.1')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        iso_str = self.timestamp.isoformat() + "Z" if self.timestamp else None
        time_str = self.timestamp.strftime("%I:%M:%S %p").lower() if self.timestamp else ""
        return {
            "id": self.id,
            "time": time_str,
            "iso_timestamp": iso_str,
            "action": self.action,
            "route": self.route,
            "method": self.method,
            "status": self.status_code,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class AlertNotice(db.Model):
    __tablename__ = 'alert_notices'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(150), nullable=False)
    severity = db.Column(db.String(50), default='Warning') # Critical, Warning, Info, Normal
    domain = db.Column(db.String(50), default='Financial') # Financial, Academic, Behavioral, Visual
    message = db.Column(db.String(255), nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity,
            "domain": self.domain,
            "message": self.message,
            "is_resolved": self.is_resolved,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class BehavioralEntry(db.Model):
    __tablename__ = 'behavioral_entries'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    entry_type = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    recurring_frequency = db.Column(db.String(50))
    impact_on_goals = db.Column(db.String(50))
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "entry_type": self.entry_type,
            "category": self.category,
            "description": self.description,
            "recurring_frequency": self.recurring_frequency,
            "impact_on_goals": self.impact_on_goals,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S") if self.timestamp else None
        }


class DailyFinancialRecord(db.Model):
    __tablename__ = 'daily_financial_records'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'date_str', name='uq_user_daily_date'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    date_str = db.Column(db.String(20), nullable=False)  # YYYY-MM-DD
    day = db.Column(db.String(20), nullable=False)       # Monday, Tuesday...
    month = db.Column(db.String(20), nullable=True)     # January, February...
    year = db.Column(db.Integer, nullable=True)
    is_weekend = db.Column(db.Integer, default=0)
    
    income = db.Column(db.Float, default=0.0)
    food_expense = db.Column(db.Float, default=0.0)
    health_expense = db.Column(db.Float, default=0.0)
    travel_expense = db.Column(db.Float, default=0.0)
    other_expense = db.Column(db.Float, default=0.0)
    total_expense = db.Column(db.Float, default=0.0)
    savings = db.Column(db.Float, default=0.0)
    cumulative_savings = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default="Low")
    
    # Pre-computed indicators
    rolling_7d_expense = db.Column(db.Float, default=0.0)
    rolling_30d_expense = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Guarantee clean 4-digit ISO date string format (YYYY-MM-DD)
        raw_date = str(self.date_str or "").strip()
        if len(raw_date) == 10 and raw_date[4] == '-' and raw_date[7] == '-':
            formatted_date = raw_date
        else:
            try:
                formatted_date = datetime.strptime(raw_date, "%Y-%m-%d").strftime("%Y-%m-%d")
            except Exception:
                formatted_date = raw_date

        return {
            "id": self.id,
            "date": formatted_date,
            "day": self.day,
            "month": self.month,
            "year": self.year or (int(formatted_date[:4]) if len(formatted_date) >= 4 and formatted_date[:4].isdigit() else 2026),
            "is_weekend": bool(self.is_weekend),
            "income": round(self.income or 0.0, 2),
            "food_expense": round(self.food_expense or 0.0, 2),
            "health_expense": round(self.health_expense or 0.0, 2),
            "travel_expense": round(self.travel_expense or 0.0, 2),
            "other_expense": round(self.other_expense or 0.0, 2),
            "total_expense": round(self.total_expense or 0.0, 2),
            "savings": round(self.savings or 0.0, 2),
            "cumulative_savings": round(self.cumulative_savings or 0.0, 2),
            "risk_level": self.risk_level or "Low",
            "rolling_7d_expense": round(self.rolling_7d_expense or 0.0, 2),
            "rolling_30d_expense": round(self.rolling_30d_expense or 0.0, 2)
        }


class SimulationScenario(db.Model):
    __tablename__ = 'simulation_scenarios'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    scenario_type = db.Column(db.String(50), default='Custom') # Baseline, Optimistic, Conservative, Aggressive, Custom
    
    # What-If variable levers
    savings_delta_pct = db.Column(db.Float, default=0.0)      # e.g. +20.0%
    expense_delta_pct = db.Column(db.Float, default=0.0)      # e.g. -15.0%
    study_hours_delta = db.Column(db.Float, default=0.0)      # e.g. +1.5 hrs/day
    sleep_hours_delta = db.Column(db.Float, default=0.0)      # e.g. +1.0 hrs/day
    
    # Forecasted impact outcomes
    projected_savings_30d = db.Column(db.Float, default=0.0)
    projected_savings_90d = db.Column(db.Float, default=0.0)
    projected_savings_1yr = db.Column(db.Float, default=0.0)
    projected_productivity_score = db.Column(db.Float, default=85.0)
    projected_goal_delta_days = db.Column(db.Integer, default=0) # positive means reached earlier
    
    is_active_baseline = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description or "",
            "scenario_type": self.scenario_type,
            "savings_delta_pct": self.savings_delta_pct,
            "expense_delta_pct": self.expense_delta_pct,
            "study_hours_delta": self.study_hours_delta,
            "sleep_hours_delta": self.sleep_hours_delta,
            "projected_savings_30d": round(self.projected_savings_30d or 0.0, 2),
            "projected_savings_90d": round(self.projected_savings_90d or 0.0, 2),
            "projected_savings_1yr": round(self.projected_savings_1yr or 0.0, 2),
            "projected_productivity_score": round(self.projected_productivity_score or 85.0, 1),
            "projected_goal_delta_days": self.projected_goal_delta_days or 0,
            "is_active_baseline": self.is_active_baseline,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class AIRecommendation(db.Model):
    __tablename__ = 'ai_recommendations'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), default='Financial') # Financial, Habit, Productivity, Risk, Cross-Domain
    recommendation_text = db.Column(db.Text, nullable=False)
    impact_score = db.Column(db.String(20), default='High') # High, Medium, Low
    action_type = db.Column(db.String(50), default='simulate_scenario')
    action_payload = db.Column(db.Text, nullable=True) # JSON or config string
    
    is_applied = db.Column(db.Boolean, default=False)
    is_dismissed = db.Column(db.Boolean, default=False)
    feedback_rating = db.Column(db.Integer, default=0) # 1: Upvote, -1: Downvote, 0: None
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "recommendation_text": self.recommendation_text,
            "impact_score": self.impact_score,
            "action_type": self.action_type,
            "action_payload": self.action_payload or "{}",
            "is_applied": self.is_applied,
            "is_dismissed": self.is_dismissed,
            "feedback_rating": self.feedback_rating,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class ExternalBenchmark(db.Model):
    __tablename__ = 'external_benchmarks'
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(100), unique=True, nullable=False)
    metric_value = db.Column(db.Float, nullable=False)
    metric_unit = db.Column(db.String(20), default='%')
    source = db.Column(db.String(200), default='Economic Benchmark 2026')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_unit": self.metric_unit,
            "source": self.source,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }