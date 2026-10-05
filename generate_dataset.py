import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_financial_dataset(n_days=1200, output_path="financial_forecasting_dataset.csv"):
    """
    Generates a realistic multi-year daily financial dataset for time-series forecasting,
    budget analytics, and risk management.
    """
    np.random.seed(42)
    
    # 1200+ days (over 3.2 years of continuous daily data)
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    records = []
    cumulative_savings = 50000.0  # Starting balance/savings
    
    # Monthly base salary range with annual increments
    base_salary = 60000.0
    
    for i, d in enumerate(dates):
        # Annual increment of 8% every 365 days
        annual_growth = (1.08 ** (i // 365))
        current_salary = base_salary * annual_growth
        
        day_name = d.strftime("%A")
        month_name = d.strftime("%B")
        is_weekend = int(day_name in ["Saturday", "Sunday"])
        is_payday = int(d.day in [1, 15])  # Semi-monthly payroll
        
        # 1. Income Generation (Salary + Freelance / Bonuses / Investments)
        income = 0.0
        if is_payday:
            income += np.random.normal(current_salary / 2, 800)
        
        # Occasional freelance / dividend / reimbursement income
        if np.random.rand() < 0.08:
            income += np.random.uniform(2000, 10000)
            
        income = round(max(0.0, income), 2)
        
        # 2. Food Expense (Baseline + Weekend Dining spikes + Inflation)
        food_base = np.random.normal(350, 60) * (1.35 if is_weekend else 1.0) * annual_growth
        # Occasional fine dining / family dinner
        if np.random.rand() < 0.05:
            food_base += np.random.uniform(800, 2000)
        food_expense = round(max(100.0, food_base), 2)
        
        # 3. Health Expense (Pharmacy, Consultations, Occasional Hospital/Dental)
        health_prob = np.random.rand()
        if health_prob < 0.82:
            health_expense = 0.0  # Most days 0 health expense
        elif health_prob < 0.94:
            health_expense = round(np.random.uniform(150, 600), 2) # Routine pharmacy
        elif health_prob < 0.985:
            health_expense = round(np.random.uniform(1200, 3500), 2) # Specialist visit / tests
        else:
            health_expense = round(np.random.uniform(5000, 18000), 2) # Medical emergency / procedure
            
        # 4. Travel Expense (Commute, Fuel, Public Transit, Weekend Getaways)
        if is_weekend:
            travel_expense = np.random.choice([0, np.random.uniform(100, 400), np.random.uniform(1000, 3500)], p=[0.4, 0.45, 0.15])
        else:
            travel_expense = np.random.normal(180, 40) # Daily work commute / fuel
        travel_expense = round(max(0.0, travel_expense), 2)
        
        # 5. Other Expenses (Utilities, Shopping, Subscriptions, Household, Leisure)
        other_base = np.random.uniform(50, 300)
        # End of month utility bills (electricity, internet, rent support)
        if d.day in [28, 29, 30, 31]:
            other_base += np.random.uniform(1500, 5000)
        # Occasional electronics / apparel shopping
        if np.random.rand() < 0.06:
            other_base += np.random.uniform(1500, 8000)
        other_expense = round(max(20.0, other_base), 2)
        
        # 6. Aggregates & Financial Indicators
        total_expense = round(food_expense + health_expense + travel_expense + other_expense, 2)
        savings = round(income - total_expense, 2)
        cumulative_savings = round(cumulative_savings + savings, 2)
        
        # Risk classification for the day
        if total_expense > 8000 or (income == 0 and total_expense > 3500):
            risk_level = "High"
        elif total_expense > 3000 or (income == 0 and total_expense > 1500):
            risk_level = "Medium"
        else:
            risk_level = "Low"
            
        records.append({
            "Date": d.strftime("%Y-%m-%d"),
            "Day": day_name,
            "Month": month_name,
            "Year": d.year,
            "Is_Weekend": is_weekend,
            "Income": income,
            "Food_Expense": food_expense,
            "Health_Expense": health_expense,
            "Travel_Expense": travel_expense,
            "Other_Expense": other_expense,
            "Total_Expense": total_expense,
            "Savings": savings,
            "Cumulative_Savings": cumulative_savings,
            "Risk_Level": risk_level
        })
        
    df = pd.DataFrame(records)
    
    # 7. Time-Series & Forecasting Engineered Features
    df["Rolling_7Day_Total_Expense_Avg"] = df["Total_Expense"].rolling(window=7, min_periods=1).mean().round(2)
    df["Rolling_30Day_Total_Expense_Avg"] = df["Total_Expense"].rolling(window=30, min_periods=1).mean().round(2)
    df["Rolling_7Day_Savings_Avg"] = df["Savings"].rolling(window=7, min_periods=1).mean().round(2)
    df["Lag_1Day_Expense"] = df["Total_Expense"].shift(1).fillna(df["Total_Expense"].iloc[0]).round(2)
    df["Lag_7Day_Expense"] = df["Total_Expense"].shift(7).fillna(df["Total_Expense"].iloc[0]).round(2)
    df["Expense_To_Income_Ratio"] = np.where(df["Income"] > 0, (df["Total_Expense"] / df["Income"]).round(4), 0.0)
    
    # Target Ground Truth for ML: Next 7 Days Total Expense (Lead/Forecast target)
    df["Target_Next_7Day_Total_Expense"] = df["Total_Expense"].shift(-7).fillna(df["Total_Expense"].mean()).round(2)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Successfully generated {len(df)} rows and {len(df.columns)} columns in '{output_path}'.")
    print("\nDataset Summary Preview:")
    print(df.head(5)[["Date", "Day", "Income", "Food_Expense", "Health_Expense", "Travel_Expense", "Other_Expense", "Total_Expense", "Savings"]])
    return df

if __name__ == "__main__":
    generate_financial_dataset(n_days=1200, output_path="financial_forecasting_dataset.csv")
