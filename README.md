# AI FinTech Decision Intelligence System

An end-to-end FinTech Decision Intelligence platform that combines credit-risk modelling, risk-adjusted financial evaluation, policy-as-code, collateral-aware LGD logic, FastAPI, audit logging, portfolio analytics, and planned Generative AI capabilities to support lending decisions and portfolio monitoring.

This project is designed to demonstrate how AI can support lending decisions in a controlled, explainable, and auditable way.

---

## Project Overview

This project simulates how modern fintech lenders evaluate loan applications, assess credit risk, calculate risk-adjusted profitability, apply lending policy rules, store decision audit records, and generate portfolio-level insights.

The system is not designed as a simple loan approval classifier.

Instead, it combines:

- Probability of Default prediction
- Term-risk adjustment
- Collateral-aware Loss Given Default calculation
- Expected loss modelling
- Risk-adjusted income calculation
- Cost of capital
- Policy-as-code checks
- Deterministic decision logic
- Decision audit logging
- Portfolio analytics
- Planned LLM-to-SQL and RAG-supported explanations

The project follows a modular architecture to separate machine learning, financial logic, policy rules, decisioning, audit persistence, analytics, and future Generative AI layers.

---

## Current Features

### 1. Database Layer

- SQLAlchemy ORM implementation
- SQLite database for local development
- Relational lending data model
- Customer management
- Loan application management
- Loan tracking
- Repayment tracking
- Decision audit log table

Main database entities:

- `customers`
- `loan_applications`
- `loans`
- `repayments`
- `decision_audit_logs`

---

### 2. Synthetic Data Generation

The system includes synthetic lending data generation for:

- Customer demographics
- Employment profiles
- Income and debt characteristics
- Credit scores
- Loan applications
- Loan approval/rejection outcomes
- Repayment behaviour
- Default scenarios

This allows the project to simulate lending workflows without using sensitive real customer data.

---

### 3. Probability of Default Prediction

The system predicts application-level Probability of Default.

PD represents the estimated probability that a specific loan applicant may default.

Current workflow:

```text
Application Data
      ↓
Feature Engineering
      ↓
PD Model
      ↓
Raw Probability of Default 
```

Example:

Raw PD = 28.33%

The PD output is then passed into the risk-adjustment and financial evaluation layers.

4. Term-Risk Adjustment

Longer loan terms can create additional uncertainty.

The system applies a transparent term-risk adjustment to the raw PD.

Example:

Raw PD = 28.33%
Term-risk multiplier = 1.15
Adjusted PD = 32.58%

This makes the system more conservative for longer-duration loans.

5. Collateral-Aware LGD Engine

The project now supports secured and unsecured loans.

Collateral details are accepted through the FastAPI endpoint:

is_secured
collateral_type
collateral_value

The system calculates:

Collateral Coverage Ratio = Collateral Value / Requested Amount

Then it estimates Loss Given Default based on collateral coverage.

Loan Type	LGD Assumption	Reason Code
Unsecured loan	75%	UNSECURED_LOAN_HIGH_LGD
Fully secured loan	30%	FULLY_COLLATERALISED_LOW_LGD
Partially secured loan	45%	PARTIALLY_COLLATERALISED_MODERATE_LGD
Low collateral coverage	60%	LOW_COLLATERAL_COVERAGE_HIGH_LGD

This improves the realism of expected-loss calculation because unsecured and secured loans should not carry the same loss assumption.

6. Financial Evaluation Engine

The financial engine calculates the expected financial outcome of a loan using adjusted PD and LGD.

Core formulas:

Expected Loss = PD × LGD × EAD

Expected Interest Income = Loan Amount × Annual Interest Rate × Loan Term in Years

Risk-Adjusted Income = Expected Interest Income × (1 - PD)

Cost of Capital = Loan Amount × Cost of Capital Rate × Loan Term in Years

Risk-Adjusted Net Profit = Risk-Adjusted Income - Expected Loss - Cost of Capital

Where:

PD  = Probability of Default
LGD = Loss Given Default
EAD = Exposure at Default

The financial engine returns:

Expected loss
Expected interest income
Risk-adjusted income
Cost of capital
Risk-adjusted net profit
Profitability flag
7. Policy-as-Code Engine

