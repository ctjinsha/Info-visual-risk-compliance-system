# OptimaTrack — Visual Risk & Compliance Intelligence System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)](https://flask.palletsprojects.com/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML--Enabled-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20PostgreSQL-indigo.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)](#license)

**OptimaTrack (Info-Visual-Risk-System)** is an enterprise-grade behavioral, financial, and compliance intelligence platform. It fuses machine learning forecasting, multi-scenario simulation engines, audit trail monitoring, and interactive visual dashboards to provide actionable risk mitigation and personal/institutional compliance management.

---

## 📑 Table of Contents

- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Directory Structure](#-directory-structure)
- [Installation & Getting Started](#-installation--getting-started)
- [Data Seeding & ML Model Training](#-data-seeding--ml-model-training)
- [Demo Credentials](#-demo-credentials)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Security & Audit Logging](#-security--audit-logging)
- [License](#-license)

---

## 🚀 Key Features

### 1. 📊 Executive Visual Risk Dashboard (`/`)
- Unified KPI matrix tracking compliance scores, goal performance, and active streak metrics.
- Dynamic visual widgets for instantaneous health assessment across financial, academic, and behavioral verticals.
- Actionable task recommendations and real-time alert notifications.

### 2. 💰 Financial Intelligence & Forecasting (`/finance`)
- **Multi-Category Tracking**: Manage Savings, Income, and Expenses with target dates and budget milestones.
- **Daily Financial Records**: Granular daily spending tracking with category breakdown and historical audit trail.
- **ML Predictive Modeling (`finance_model.py`)**: Trained regression algorithms forecasting risk zones, savings shortfall risks, and future trajectory projections.

### 3. 📚 Study & Academic Performance Engine (`/study`)
- Record study hours, subject distribution, focus ratings (1–100), and pedagogical methods (Revision, Theory, Practice, Problem Solving).
- **ML Study Predictor (`study_model.py`)**: Machine learning engine evaluating learning efficiency, cognitive retention factors, and target completion probabilities.

### 4. ⚡ Habit & Behavioral Analytics (`/habit`)
- Daily habit routine verification, streak stability, and productivity score mapping.
- **Behavioral Risk Classifier (`habit_model.py`)**: Identifies drop-off risk factors and triggers automated corrective recommendations.

### 5. 🧪 Multi-Section "What-If" Simulation Engine (`/milestone3`)
- Cross-domain simulation framework enabling stress-testing under custom scenarios (e.g., spending spikes, study drops, habit lapses).
- Calculates multi-metric resilience score and displays comparative pre/post simulation delta charts.

### 6. 🤖 Interactive Enterprise AI Copilot (`/chat`)
- Context-aware intelligence assistant capable of querying real-time system metrics, user history, and compliance alerts.
- Provides immediate mitigation playbooks and strategic decision support.

### 7. 🛡️ Audit Trail & Security Management (`/history`, `/profile`)
- Comprehensive audit terminal recording every user action with IP address, HTTP method, route, and status code.
- Profile customization, password security, and automated alert resolution.

---

## 🏛 System Architecture

```mermaid
flowchart TD
    subgraph UI ["Modern Glassmorphism UI (Jinja2 + Vanilla CSS)"]
        A[Executive Dashboard]
        B[Finance Module]
        C[Study Engine]
        D[Habits & Routines]
        E[Simulation Engine]
        F[AI Assistant Chat]
    end

    subgraph Backend ["Flask Application Server (app.py)"]
        G[Authentication & Session Guard]
        H[REST API & CRUD Controllers]
        I[Audit Logging Middleware]
    end

    subgraph Intelligence ["ML & Analytics Layer (intelligence_engine.py)"]
        J[FinancialForecastingEngine]
        K[HabitProductivityAnalyticsEngine]
        L[WhatIfSimulationEngine]
        M[PredictiveAnalyticsEngine]
        N[AIRecommendationEngine]
    end

    subgraph ML_Models ["Trained ML Artifacts (.pkl)"]
        O[finance_model.pkl]
        P[habit_model.pkl]
        Q[study_model.pkl]
    end

    subgraph Persistence ["Data Layer (models.py)"]
        R[(SQLite / PostgreSQL)]
    end

    UI --> Backend
    Backend --> Intelligence
    Backend --> Persistence
    Intelligence --> ML_Models
    Intelligence --> Persistence
    Backend --> I
    I --> Persistence
```

---

## 🛠 Tech Stack

- **Backend**: Python 3.10+, Flask 3.1, Jinja2, Werkzeug
- **Database & ORM**: SQLAlchemy 2.0, Flask-SQLAlchemy, SQLite (default) / PostgreSQL (`psycopg2-binary`)
- **Data Science & ML**: Scikit-Learn, Pandas, NumPy
- **Frontend**: Vanilla CSS, Modern Responsive Glassmorphism Design, Micro-animations, Google Fonts
- **Environment & Config**: `python-dotenv`, `dataclasses`, `pickle`

---

## 📂 Directory Structure

```text
Info-visual-risk-system/
├── app.py                         # Main Flask application and API route controllers
├── models.py                      # SQLAlchemy ORM database models
├── extensions.py                  # SQLAlchemy db instance initialization
├── intelligence_engine.py         # Core analytical and simulation algorithms
├── requirements.txt               # Project Python dependencies
├── seed.py                        # Database seeder with comprehensive demo datasets
├── setup_db.py                    # Database schema creation script
│
├── finance_model.py               # Financial ML model training and inference
├── habit_model.py                 # Habit ML model training and inference
├── study_model.py                 # Study ML model training and inference
├── generate_dataset.py            # Synthetic dataset generator for ML pipelines
│
├── *.csv                          # Datasets for finance, study, and habit modeling
├── *.pkl                          # Serialized trained scikit-learn models
│
├── templates/                     # Frontend HTML/Jinja2 templates
│   ├── index.html                 # Executive Dashboard
│   ├── finance.html               # Financial tracking & forecasting
│   ├── study.html                 # Study analytics & target tracker
│   ├── habit.html                 # Habit & behavioral monitor
│   ├── milestone3.html            # Scenario simulations & compliance
│   ├── chat.html                  # AI Copilot assistant interface
│   ├── history.html               # Audit logs & event timeline
│   ├── login.html                 # Authentication portal
│   └── profile.html               # User profile management
│
├── static/                        # CSS styles, JavaScript, and user uploads
└── tests/                         # Integration and unit test suites
```

---

## ⚙️ Installation & Getting Started

### 1. Prerequisites
- Python 3.10 or higher installed.
- Git installed.

### 2. Clone the Repository
```bash
git clone https://github.com/ctjinsha/Info-visual-risk-compliance-system.git
cd Info-visual-risk-system
```

### 3. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows (Command Prompt)
python -m venv venv
.\venv\Scripts\activate.bat

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Create a `.env` file in the root directory (optional, defaults provided):
```env
SECRET_KEY=optimatrack_super_secret_key_2026
DATABASE_URL=sqlite:///optimatrack.db
# Or PostgreSQL: postgresql://username:password@localhost:5432/optimatrack
```

### 6. Initialize Database & Seed Data
```bash
python setup_db.py
python seed.py
```

### 7. Run the Application
```bash
python app.py
```
Open your browser and navigate to **`http://127.0.0.1:5000`**.

---

## 🤖 Data Seeding & ML Model Training

To retrain the predictive machine learning models or generate fresh synthetic datasets:

```bash
# Generate baseline training data
python generate_dataset.py

# Train individual ML models
python finance_model.py
python habit_model.py
python study_model.py
```

---

## 🔑 Demo Credentials

After running `python seed.py`, the following demo accounts are available:

| Email | Password | Role | Description |
|---|---|---|---|
| `shreya@optimatrack.com` | `password123` | Risk & Compliance Lead | Fully populated financial, study, and habit records |
| `ctjinshamol@gmail.com` | `password123` | Visual Risk Engineer | Admin privileges, benchmark data & simulations |

---

## 🧪 Testing & Quality Assurance

Run the automated test suites to verify CRUD operations, multi-section simulation integrity, and ML inference:

```bash
python test_sections_crud.py
python test_simulation_multisection.py
python test_milestone3.py
```

---

## 🛡️ Security & Audit Logging

- **Zero-Trust Audit Logging**: Every mutation, data entry, and view route is logged into the `AuditLog` table with timestamp, user ID, IP address, and response code.
- **Password Hashing**: Secure salted SHA-256 password hashing powered by Werkzeug.
- **SQL Injection & XSS Protection**: Parameterized queries via SQLAlchemy ORM and automatic context-aware escaping via Jinja2.

---

## 📄 License

This project is licensed under the **MIT License**. Feel free to use, modify, and distribute for academic and professional applications.
