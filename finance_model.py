import os
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from finance_dataset import generate_financial_dataset

def train_finance_model(dataset_path="financial_forecasting_dataset.csv", model_export_path="finance_model.pkl"):
    """
    Trains and serializes financial forecasting regression models using scikit-learn ensemble (GBDT, Random Forest, Autoregressive Lag).
    Predicts next 7 days total expenses and next month savings velocity based on historical category spending.
    """
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Generating new financial dataset...")
        generate_financial_dataset(n_days=1200, output_path=dataset_path)
        
    df = pd.read_csv(dataset_path)
    print(f"Loaded financial dataset with {len(df)} rows.")
    
    # Autoregressive lag features (ARIMA-style)
    df["Lag_1_Expense"] = df["Total_Expense"].shift(1).fillna(df["Total_Expense"].mean()).round(2)
    df["Lag_7_Expense"] = df["Total_Expense"].shift(7).fillna(df["Total_Expense"].mean()).round(2)
    df["Lag_14_Expense"] = df["Total_Expense"].shift(14).fillna(df["Total_Expense"].mean()).round(2)
    
    # Define features
    feature_cols = [
        "Income", "Food_Expense", "Health_Expense", "Travel_Expense", "Other_Expense",
        "Total_Expense", "Lag_1_Expense", "Lag_7_Expense", "Lag_14_Expense",
        "Rolling_7Day_Total_Expense_Avg", "Rolling_30Day_Total_Expense_Avg",
        "Rolling_7Day_Savings_Avg"
    ]
    
    # Ensure missing engineered columns exist
    if "Rolling_7Day_Total_Expense_Avg" not in df.columns:
        df["Rolling_7Day_Total_Expense_Avg"] = df["Total_Expense"].rolling(window=7, min_periods=1).mean().round(2)
    if "Rolling_30Day_Total_Expense_Avg" not in df.columns:
        df["Rolling_30Day_Total_Expense_Avg"] = df["Total_Expense"].rolling(window=30, min_periods=1).mean().round(2)
    if "Rolling_7Day_Savings_Avg" not in df.columns:
        df["Rolling_7Day_Savings_Avg"] = df["Savings"].rolling(window=7, min_periods=1).mean().round(2)
    if "Target_Next_7Day_Total_Expense" not in df.columns:
        df["Target_Next_7Day_Total_Expense"] = df["Total_Expense"].shift(-7).fillna(df["Total_Expense"].mean()).round(2)
    if "Target_Next_Month_Savings" not in df.columns:
        df["Target_Next_Month_Savings"] = df["Savings"].rolling(window=30, min_periods=1).sum().shift(-30).fillna(df["Savings"].mean() * 30).round(2)
        
    X = df[feature_cols].fillna(0)
    y_expense = df["Target_Next_7Day_Total_Expense"]
    y_savings = df["Target_Next_Month_Savings"]
    
    # Train / Test split
    X_train, X_test, y_exp_train, y_exp_test = train_test_split(X, y_expense, test_size=0.2, random_state=42)
    _, _, y_sav_train, y_sav_test = train_test_split(X, y_savings, test_size=0.2, random_state=42)
    
    # Train models (Gradient Boosting + Random Forest Ensemble)
    model_expense = GradientBoostingRegressor(n_estimators=80, learning_rate=0.08, max_depth=4, random_state=42)
    model_expense.fit(X_train, y_exp_train)
    
    model_savings = RandomForestRegressor(n_estimators=75, random_state=42, max_depth=8)
    model_savings.fit(X_train, y_sav_train)
    
    # Evaluation
    pred_exp = model_expense.predict(X_test)
    pred_sav = model_savings.predict(X_test)
    
    mae_exp = mean_absolute_error(y_exp_test, pred_exp)
    mse_exp = mean_squared_error(y_exp_test, pred_exp)
    r2_exp = r2_score(y_exp_test, pred_exp)
    
    mae_sav = mean_absolute_error(y_sav_test, pred_sav)
    mse_sav = mean_squared_error(y_sav_test, pred_sav)
    r2_sav = r2_score(y_sav_test, pred_sav)
    
    print("\n--- Finance ML Model Evaluation ---")
    print(f"Expense Forecast Model -> MAE: {mae_exp:.2f}, MSE: {mse_exp:.2f}, R2: {r2_exp:.4f}")
    print(f"Savings Forecast Model -> MAE: {mae_sav:.2f}, MSE: {mse_sav:.2f}, R2: {r2_sav:.4f}")
    
    # Serialization
    bundle = {
        "model_expense": model_expense,
        "model_savings": model_savings,
        "feature_cols": feature_cols,
        "metrics": {
            "mae_expense": float(mae_exp),
            "mse_expense": float(mse_exp),
            "r2_expense": float(r2_exp),
            "mae_savings": float(mae_sav),
            "mse_savings": float(mse_sav),
            "r2_savings": float(r2_sav)
        }
    }
    
    with open(model_export_path, "wb") as f:
        pickle.dump(bundle, f)
        
    print(f"Successfully exported finance model bundle to '{model_export_path}'.")
    return bundle

if __name__ == "__main__":
    train_finance_model()