The system uses structured policy configuration to apply lending rules.

The policy layer evaluates:

Maximum PD for approval
Manual review PD threshold
Debt-to-income ratio
Loan-to-income ratio
Minimum credit score
Minimum risk-adjusted net profit
Expected-loss-to-income ratio

The policy engine returns:

Policy status
Passed rules
Review reason codes
Rejection reason codes
Evaluated thresholds
Policy version

This makes the lending logic more auditable and maintainable than hard-coded conditions.

8. Decision Engine

The decision engine combines:

Adjusted PD
Financial evaluation result
Policy result

It returns one of three outcomes:

APPROVE
REVIEW
REJECT

The decision is deterministic and produces primary reason codes.

Example reason codes:

PD_REQUIRES_MANUAL_REVIEW
NEGATIVE_RISK_ADJUSTED_NET_PROFIT
PD_ABOVE_MAXIMUM_POLICY_THRESHOLD
EXPECTED_LOSS_EXCEEDS_ALLOWED_INCOME_RATIO

The LLM does not make lending decisions.
The core decision pipeline remains deterministic, testable, and auditable.

9. FastAPI Endpoint

The project includes a FastAPI backend for real-time loan evaluation.

Main endpoint:

POST /evaluate-loan

Example request:

{
  "age": 42,
  "annual_income": 120000,
  "existing_debt": 5000,
  "credit_score": 790,
  "requested_amount": 8000,
  "loan_term_months": 60,
  "interest_rate": 0.15,
  "is_secured": true,
  "collateral_type": "gold",
  "collateral_value": 9000,
  "employment_status": "employed",
  "region": "London",
  "segment": "prime",
  "channel": "web"
}

Example LGD result:

{
  "is_secured": true,
  "loss_given_default": 0.3,
  "loss_given_default_percent": 30.0,
  "collateral_coverage_ratio": 1.125,
  "collateral_coverage_percent": 112.5,
  "lgd_reason_code": "FULLY_COLLATERALISED_LOW_LGD",
  "collateral_type": "gold",
  "collateral_value": 9000
}
10. Decision Audit Logging

Every loan evaluation is stored in the database for traceability.

The audit table stores:

Audit ID
Created timestamp
Model name
Model threshold
Policy version
Applicant details
Loan details
Collateral details
Raw PD
Adjusted PD
Term-risk multiplier
LGD
LGD reason code
Expected loss
Expected interest income
Risk-adjusted income
Cost of capital
Risk-adjusted net profit
Policy status
Final decision
Primary reason codes
Rejection reason codes
Review reason codes
Passed policy rules
Evaluated thresholds

This enables governance, explainability, and future LLM-to-SQL analytics.

11. Portfolio Analytics

The analytics layer summarises stored decision records.

Current outputs include:

Total decisions
Approval count
Review count
Rejection count
Approval rate
Review rate
Rejection rate
Average raw PD
Average adjusted PD
Total expected loss
Total expected interest income
Total cost of capital
Total risk-adjusted net profit
Segment-level summary
Top primary reason codes

Planned analytics upgrades:

Secured vs unsecured summary
Average LGD by collateral type
Expected loss by collateral type
Top LGD reason codes
Risk-adjusted profitability by segment
Decision distribution by region and channel
Current Architecture
flowchart TD

    A[Loan Application Input]
    B[Feature Engineering]
    C[PD Model Prediction]
    D[Term Risk Adjustment]
    E[Collateral-Aware LGD Engine]
    F[Financial Evaluation Engine]
    G[Policy-as-Code Engine]
    H[Decision Engine]
    I[Decision Audit Logging]
    J[(SQLite / SQLAlchemy Database)]
    K[Portfolio Analytics]
    L[LLM-to-SQL - Planned]
    M[RAG Policy Explanation - Planned]

    A --> B
    B --> C
    C --> D
    A --> E
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
    J --> L
    M --> L
