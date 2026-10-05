import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from study_dataset import generate_study_dataset

def train_study_model(dataset_path="study_dataset.csv", model_export_path="study_model.pkl"):
    """
    Trains and serializes study tracking regression models using scikit-learn and pickle.
    Predicts Exam Readiness Score (0-100) and Projected Weekly Study Hours.
    """
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Generating new study dataset...")
        generate_study_dataset(n_records=900, output_path=dataset_path)
        
    df = pd.read_csv(dataset_path)
    print(f"Loaded study dataset with {len(df)} rows.")
    
    # Label encoding for categorical features
    le_subject = LabelEncoder()
    df["Subject_Code"] = le_subject.fit_transform(df["Subject"].astype(str))
    
    le_method = LabelEncoder()
    df["Method_Code"] = le_method.fit_transform(df["Study_Method"].astype(str))
    
    feature_cols = ["Subject_Code", "Method_Code", "Hours_Spent", "Focus_Score", "Past_7Day_Hours"]
    X = df[feature_cols].fillna(0)
    y_readiness = df["Exam_Readiness_Score"]
    y_weekly_hours = df["Predicted_Weekly_Hours"]
    
    # Train / test split
    X_train, X_test, y_read_train, y_read_test = train_test_split(X, y_readiness, test_size=0.2, random_state=42)
    _, _, y_wh_train, y_wh_test = train_test_split(X, y_weekly_hours, test_size=0.2, random_state=42)
    
    # Train models
    model_readiness = RandomForestRegressor(n_estimators=70, max_depth=7, random_state=42)
    model_readiness.fit(X_train, y_read_train)
    
    model_weekly_hours = LinearRegression()
    model_weekly_hours.fit(X_train, y_wh_train)
    
    # Evaluation
    pred_read = model_readiness.predict(X_test)
    pred_wh = model_weekly_hours.predict(X_test)
    
    mae_read = mean_absolute_error(y_read_test, pred_read)
    mse_read = mean_squared_error(y_read_test, pred_read)
    r2_read = r2_score(y_read_test, pred_read)
    
    mae_wh = mean_absolute_error(y_wh_test, pred_wh)
    mse_wh = mean_squared_error(y_wh_test, pred_wh)
    r2_wh = r2_score(y_wh_test, pred_wh)
    
    print("\n--- Study ML Model Evaluation ---")
    print(f"Exam Readiness Model -> MAE: {mae_read:.2f}, MSE: {mse_read:.2f}, R2: {r2_read:.4f}")
    print(f"Weekly Hours Forecast -> MAE: {mae_wh:.2f}, MSE: {mse_wh:.2f}, R2: {r2_wh:.4f}")
    
    # Serialization
    bundle = {
        "model_readiness": model_readiness,
        "model_weekly_hours": model_weekly_hours,
        "le_subject": le_subject,
        "le_method": le_method,
        "feature_cols": feature_cols,
        "subjects": list(le_subject.classes_),
        "methods": list(le_method.classes_),
        "metrics": {
            "mae_readiness": float(mae_read),
            "mse_readiness": float(mse_read),
            "r2_readiness": float(r2_read),
            "mae_weekly_hours": float(mae_wh),
            "mse_weekly_hours": float(mse_wh),
            "r2_weekly_hours": float(r2_wh)
        }
    }
    
    with open(model_export_path, "wb") as f:
        pickle.dump(bundle, f)
        
    print(f"Successfully exported study model bundle to '{model_export_path}'.")
    return bundle

if __name__ == "__main__":
    train_study_model()
