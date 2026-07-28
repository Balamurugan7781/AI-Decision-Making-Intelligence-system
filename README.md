# AI FinTech Decision Intelligence System

A production-style FinTech decision intelligence system for evaluating loan applications using credit-risk modelling, collateral-aware LGD logic, risk-adjusted financial evaluation, policy-as-code, FastAPI, audit logging, and portfolio analytics.

The project demonstrates how machine learning, deterministic business rules, and financial logic can be combined to support explainable and auditable lending decisions.

---

## 1. Project Overview

This project simulates how a fintech lender can evaluate loan applications beyond a simple machine-learning prediction.

Instead of only predicting whether a borrower may default, the system evaluates:

- Probability of Default (PD)
- Term-risk-adjusted PD
- Loss Given Default (LGD)
- Collateral coverage
- Expected loss
- Expected interest income
- Cost of capital
- Risk-adjusted net profit
- Credit policy rules
- Final decision reason codes
- Portfolio-level decision impact

The system produces one of three decisions:

```text
APPROVE
REVIEW
REJECT
```

The core lending decision is deterministic and auditable. Generative AI is planned as a future interface layer for querying and explaining verified outputs, not for making lending decisions directly.

---

## 2. Business Problem

Lending decisions require more than model accuracy.

A real decision process needs to answer:

- Is the applicant likely to default?
- Is the loan financially viable after expected loss?
- Is the loan compliant with credit policy?
- Is the loan secured or unsecured?
- How much collateral coverage exists?
- Why was the application approved, reviewed, or rejected?
- Can the decision be audited later?

This project addresses those questions through a modular decision-intelligence architecture.

---

## 3. High-Level Architecture

```text
Loan Application Input
        ↓
Feature Engineering
        ↓
Probability of Default Model
        ↓
Term-Risk Adjustment
        ↓
Collateral-Aware LGD Engine
        ↓
Financial Evaluation Engine
        ↓
Policy-as-Code Engine
        ↓
Decision Engine
        ↓
Decision Audit Logging
        ↓
Portfolio Analytics
        ↓
Future: LLM-to-SQL and RAG Explanation Layer
```

---

## 4. Current System Capabilities

### 4.1 Probability of Default Prediction

The system predicts the probability that a specific loan applicant may default.

```text
Raw PD = model-predicted probability of default
```

Example:

```text
Raw PD = 28.33%
```

The PD model is trained on synthetic lending data and used during real-time FastAPI evaluation.

---

### 4.2 Term-Risk Adjustment

Longer loan terms can increase uncertainty.  
The system applies a transparent term-risk multiplier to the raw PD.

Example:

```text
Raw PD = 28.33%
Term-risk multiplier = 1.15
Adjusted PD = 32.58%
```

The adjusted PD is used in financial evaluation and policy checks.

---

### 4.3 Collateral-Aware LGD Engine

The system supports both secured and unsecured loans.

Input fields:

```text
is_secured
collateral_type
collateral_value
```

The system calculates:

```text
Collateral Coverage Ratio = Collateral Value / Requested Loan Amount
```

LGD assumptions:

| Loan Condition | LGD | Reason Code |
|---|---:|---|
| Unsecured loan | 75% | `UNSECURED_LOAN_HIGH_LGD` |
| Fully collateralised loan | 30% | `FULLY_COLLATERALISED_LOW_LGD` |
| Partially collateralised loan | 45% | `PARTIALLY_COLLATERALISED_MODERATE_LGD` |
| Low collateral coverage | 60% | `LOW_COLLATERAL_COVERAGE_HIGH_LGD` |

This makes the expected-loss calculation more realistic than using one fixed LGD for every loan.

---

### 4.4 Financial Evaluation Engine

The financial engine calculates the risk-adjusted economics of a loan.

Core formulas:

```text
Expected Loss = PD × LGD × EAD
```

```text
Expected Interest Income = Loan Amount × Annual Interest Rate × Loan Term in Years
```

```text
Risk-Adjusted Income = Expected Interest Income × (1 - PD)
```

```text
Cost of Capital = Loan Amount × Cost of Capital Rate × Loan Term in Years
```

```text
Risk-Adjusted Net Profit = Risk-Adjusted Income - Expected Loss - Cost of Capital
```

Where:

```text
PD  = Probability of Default
LGD = Loss Given Default
EAD = Exposure at Default
```

