import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_study_dataset(n_records=900, output_path="study_dataset.csv"):
    """
    Generates a realistic synthetic study tracking dataset for educational analytics,
    weekly study hours forecasting, and exam readiness score prediction.
    """
    np.random.seed(42)
    
    subjects = [
        "Python Programming", "Java", "Distributed Systems",
        "Cloud Architecture", "Machine Learning", "Quantitative Risk",
        "Algorithms & Data Structures", "Database Engineering"
    ]
    
    study_methods = ["Practice", "Revision", "Theory", "Problem Solving"]
    
    start_date = datetime(2024, 1, 1)
    records = []
    
    for i in range(n_records):
        record_date = start_date + timedelta(days=int(i * 0.8))
        subject = np.random.choice(subjects, p=[0.22, 0.18, 0.15, 0.15, 0.12, 0.08, 0.05, 0.05])
        method = np.random.choice(study_methods, p=[0.42, 0.30, 0.15, 0.13])
        
        # Study hours between 0.5 and 7.5 hours
        if method in ["Practice", "Problem Solving"]:
            hours = np.random.normal(3.2, 1.1)
        else:
            hours = np.random.normal(2.1, 0.8)
        hours = round(float(np.clip(hours, 0.5, 8.0)), 1)
        
        # Focus score between 50 and 100
        focus_score = int(np.clip(np.random.normal(82, 10), 45, 100))
        
        # Past 7 days accumulated hours
        past_7d_hours = round(float(np.clip(np.random.normal(16.5, 5.0), 3.0, 42.0)), 1)
        
        # Method weight for exam readiness
        method_multiplier = {"Practice": 1.12, "Problem Solving": 1.10, "Revision": 1.05, "Theory": 0.95}[method]
        
        # Exam readiness score (0-100)
        readiness = (
            (focus_score * 0.40) +
            (min(hours, 6.0) / 6.0 * 30.0 * method_multiplier) +
            (min(past_7d_hours, 30.0) / 30.0 * 30.0) +
            np.random.normal(0, 3.0)
        )
        exam_readiness = round(float(np.clip(readiness, 20.0, 99.0)), 1)
        
        # Predicted weekly hours
        predicted_weekly_hours = round(float(np.clip(hours * 5.2 + np.random.normal(0, 2.0), 5.0, 45.0)), 1)
        
        records.append({
            "Date": record_date.strftime("%Y-%m-%d"),
            "Subject": subject,
            "Study_Method": method,
            "Hours_Spent": hours,
            "Focus_Score": focus_score,
            "Past_7Day_Hours": past_7d_hours,
            "Exam_Readiness_Score": exam_readiness,
            "Predicted_Weekly_Hours": predicted_weekly_hours
        })
        
    df = pd.DataFrame(records)
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} study tracking records in '{output_path}'.")
    return df

if __name__ == "__main__":
    generate_study_dataset(n_records=900, output_path="study_dataset.csv")
