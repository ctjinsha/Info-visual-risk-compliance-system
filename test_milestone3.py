import unittest
import json
from app import app, db
from models import User, FinancialRecord, DailyFinancialRecord, StudyRecord, HabitRecord, SimulationScenario, AIRecommendation, ExternalBenchmark
from intelligence_engine import (
    FinancialForecastingEngine, HabitProductivityAnalyticsEngine,
    WhatIfSimulationEngine, PredictiveAnalyticsEngine, AIRecommendationEngine
)

class Milestone3IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Find or create a test user
        self.user = User.query.filter_by(email="shreya@optimatrack.com").first()
        if not self.user:
            self.user = User.query.first()

    def tearDown(self):
        self.app_context.pop()

    def test_01_financial_forecasting_engine(self):
        daily_records = DailyFinancialRecord.query.filter_by(user_id=self.user.id).all()
        forecast = FinancialForecastingEngine.forecast_cashflow(daily_records, horizon_days=30)
        
        self.assertIn("timeline", forecast)
        self.assertEqual(len(forecast["timeline"]), 30)
        self.assertIn("total_projected_expense", forecast)
        self.assertIn("projected_final_savings", forecast)

        sip_proj = FinancialForecastingEngine.project_investment_growth(
            initial_capital=50000, monthly_sip=5000, annual_cagr_pct=12.0, horizon_years=2, inflation_rate=5.0
        )
        self.assertIn("growth_timeline", sip_proj)
        self.assertGreater(sip_proj["final_nominal_wealth"], sip_proj["final_invested"])

        risk = FinancialForecastingEngine.compute_financial_risk_score([38000], [18000], [15000])
        self.assertIn("score", risk)
        self.assertIn("rating", risk)
        self.assertLess(risk["score"], 50.0)

    def test_02_habit_productivity_engine(self):
        habits = HabitRecord.query.filter_by(user_id=self.user.id).all()
        studies = StudyRecord.query.filter_by(user_id=self.user.id).all()
        daily = DailyFinancialRecord.query.filter_by(user_id=self.user.id).all()

        correlations = HabitProductivityAnalyticsEngine.calculate_correlations(habits, studies, daily)
        self.assertIn("correlations", correlations)
        self.assertIn("matrix", correlations["correlations"])
        self.assertEqual(len(correlations["correlations"]["variables"]), 5)

        prod_score = HabitProductivityAnalyticsEngine.compute_personalized_productivity_score(habits, studies, [])
        self.assertIn("productivity_score", prod_score)
        self.assertIn("grade", prod_score)

    def test_03_what_if_simulation_engine(self):
        baseline = {
            "monthly_savings": 15000.0,
            "monthly_expense": 19500.0,
            "current_savings": 80000.0,
            "productivity_score": 88.0,
            "emergency_goal_remaining": 10000.0
        }
        sim = WhatIfSimulationEngine.simulate_scenario(
            baseline, savings_delta_pct=25.0, expense_delta_pct=-15.0, study_hours_delta=1.5, sleep_hours_delta=0.5
        )
        self.assertIn("financial_outcomes", sim)
        self.assertIn("productivity_outcomes", sim)
        self.assertIn("progression_curve", sim)
        self.assertGreater(sim["financial_outcomes"]["savings_1yr"], sim["financial_outcomes"]["base_savings_1yr"])
        self.assertGreater(sim["productivity_outcomes"]["scenario_productivity_score"], baseline["productivity_score"])

    def test_04_ai_recommendation_and_chat(self):
        user_context = {
            "name": "Shreya",
            "current_savings": 80000.0,
            "monthly_income": 38500.0,
            "monthly_expense": 19500.0,
            "monthly_savings": 15000.0,
            "productivity_score": 88.0,
            "top_goal": "Emergency Capital Reserve ($25,000)",
            "top_goal_progress": 60.0
        }

        # Query 1: What happens if I save 20% more?
        reply_savings = AIRecommendationEngine.chat_with_data("What happens if I save 20% more next month?", user_context)
        self.assertEqual(reply_savings["intent"], "what_if_savings")
        self.assertIn("20", reply_savings["reply"])

        # Query 2: Sleep correlation
        reply_sleep = AIRecommendationEngine.chat_with_data("Analyze my sleep vs productivity correlation", user_context)
        self.assertEqual(reply_sleep["intent"], "sleep_correlation")
        self.assertIn("Sleep Hours", reply_sleep["reply"])

        # Query 3: Goal ETA
        reply_goal = AIRecommendationEngine.chat_with_data("When will I reach my emergency fund goal?", user_context)
        self.assertEqual(reply_goal["intent"], "goal_projection")
        self.assertIn("Emergency Capital Reserve", reply_goal["reply"])

    def test_05_milestone3_api_endpoints(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.id

        # 1. Milestone 3 HTML view
        res = self.client.get('/milestone3')
        self.assertEqual(res.status_code, 200)

        # 2. Overview telemetry API
        res_ov = self.client.get('/api/v1/milestone3/overview')
        self.assertEqual(res_ov.status_code, 200)
        data_ov = json.loads(res_ov.data)
        self.assertIn("summary", data_ov)
        self.assertIn("forecasting", data_ov)
        self.assertIn("analytics", data_ov)
        self.assertIn("simulation", data_ov)
        self.assertIn("models", data_ov)

        # 3. Simulation run API
        res_sim = self.client.post('/api/v1/simulation/run', json={
            "savings_delta_pct": 20,
            "expense_delta_pct": -10,
            "study_hours_delta": 1.0,
            "sleep_hours_delta": 0.5
        })
        self.assertEqual(res_sim.status_code, 200)
        data_sim = json.loads(res_sim.data)
        self.assertTrue(data_sim["success"])

        # 4. Save and fetch scenario API
        res_scen = self.client.post('/api/v1/simulation/scenarios', json={
            "title": "Test Scenario Auto-Verification",
            "savings_delta_pct": 15,
            "expense_delta_pct": -5,
            "study_hours_delta": 1.0,
            "sleep_hours_delta": 0.5,
            "projected_savings_30d": 18000,
            "projected_savings_90d": 54000,
            "projected_savings_1yr": 220000,
            "projected_productivity_score": 90.5
        })
        self.assertEqual(res_scen.status_code, 201)
        data_scen = json.loads(res_scen.data)
        scen_id = data_scen["scenario"]["id"]

        # Delete scenario API
        res_del = self.client.delete(f'/api/v1/simulation/scenarios/{scen_id}')
        self.assertEqual(res_del.status_code, 200)

        # 5. AI Chat API
        res_chat = self.client.post('/api/v1/ai/chat', json={"message": "What happens if I save 25% more?"})
        self.assertEqual(res_chat.status_code, 200)
        data_chat = json.loads(res_chat.data)
        self.assertIn("reply", data_chat)

        # 6. EDA Analytics API
        res_eda = self.client.get('/api/v1/analytics/eda')
        self.assertEqual(res_eda.status_code, 200)

        # 7. Model retrain API
        res_retrain = self.client.post('/api/v1/models/retrain')
        self.assertEqual(res_retrain.status_code, 200)
        data_retrain = json.loads(res_retrain.data)
        self.assertTrue(data_retrain["success"])
        self.assertIn("finance", data_retrain["metrics"])

        # 8. Report export API
        res_rep = self.client.get('/api/v1/reports/export')
        self.assertEqual(res_rep.status_code, 200)

if __name__ == '__main__':
    unittest.main()
