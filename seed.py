from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import app, db
from models import (
    User, FinancialRecord, StudyRecord, HabitRecord,
    FitnessRecord, GoalRecord, AuditLog, AlertNotice, BehavioralEntry,
    SimulationScenario, AIRecommendation, ExternalBenchmark
)

with app.app_context():
    print("Seeding rich OptimaTrack data...")

    # 1. Create or fetch demo users
    user_shreya = User.query.filter_by(email="shreya@optimatrack.com").first()
    if not user_shreya:
        user_shreya = User(
            email="shreya@optimatrack.com",
            password_hash=generate_password_hash("password123"),
            name="Shreya",
            occupation="Risk & Compliance Lead",
            age=26,
            goal_score=88,
            days_active=48,
            profile_picture="default.png"
        )
        db.session.add(user_shreya)

    user_admin = User.query.filter_by(email="ctjinshamol@gmail.com").first()
    if not user_admin:
        user_admin = User(
            email="ctjinshamol@gmail.com",
            password_hash=generate_password_hash("password123"),
            name="Jinsha",
            occupation="Visual Risk Engineer",
            age=23,
            goal_score=92,
            days_active=60,
            profile_picture="default.png"
        )
        db.session.add(user_admin)

    db.session.commit()

    users = [user_shreya, user_admin]

    for u in users:
        # Clear existing records for clean demo seed
        FinancialRecord.query.filter_by(user_id=u.id).delete()
        StudyRecord.query.filter_by(user_id=u.id).delete()
        HabitRecord.query.filter_by(user_id=u.id).delete()
        FitnessRecord.query.filter_by(user_id=u.id).delete()
        GoalRecord.query.filter_by(user_id=u.id).delete()
        AlertNotice.query.filter_by(user_id=u.id).delete()
        AuditLog.query.filter_by(user_id=u.id).delete()

        # 2. Seed Savings Records (Matching Image 1)
        savings_data = [
            {"category": "Bank", "amount": 15000.0, "target_amount": 20000.0, "currency": "INR", "target_date": "2026-12-31", "notes": "Emergency Reserve Fund"},
            {"category": "Mutual Fund", "amount": 45000.0, "target_amount": 100000.0, "currency": "INR", "target_date": "2027-06-30", "notes": "Nifty Index Fund SIP"},
            {"category": "Crypto Reserve", "amount": 12000.0, "target_amount": 25000.0, "currency": "INR", "target_date": "2026-11-15", "notes": "Defi Staking Allocation"},
            {"category": "Cash", "amount": 8000.0, "target_amount": 10000.0, "currency": "INR", "target_date": "2026-10-01", "notes": "Liquidity Buffer"}
        ]
        for s in savings_data:
            db.session.add(FinancialRecord(
                user_id=u.id,
                record_type="Saving",
                category=s["category"],
                amount=s["amount"],
                target_amount=s["target_amount"],
                currency=s["currency"],
                target_date=s["target_date"],
                notes=s["notes"]
            ))

        # Seed Income & Expenses
        db.session.add(FinancialRecord(user_id=u.id, record_type="Income", category="Primary Tech Lead Salary", amount=30000.0, currency="INR", notes="Monthly Primary Income"))
        db.session.add(FinancialRecord(user_id=u.id, record_type="Income", category="Consulting & Advisory", amount=8500.0, currency="INR", notes="Quarterly Advisory Retainer"))
        db.session.add(FinancialRecord(user_id=u.id, record_type="Expense", category="Housing & Prime Utilities", amount=12000.0, currency="INR", notes="Rent, High-Speed Fiber, Electricity"))
        db.session.add(FinancialRecord(user_id=u.id, record_type="Expense", category="Learning & Certifications", amount=3500.0, currency="INR", notes="AWS Cloud Labs, Books, Subscriptions"))
        db.session.add(FinancialRecord(user_id=u.id, record_type="Expense", category="Discretionary & Dining", amount=4000.0, currency="INR", notes="Healthy Dining & Specialty Coffee"))

        # 3. Seed Study & Focus Records
        study_data = [
            {"subject": "Distributed Systems", "topic": "Raft & Paxos Consensus Protocols", "hours_spent": 4.5, "focus_score": 94, "target_date": "2026-09-30", "notes": "Passed MIT 6.824 Lab 2"},
            {"subject": "Quantitative Risk", "topic": "Monte Carlo Value-at-Risk Simulations", "hours_spent": 3.0, "focus_score": 91, "target_date": "2026-10-01", "notes": "Stress-testing portfolio tails"},
            {"subject": "Cloud Architecture", "topic": "AWS Security Specialty & Zero Trust", "hours_spent": 4.0, "focus_score": 96, "target_date": "2026-10-15", "notes": "KMS Envelopes & IAM Boundaries"},
            {"subject": "Machine Learning", "topic": "Transformer Attention & Fine-tuning", "hours_spent": 2.5, "focus_score": 88, "target_date": "2026-11-01", "notes": "LoRA weights evaluation"}
        ]
        for st in study_data:
            db.session.add(StudyRecord(
                user_id=u.id,
                subject=st["subject"],
                topic=st["topic"],
                hours_spent=st["hours_spent"],
                focus_score=st["focus_score"],
                target_date=st["target_date"],
                notes=st.get("notes", "")
            ))

        # 4. Seed Habits & Compliance
        habit_data = [
            {"title": "Deep Work Block (9 AM - 12 PM)", "category": "Productivity", "frequency": "Daily", "status": "Completed", "impact_on_goals": "High", "streak": 18},
            {"title": "Zero Unplanned Spending", "category": "Finance", "frequency": "Daily", "status": "Completed", "impact_on_goals": "High", "streak": 12},
            {"title": "Review Daily Risk Metrics", "category": "Compliance", "frequency": "Daily", "status": "Completed", "impact_on_goals": "Medium", "streak": 24},
            {"title": "8 Hours Sleep Cycle", "category": "Health", "frequency": "Daily", "status": "Completed", "impact_on_goals": "High", "streak": 8},
            {"title": "Evening 20-min Reading", "category": "Mindfulness", "frequency": "Daily", "status": "Completed", "impact_on_goals": "Medium", "streak": 15}
        ]
        for h in habit_data:
            db.session.add(HabitRecord(
                user_id=u.id,
                title=h["title"],
                category=h["category"],
                frequency=h["frequency"],
                status=h["status"],
                impact_on_goals=h["impact_on_goals"],
                streak=h["streak"]
            ))

        # 5. Seed Fitness Records
        fitness_data = [
            {"activity_type": "5K Morning Run", "duration_minutes": 27, "calories_burned": 340, "target": "Pace < 5:30/km", "notes": "Aerobic base conditioning"},
            {"activity_type": "Upper Body Strength & Hypertrophy", "duration_minutes": 50, "calories_burned": 320, "target": "Bench Press & Pull-ups", "notes": "Hypertrophy Block A"},
            {"activity_type": "HIIT Cardio & Core", "duration_minutes": 30, "calories_burned": 290, "target": "Heart Rate > 165 bpm", "notes": "Tabata Interval Protocol"},
            {"activity_type": "Weekend Road Cycling", "duration_minutes": 75, "calories_burned": 580, "target": "32 km distance", "notes": "Cadence 85+ rpm"}
        ]
        for f in fitness_data:
            db.session.add(FitnessRecord(
                user_id=u.id,
                activity_type=f["activity_type"],
                duration_minutes=f["duration_minutes"],
                calories_burned=f["calories_burned"],
                target=f["target"],
                notes=f.get("notes", "")
            ))

        # 6. Seed Goals & Milestones
        goal_data = [
            {"title": "Emergency Capital Reserve ($25k)", "category": "Financial", "current_val": 15000.0, "target_val": 25000.0, "unit": "$", "deadline": "2026-12-31"},
            {"title": "AWS Solutions Architect Cert", "category": "Academic", "current_val": 80.0, "target_val": 100.0, "unit": "%", "deadline": "2026-10-31"},
            {"title": "Sub-25 Minute 5K Time Trial", "category": "Fitness", "current_val": 88.0, "target_val": 100.0, "unit": "%", "deadline": "2026-11-15"},
            {"title": "100-Day Continuous Coding Streak", "category": "Career", "current_val": 60.0, "target_val": 100.0, "unit": "days", "deadline": "2026-10-01"}
        ]
        for g in goal_data:
            db.session.add(GoalRecord(
                user_id=u.id,
                title=g["title"],
                category=g["category"],
                current_val=g["current_val"],
                target_val=g["target_val"],
                unit=g["unit"],
                deadline=g["deadline"]
            ))

        # 8. Seed Milestone 3 Simulation Scenarios
        SimulationScenario.query.filter_by(user_id=u.id).delete()
        AIRecommendation.query.filter_by(user_id=u.id).delete()

        scenarios_data = [
            {
                "title": "Aggressive 25% Savings & Deep Work Protocol",
                "description": "Increase SIP by 25%, curb discretionary dining by 15%, and add 1.5h daily deep work block.",
                "scenario_type": "Aggressive",
                "savings_delta_pct": 25.0,
                "expense_delta_pct": -15.0,
                "study_hours_delta": 1.5,
                "sleep_hours_delta": 0.5,
                "projected_savings_30d": 21500.0,
                "projected_savings_90d": 64500.0,
                "projected_savings_1yr": 274000.0,
                "projected_productivity_score": 93.5,
                "projected_goal_delta_days": 45,
                "is_active_baseline": False
            },
            {
                "title": "Moderate SIP Boost (+15%) & Sleep Optimization",
                "description": "Boost monthly savings rate by 15% and increase sleep by 1 hour for enhanced cognitive stamina.",
                "scenario_type": "Optimistic",
                "savings_delta_pct": 15.0,
                "expense_delta_pct": -5.0,
                "study_hours_delta": 0.5,
                "sleep_hours_delta": 1.0,
                "projected_savings_30d": 18200.0,
                "projected_savings_90d": 54600.0,
                "projected_savings_1yr": 231000.0,
                "projected_productivity_score": 91.0,
                "projected_goal_delta_days": 28,
                "is_active_baseline": False
            }
        ]
        for sc in scenarios_data:
            db.session.add(SimulationScenario(
                user_id=u.id,
                title=sc["title"],
                description=sc["description"],
                scenario_type=sc["scenario_type"],
                savings_delta_pct=sc["savings_delta_pct"],
                expense_delta_pct=sc["expense_delta_pct"],
                study_hours_delta=sc["study_hours_delta"],
                sleep_hours_delta=sc["sleep_hours_delta"],
                projected_savings_30d=sc["projected_savings_30d"],
                projected_savings_90d=sc["projected_savings_90d"],
                projected_savings_1yr=sc["projected_savings_1yr"],
                projected_productivity_score=sc["projected_productivity_score"],
                projected_goal_delta_days=sc["projected_goal_delta_days"],
                is_active_baseline=sc["is_active_baseline"]
            ))

        # 9. Seed AI Recommendations
        recs_data = [
            {
                "title": "Automate 15% Index SIP on 1st of Month",
                "category": "Financial",
                "recommendation_text": "Moving ₹4,500 automatically to Nifty Index SIP on salary credit day eliminates discretionary spending leakage and reaches Emergency Reserve 42 days earlier.",
                "impact_score": "High",
                "action_type": "simulate_scenario",
                "action_payload": '{"savings_delta_pct": 15, "expense_delta_pct": -5}'
            },
            {
                "title": "Habit Stacking: Post-Workout Technical Reading",
                "category": "Habit",
                "recommendation_text": "Your 5K Morning Run streak is active (8+ days). Attaching your 20-minute Distributed Systems reading immediately after your morning run triples habit retention.",
                "impact_score": "High",
                "action_type": "habit_stack",
                "action_payload": '{"trigger_habit": "Morning Run", "stacked_habit": "Technical Reading"}'
            },
            {
                "title": "Peak Focus Deep Work Window (9 AM - 11:30 AM)",
                "category": "Productivity",
                "recommendation_text": "Telemetry confirms focus scores reach 94/100 during morning deep work blocks. Protect this window from non-critical meetings.",
                "impact_score": "Medium",
                "action_type": "schedule_block",
                "action_payload": '{"preferred_window": "09:00 - 11:30"}'
            }
        ]
        for r in recs_data:
            db.session.add(AIRecommendation(
                user_id=u.id,
                title=r["title"],
                category=r["category"],
                recommendation_text=r["recommendation_text"],
                impact_score=r["impact_score"],
                action_type=r["action_type"],
                action_payload=r["action_payload"]
            ))

    # 10. External Reference Benchmarks
    ExternalBenchmark.query.delete()
    benchmarks = [
        {"metric_name": "inflation_rate", "metric_value": 5.4, "metric_unit": "%", "source": "RBI Macro Economic Reference 2026"},
        {"metric_name": "market_nifty_cagr", "metric_value": 13.8, "metric_unit": "%", "source": "NSE 5-Year Rolling Index Return"},
        {"metric_name": "benchmark_savings_rate", "metric_value": 25.0, "metric_unit": "%", "source": "Personal Finance Standard 50/30/20 Rule"},
        {"metric_name": "benchmark_sleep_hours", "metric_value": 7.5, "metric_unit": "hrs", "source": "Sleep Research & Cognitive Performance Standard"},
        {"metric_name": "benchmark_deep_work_hours", "metric_value": 3.5, "metric_unit": "hrs", "source": "Deep Work & Flow State Benchmark"}
    ]
    for b in benchmarks:
        db.session.add(ExternalBenchmark(
            metric_name=b["metric_name"],
            metric_value=b["metric_value"],
            metric_unit=b["metric_unit"],
            source=b["source"]
        ))

    db.session.commit()
    print("Database successfully seeded with realistic OptimaTrack Milestone 3 data!")