Folder Structure
AI-FinTech-Decision-Intelligence-System/
│
├── analytics/
│   ├── __init__.py
│   ├── portfolio_analysis.py
│   └── decision_impact_analysis.py
│
├── app/
│   ├── __init__.py
│   └── main.py
│
├── core/
│   ├── __init__.py
│   ├── audit_repository.py
│   ├── decision.py
│   ├── decision_audit.py
│   ├── financial_engine.py
│   ├── lgd_logic_engine.py
│   ├── policy_engine.py
│   └── risk_adjustment.py
│
├── db/
│   ├── __init__.py
│   ├── database.py
│   ├── init_db.py
│   └── models.py
│
├── ml/
│   ├── __init__.py
│   ├── features.py
│   ├── predict.py
│   └── train.py
│
├── policies/
│   └── credit_policy.yaml
│
├── data/
│   └── business.db
│
├── requirements.txt
├── README.md
└── .gitignore
Technology Stack
Backend
Python
FastAPI
Pydantic
Uvicorn
Data & Persistence
SQLAlchemy
SQLite
Pandas
Machine Learning
Scikit-learn
Logistic Regression baseline
Model metadata
Decision Intelligence
Policy-as-code
YAML configuration
Reason codes
Audit logging
Portfolio analytics
Planned AI Capabilities
LLM-to-SQL
RAG policy explanation
LangChain orchestration
Natural-language business insights
Development Tools
Git
GitHub
VS Code
How to Run the Project

Install dependencies:

pip install -r requirements.txt

Initialise the database:

python -m db.init_db

Run the FastAPI server:

python -m uvicorn app.main:app --reload

Open Swagger UI:

http://127.0.0.1:8000/docs

Run portfolio analytics:

python -m analytics.decision_impact_analysis
Development Roadmap
Phase 1 — Data Foundation
 Database design
 SQLAlchemy ORM
 Synthetic data generation
 Customer, loan, repayment schema
Phase 2 — Machine Learning
 Feature engineering for PD model
 Baseline PD model
 Prediction pipeline
 Model metadata loading
Phase 3 — Decision Intelligence
 Financial evaluation engine
 Expected loss calculation
 Risk-adjusted income calculation
 Cost of capital calculation
 Policy-as-code engine
 Decision engine
 Reason codes
Phase 4 — Risk Realism Upgrade
 Term-risk adjustment
 Collateral-aware LGD logic
 Secured vs unsecured loan handling
 LGD reason codes
 LGD fields persisted in audit logs
Phase 5 — API and Auditability
 FastAPI endpoint
 Pydantic request validation
 Decision audit record generation
 Decision audit persistence
 Database verification queries
Phase 6 — Analytics
 Portfolio decision summary
 Decision breakdown
 Segment-level summary
 Top primary reason codes
 Secured vs unsecured summary
 Collateral-type risk analysis
 LGD reason-code analytics
Phase 7 — Generative AI
 LLM-to-SQL endpoint
 Natural-language portfolio querying
 SQL validation and safety layer
 RAG-supported policy explanation
 LangChain tool orchestration
Phase 8 — Production Readiness
 Unit tests
 API tests
 Dockerisation
 Logging layer
 Environment configuration
 CI/CD workflow
 PostgreSQL migration option
Business Objective

The objective of this project is to demonstrate how credit-risk modelling, financial reasoning, policy governance, and AI-powered analytics can be combined to support:

Credit risk assessment
Loan approval strategy
Risk-adjusted lending decisions
Portfolio monitoring
Explainable AI in financial services
Decision auditability
Responsible use of AI in lending workflows
Important Design Principle

The system deliberately separates deterministic decision logic from Generative AI.

ML model
→ predicts Probability of Default

Financial engine
→ calculates expected loss and risk-adjusted profitability

Policy-as-code
→ applies approved lending rules

Decision engine
→ produces approve, review, or reject outcome

Audit layer
→ stores traceable decision evidence

LLM-to-SQL and RAG
→ planned for querying and explaining verified outputs

Generative AI is planned as an interface and explanation layer, not as the authority making lending decisions.

Project Status

Active development.

Current completed milestone:

Collateral-aware LGD audit logging has been implemented and verified.

Current focus:

Expanding portfolio analytics to analyse secured vs unsecured lending risk, collateral type, LGD reason codes, and expected loss by collateral category.

Next planned implementation:

LLM-to-SQL endpoint for natural-language querying over stored decision audit records.
Author

Balamurugan Purushothaman

AI Engineer | Decision Intelligence Systems | FinTech Analytics