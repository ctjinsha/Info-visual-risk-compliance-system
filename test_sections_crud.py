import unittest
from app import app, db, User, FinancialRecord, StudyRecord, HabitRecord, FitnessRecord, GoalRecord

class OptimaTrackSectionsTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_login_and_dashboard(self):
        res = self.client.post('/login', data={'email': 'shreya@optimatrack.com', 'password': 'password123'}, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'OptimaTrack', res.data)
        self.assertIn(b'Cashflow Ledger', res.data)
        self.assertIn(b'Study Sessions &amp; Focus', res.data)
        self.assertIn(b'Academics &amp; Curriculum', res.data)
        self.assertIn(b'Habits &amp; Behavioral Compliance', res.data)
        self.assertIn(b'Fitness &amp; Physical Wellness', res.data)
        self.assertIn(b'Goals &amp; Milestones', res.data)

    def test_authenticated_endpoints(self):
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(email='shreya@optimatrack.com').first()
            self.assertIsNotNone(user)
            sess['user_id'] = user.id

        # 1. Financial GET & POST & DELETE
        res = self.client.get('/api/v1/financial')
        self.assertEqual(res.status_code, 200)
        
        res = self.client.post('/api/v1/financial', json={
            'record_type': 'Income',
            'category': 'Freelance Project',
            'amount': 2500,
            'currency': 'USD',
            'notes': 'API Integration'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        fin_id = data['record']['id']

        res = self.client.delete(f'/api/v1/financial/{fin_id}')
        self.assertEqual(res.status_code, 200)

        # 2. Study GET & POST & DELETE
        res = self.client.get('/api/v1/study')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/api/v1/study', json={
            'subject': 'Quantum Computing',
            'topic': 'Qubits & Gates',
            'hours_spent': 2.5,
            'focus_score': 95,
            'target_date': '2026-10-10'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        study_id = data['record']['id']

        res = self.client.delete(f'/api/v1/study/{study_id}')
        self.assertEqual(res.status_code, 200)

        # 3. Habits GET, POST, PUT, DELETE
        res = self.client.get('/api/v1/habits')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/api/v1/habits', json={
            'title': 'Morning Meditation',
            'category': 'Mindfulness',
            'frequency': 'Daily',
            'impact_on_goals': 'High'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        habit_id = data['record']['id']

        res = self.client.put(f'/api/v1/habits/{habit_id}', json={'status': 'Completed'})
        self.assertEqual(res.status_code, 200)

        res = self.client.delete(f'/api/v1/habits/{habit_id}')
        self.assertEqual(res.status_code, 200)

        # 4. Fitness GET, POST, DELETE
        res = self.client.get('/api/v1/fitness')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/api/v1/fitness', json={
            'activity_type': 'Rowing',
            'duration_minutes': 30,
            'calories_burned': 260,
            'target': '5000m'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        fit_id = data['record']['id']

        res = self.client.delete(f'/api/v1/fitness/{fit_id}')
        self.assertEqual(res.status_code, 200)

        # 5. Goals GET, POST, DELETE
        res = self.client.get('/api/v1/goals')
        self.assertEqual(res.status_code, 200)

        res = self.client.post('/api/v1/goals', json={
            'title': 'Publish Technical Paper',
            'category': 'Academic',
            'current_val': 50,
            'target_val': 100,
            'unit': '%'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        goal_id = data['record']['id']

        res = self.client.delete(f'/api/v1/goals/{goal_id}')
        self.assertEqual(res.status_code, 200)

    def test_milestone2_pages_and_ml_predictions(self):
        with self.client.session_transaction() as sess:
            user = User.query.filter_by(email='shreya@optimatrack.com').first()
            self.assertIsNotNone(user)
            sess['user_id'] = user.id

        # 1. Habit Page & Activity Creation
        res = self.client.get('/habit')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Habit Intelligence', res.data)
        self.assertIn(b'Next 7 Days Productivity Trend', res.data)

        res = self.client.post('/habit', data={
            'title': 'Evening Stretching & Mobility',
            'duration_minutes': '25',
            'status': 'Completed',
            'category': 'Health',
            'date_str': '2026-09-08'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Evening Stretching', res.data)

        # 2. AI Productivity Prediction API
        res = self.client.post('/api/predict/productivity', json={
            'sleep_hours': 8.0,
            'exercise_minutes': 45,
            'screen_time': 4.5,
            'tasks_completed': 8,
            'habit_duration': 60
        })
        self.assertEqual(res.status_code, 200)
        pred_data = res.get_json()
        self.assertTrue(pred_data['success'])
        self.assertIn('score', pred_data)
        self.assertIn('trend', pred_data)
        self.assertEqual(len(pred_data['trend']), 7)

        # 3. Study Page & Record Creation
        res = self.client.get('/study')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Study Tracking, Metrics', res.data)

        res = self.client.post('/study', data={
            'subject': 'Machine Learning',
            'hours_spent': '3.5',
            'study_method': 'Practice',
            'topic': 'Scikit-learn Regressors',
            'focus_score': '95'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Machine Learning', res.data)

        # 4. AI Study Prediction API
        res = self.client.post('/api/predict/study', json={
            'subject': 'Machine Learning',
            'study_method': 'Practice',
            'hours_spent': 3.5,
            'focus_score': 95,
            'past_7d_hours': 20.0
        })
        self.assertEqual(res.status_code, 200)
        study_pred = res.get_json()
        self.assertTrue(study_pred['success'])
        self.assertIn('exam_readiness', study_pred)

        # 5. Finance Page & Transaction Creation
        res = self.client.get('/finance')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Financial Forecasting', res.data)
        self.assertIn(b'1-Year Financial Forecast Trajectory', res.data)

        res = self.client.post('/finance', data={
            'record_type': 'Expense',
            'category': 'Education & Tools',
            'amount': '1200',
            'notes': 'Cloud Credits'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 6. AI Finance Prediction API
        res = self.client.post('/api/predict/finance', json={
            'income': 65000.0,
            'total_expense': 22000.0,
            'current_savings': 80000.0
        })
        self.assertEqual(res.status_code, 200)
        fin_pred = res.get_json()
        self.assertTrue(fin_pred['success'])
        self.assertIn('projected_1y_savings', fin_pred)

        # 7. History Activity Ledger Page
        res = self.client.get('/history')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Historical Activity Ledger', res.data)
        self.assertIn(b'Chronological Event Feed', res.data)

        res_filtered = self.client.get('/history?domain=habit')
        self.assertEqual(res_filtered.status_code, 200)

if __name__ == '__main__':
    unittest.main()

