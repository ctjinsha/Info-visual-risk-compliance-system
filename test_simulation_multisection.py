import unittest
import json
from app import app, db, User

class SimulationMultiSectionTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def set_session_user(self):
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(email='shreya@optimatrack.com').first()
            if not user:
                user = User(
                    email='shreya@optimatrack.com',
                    password_hash='dummy_hash',
                    name='Shreya'
                )
                db.session.add(user)
                db.session.commit()
            sess['user_id'] = user.id

    def test_study_simulation_endpoint(self):
        self.set_session_user()
        payload = {
            "hours_delta": 1.5,
            "focus_delta": 10,
            "study_method": "feynman",
            "target_hours": 60,
            "days_per_week": 6
        }
        res = self.client.post(
            '/api/v1/simulation/study',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        sim = data['simulation']
        self.assertEqual(sim['domain'], 'study')
        self.assertIn('academic_outcomes', sim)
        outcomes = sim['academic_outcomes']
        self.assertIn('scenario_readiness', outcomes)
        self.assertIn('cumulative_12w_hours', outcomes)
        self.assertIn('fatigue_status', outcomes)
        self.assertEqual(len(sim['progression_curve']), 12)

    def test_habit_simulation_endpoint(self):
        self.set_session_user()
        payload = {
            "sleep_delta": 1.0,
            "exercise_delta": 30,
            "screen_reduction": 45,
            "habit_duration_days": 30,
            "task_velocity": 4
        }
        res = self.client.post(
            '/api/v1/simulation/habit',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        sim = data['simulation']
        self.assertEqual(sim['domain'], 'habit')
        self.assertIn('behavioral_outcomes', sim)
        outcomes = sim['behavioral_outcomes']
        self.assertIn('scenario_productivity_score', outcomes)
        self.assertIn('adherence_probability', outcomes)
        self.assertIn('weekly_reclaimed_hours', outcomes)
        self.assertEqual(len(sim['progression_curve']), 30)

    def test_finance_simulation_endpoint(self):
        self.set_session_user()
        payload = {
            "savings_boost_pct": 20,
            "expense_cut_pct": 15,
            "investment_roi_pct": 9,
            "months_horizon": 12
        }
        res = self.client.post(
            '/api/v1/simulation/finance',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertTrue(data['success'])
        sim = data['simulation']
        self.assertEqual(sim['domain'], 'finance')
        self.assertIn('financial_outcomes', sim)
        outcomes = sim['financial_outcomes']
        self.assertIn('final_scenario_wealth', outcomes)
        self.assertIn('monthly_savings_delta', outcomes)
        self.assertEqual(len(sim['progression_curve']), 12)

    def test_generic_simulation_run_dispatcher(self):
        self.set_session_user()
        # Test study dispatch
        res_study = self.client.post(
            '/api/v1/simulation/run',
            data=json.dumps({'domain': 'study', 'hours_delta': 2.0}),
            content_type='application/json'
        )
        self.assertEqual(res_study.status_code, 200)
        self.assertTrue(json.loads(res_study.data)['success'])

        # Test habit dispatch
        res_habit = self.client.post(
            '/api/v1/simulation/run',
            data=json.dumps({'domain': 'habit', 'sleep_delta': 1.5}),
            content_type='application/json'
        )
        self.assertEqual(res_habit.status_code, 200)
        self.assertTrue(json.loads(res_habit.data)['success'])

        # Test finance dispatch
        res_finance = self.client.post(
            '/api/v1/simulation/run',
            data=json.dumps({'domain': 'finance', 'savings_boost_pct': 25}),
            content_type='application/json'
        )
        self.assertEqual(res_finance.status_code, 200)
        self.assertTrue(json.loads(res_finance.data)['success'])

    def test_ai_chat_and_knowledge_endpoints(self):
        self.set_session_user()
        # 1. Test /chat page load
        res_page = self.client.get('/chat')
        self.assertEqual(res_page.status_code, 200)
        self.assertIn(b'AI Knowledge &amp; Data Assistant', res_page.data)
        self.assertIn(b'High-Token Deep Analysis', res_page.data)

        # 2. Test Architecture deep dive query
        res_arch = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'Explain the entire project architecture and tech stack', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_arch.status_code, 200)
        data_arch = json.loads(res_arch.data)
        self.assertIn('System Architecture', data_arch['title'])
        self.assertIn('Flask 3.0', data_arch['reply'])
        self.assertGreater(data_arch['tokens_estimate'], 300)

        # 3. Test ML Models deep dive query
        res_ml = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'How do the 3 ML models work and what are their R2 scores?', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_ml.status_code, 200)
        data_ml = json.loads(res_ml.data)
        self.assertIn('study_model.pkl', data_ml['reply'])
        self.assertIn('habit_model.pkl', data_ml['reply'])
        self.assertIn('finance_model.pkl', data_ml['reply'])

        # 5. Test Study Procrastination / Exam Doubt Advice Query
        res_doubt_study = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'I have a doubt on how to stop procrastinating and prepare for exams effectively', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_doubt_study.status_code, 200)
        data_doubt_study = json.loads(res_doubt_study.data)
        self.assertIn('Academic Mastery', data_doubt_study['title'])
        self.assertIn('Feynman', data_doubt_study['reply'])
        self.assertIn('90-Minute Ultradian', data_doubt_study['reply'])

        # 6. Test Sleep & Screen Time Doubt Advice Query
        res_doubt_sleep = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'Give me advice on fixing late night sleep and reducing 5+ hours screen time', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_doubt_sleep.status_code, 200)
        data_doubt_sleep = json.loads(res_doubt_sleep.data)
        self.assertIn('Habit Optimization', data_doubt_sleep['title'])
        self.assertIn('10-3-2-1-0 Sleep Hygiene', data_doubt_sleep['reply'])

        # 7. Test Financial Budget Allocation Doubt Advice Query
        res_doubt_fin = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'How should I allocate my salary between savings, expenses, and emergency fund?', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_doubt_fin.status_code, 200)
        data_doubt_fin = json.loads(res_doubt_fin.data)
        self.assertIn('Capital Allocation', data_doubt_fin['title'])
        self.assertIn('Emergency Liquidity Moat', data_doubt_fin['reply'])

        # 9. Test User's Exact Query: "hi can you give some advice to improve my savings"
        res_exact = self.client.post(
            '/api/v1/ai/chat',
            data=json.dumps({'message': 'hi can you give some advice to improve my savings', 'mode': 'detailed'}),
            content_type='application/json'
        )
        self.assertEqual(res_exact.status_code, 200)
        data_exact = json.loads(res_exact.data)
        self.assertEqual(data_exact['intent'], 'financial_doubt_advice')
        self.assertIn('Financial Capital Advisory', data_exact['reply'])
        self.assertIn('Emergency Liquidity Moat', data_exact['reply'])
        self.assertIn('Monthly Surplus Velocity', data_exact['reply'])

if __name__ == '__main__':
    unittest.main()
