import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_habit_dataset(n_records=1000, output_path="habit_dataset.csv"):
    """
    Generates a realistic habit and productivity dataset for training regression models
    to forecast daily productivity scores and 7-day productivity trajectories.
    """
    np.random.seed(42)
    
    habit_names = [
        "Deep Work Block", "Morning Workout / Exercise", "Daily Reading",
        "Meditation & Mindfulness", "Hydration & Nutrition Tracking",
        "Coding Practice", "Language Learning", "Evening Journaling"
    ]
    
    statuses = ["Completed", "Partial", "Missed"]
    
    start_date = datetime(2024, 1, 1)
    records = []
    
    for i in range(n_records):
        record_date = start_date + timedelta(days=int(i * 0.7))
        habit_name = np.random.choice(habit_names)
        status = np.random.choice(statuses, p=[0.68, 0.22, 0.10])
        
        # 1. Sleep Hours (4.5 to 9.5 hours)
        sleep_hours = round(float(np.clip(np.random.normal(7.2, 1.1), 4.0, 10.0)), 1)
        
        # 2. Exercise Minutes (0 to 90 minutes)
        if np.random.rand() < 0.25:
            exercise_mins = 0
        else:
            exercise_mins = int(np.clip(np.random.normal(38, 18), 10, 90))
            
        # 3. Screen Time Hours (1.5 to 11.0 hours)
        screen_time_hours = round(float(np.clip(np.random.normal(5.8, 1.8), 1.0, 12.0)), 1)
        
        # 4. Tasks Completed (1 to 14 tasks)
        tasks_completed = int(np.clip(np.random.normal(6.5, 2.5), 1, 15))
        
        # 5. Habit Duration Minutes (15 to 120 minutes)
        if status == "Completed":
            habit_duration = int(np.clip(np.random.normal(55, 20), 20, 120))
        elif status == "Partial":
            habit_duration = int(np.clip(np.random.normal(25, 10), 10, 45))
        else:
            habit_duration = int(np.clip(np.random.normal(10, 5), 5, 20))
            
        # Realistic multi-variable ground truth productivity calculation:
        # - Optimal sleep is 7-8 hours (penalize <6 or >9)
        sleep_factor = max(0.0, 1.0 - (abs(sleep_hours - 7.5) / 3.5)) * 25.0
        # - Exercise gives up to 20 points
        exercise_factor = min(exercise_mins / 45.0, 1.0) * 20.0
        # - High screen time (>6 hrs) decreases productivity
        screen_penalty = max(0.0, (screen_time_hours - 4.5) * 3.5)
        # - Tasks completed adds up to 30 points
        tasks_factor = min(tasks_completed / 8.0, 1.0) * 30.0
        # - Habit duration adds up to 25 points
        duration_factor = min(habit_duration / 60.0, 1.0) * 25.0
        
        raw_score = 15.0 + sleep_factor + exercise_factor + tasks_factor + duration_factor - screen_penalty
        productivity_score = round(float(np.clip(raw_score + np.random.normal(0, 3.5), 10.0, 99.5)), 1)
        
        records.append({
            "Date": record_date.strftime("%Y-%m-%d"),
            "Habit_Name": habit_name,
            "Status": status,
            "Sleep_Hours": sleep_hours,
            "Exercise_Minutes": exercise_mins,
            "Screen_Time_Hours": screen_time_hours,
            "Tasks_Completed": tasks_completed,
            "Habit_Duration_Minutes": habit_duration,
            "Productivity_Score": productivity_score
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} habit records in '{output_path}'.")
    return df

if __name__ == "__main__":
    generate_habit_dataset(n_records=1000, output_path="habit_dataset.csv")