The engine returns:

- Expected loss
- Expected interest income
- Risk-adjusted income
- Cost of capital
- Risk-adjusted net profit
- Profitability flag

---

### 4.5 Policy-as-Code Engine

Credit policy rules are stored as structured configuration instead of being hidden inside hard-coded logic.

The policy engine evaluates:

- Maximum PD for approval
- Manual review PD threshold
- Debt-to-income ratio
- Loan-to-income ratio
- Minimum credit score
- Minimum risk-adjusted net profit
- Expected-loss-to-income ratio

The policy engine returns:

- Policy status
- Passed rules
- Review reason codes
- Rejection reason codes
- Evaluated thresholds
- Policy version

---

### 4.6 Decision Engine

The final decision is based on:

- Adjusted PD
- Financial viability
- Policy rule outcomes

Possible decisions:

```text
APPROVE
REVIEW
REJECT
```

The decision engine produces machine-readable reason codes such as:

```text
PD_REQUIRES_MANUAL_REVIEW
NEGATIVE_RISK_ADJUSTED_NET_PROFIT
PD_ABOVE_MAXIMUM_POLICY_THRESHOLD
EXPECTED_LOSS_EXCEEDS_ALLOWED_INCOME_RATIO
```

---

### 4.7 Decision Audit Logging

Every evaluated loan application is stored in the `decision_audit_logs` table.

The audit record stores:

- Audit ID
- Timestamp
- Model name
- Model threshold
- Policy version
- Applicant details
- Loan details
- Collateral details
- Raw PD
- Adjusted PD
- Term-risk multiplier
- LGD
- LGD reason code
- Expected loss
- Expected interest income
- Risk-adjusted income
- Cost of capital
- Risk-adjusted net profit
- Policy status
- Final decision
- Primary reason codes
- Review reason codes
- Rejection reason codes
- Passed policy rules

This creates a traceable decision history for analytics, governance, and future LLM-to-SQL querying.

---

### 4.8 Portfolio Analytics

The analytics layer summarises decision audit records.

Current analytics include:

- Total decisions
- Approval count
- Review count
- Rejection count
- Approval rate
- Review rate
- Rejection rate
- Average raw PD
- Average adjusted PD
- Total expected loss
- Total expected interest income
- Total cost of capital
- Total risk-adjusted net profit
- Segment-level decision summary
- Top primary reason codes

Planned analytics upgrades:

- Secured vs unsecured summary
- Average LGD by collateral type
- Expected loss by collateral type
- Top LGD reason codes
- Risk-adjusted profitability by segment, region, and channel

---

## 5. FastAPI Endpoint

### POST `/evaluate-loan`

The endpoint accepts loan application details and returns a full decision result.

Example request:

```json
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
```

Example LGD output:

```json
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
```

---

## 6. Database Design

Main database tables:

```text
customers
loan_applications
loans
repayments
decision_audit_logs
```

The `decision_audit_logs` table is used to persist decision evidence for later review and analytics.

Important stored fields include:

```text
raw_probability_of_default
adjusted_probability_of_default
loss_given_default
lgd_reason_code
collateral_type
collateral_value
collateral_coverage_ratio
expected_loss
risk_adjusted_net_profit
policy_status
final_decision
primary_reason_codes
```

---

## 7. Project Structure

```text
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
```

---

## 8. Technology Stack

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn

### Data and Persistence

- SQLAlchemy
- SQLite
- Pandas

### Machine Learning

- Scikit-learn
- Logistic Regression baseline
- Model metadata

### Decision Intelligence

- Policy-as-code
- YAML configuration
- Reason codes
- Audit logging
- Portfolio analytics

### Planned Generative AI

- LLM-to-SQL
- RAG policy explanation
- LangChain tool orchestration
- Natural-language portfolio analytics

### Development Tools

- Git
- GitHub
- VS Code

---

## 9. How to Run Locally

Install dependencies:

```bash
pip install -r requirements.txt
```

Initialise the database:

```bash
python -m db.init_db
```

Run the FastAPI server:

```bash
python -m uvicorn app.main:app --reload
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Run portfolio analytics:

```bash
python -m analytics.decision_impact_analysis
```

---

## 10. Example Database Verification Query

After testing the API, verify saved audit records:

```bash
python -c "import sqlite3; conn=sqlite3.connect('data/business.db'); cur=conn.cursor(); cur.execute('SELECT final_decision, is_secured, collateral_type, collateral_value, collateral_coverage_ratio, loss_given_default, loss_given_default_percent, lgd_reason_code, expected_loss FROM decision_audit_logs ORDER BY created_at DESC LIMIT 10'); rows=cur.fetchall(); [print(row) for row in rows]; conn.close()"
```

Expected pattern:

```text
('REVIEW', 1, 'gold', 9000.0, 1.125, 0.3, 30.0, 'FULLY_COLLATERALISED_LOW_LGD', ...)
('REVIEW', 1, 'vehicle', 5000.0, 0.625, 0.45, 45.0, 'PARTIALLY_COLLATERALISED_MODERATE_LGD', ...)
('REVIEW', 0, 'none', 0.0, 0.0, 0.75, 75.0, 'UNSECURED_LOAN_HIGH_LGD', ...)
```

---

## 11. Development Roadmap

### Phase 1 — Data Foundation

- [x] Relational database design
- [x] SQLAlchemy ORM setup
- [x] Synthetic lending data generation
- [x] Customer, application, loan, and repayment tables

### Phase 2 — Machine Learning

- [x] Feature engineering
- [x] Baseline PD model
- [x] Prediction pipeline
- [x] Model metadata loading

### Phase 3 — Decision Intelligence

- [x] Financial evaluation engine
- [x] Expected loss calculation
- [x] Risk-adjusted income calculation
- [x] Cost of capital calculation
- [x] Policy-as-code engine
- [x] Deterministic decision engine
- [x] Reason codes

### Phase 4 — Risk Realism Upgrade

- [x] Term-risk adjustment
- [x] Collateral-aware LGD logic
- [x] Secured vs unsecured loan handling
- [x] LGD reason codes
- [x] LGD and collateral fields stored in audit logs

### Phase 5 — API and Auditability

- [x] FastAPI endpoint
- [x] Pydantic request validation
- [x] Decision audit record generation
- [x] Decision audit persistence
- [x] Database verification queries

### Phase 6 — Analytics

- [x] Portfolio decision summary
- [x] Decision breakdown
- [x] Segment-level summary
- [x] Top primary reason codes
- [ ] Secured vs unsecured summary
- [ ] Collateral-type risk analysis
- [ ] LGD reason-code analytics

### Phase 7 — Generative AI

- [ ] LLM-to-SQL endpoint
- [ ] Natural-language portfolio querying
- [ ] SQL validation and safety layer
- [ ] RAG-supported policy explanation
- [ ] LangChain tool orchestration

### Phase 8 — Production Readiness

- [ ] Unit tests
- [ ] API tests
- [ ] Dockerisation
- [ ] Logging layer
- [ ] Environment configuration
- [ ] CI/CD workflow
- [ ] PostgreSQL migration option

---

## 12. Key Design Principle

The system separates prediction, financial evaluation, policy enforcement, and explanation.

```text
ML model
    → predicts Probability of Default

Risk adjustment
    → adjusts PD for term risk

LGD engine
    → estimates loss severity using collateral

Financial engine
    → calculates expected loss and profitability

Policy-as-code
    → applies approved lending rules

Decision engine
    → generates approve, review, or reject outcome

Audit layer
    → stores traceable decision evidence

Future GenAI layer
    → queries and explains verified outputs
```

Generative AI is planned as an interface and explanation layer, not as the authority making lending decisions.

---

## 13. Current Project Status

Active development.

Current completed milestone:

```text
Collateral-aware LGD audit logging has been implemented and verified.
```

Current focus:

```text
Expanding portfolio analytics to analyse secured vs unsecured lending risk, collateral type, LGD reason codes, and expected loss by collateral category.
```

Next planned implementation:

```text
LLM-to-SQL endpoint for natural-language querying over stored decision audit records.
```

---

## 14. Important Disclaimer

This project uses synthetic data and simplified financial assumptions.

It is intended as a portfolio demonstration of AI system design, credit-risk reasoning, auditability, and decision-intelligence architecture.

It should not be used for real lending decisions without proper validation, regulatory review, production-grade model governance, and domain-expert approval.

---

## 15. Author

**Balamurugan Purushothaman**

AI Engineer | Decision Intelligence Systems | FinTech Analytics