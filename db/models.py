from sqlalchemy import (Column, Integer, String, Float, Date, ForeignKey,Boolean, DateTime,Text)

from datetime import datetime,timezone
# now importing object relational mapper from sqlalchemy
from sqlalchemy.orm import relationship

from db.database import Base

# Customers table

class Customer(Base):
    __tablename__ = "customers"

    customer_id = Column(Integer, primary_key=True, index=True)
    age = Column(Integer,nullable=False)
    employment_status = Column(String,nullable=False)
    employment_years = Column(Integer,nullable=False)
    annual_income = Column(Float,nullable=False)
    existing_debt = Column(Float,nullable=False)
    credit_score = Column(Integer,nullable=False)
    region = Column(String,nullable=False)
    signup_date = Column(Date,nullable=False)

    # Relationships
    loan_applications = relationship("LoanApplication", back_populates="customer")




# Loan Applications Table

class LoanApplication(Base):
    __tablename__ = "loan_applications"
    application_id =Column(Integer, primary_key=True, index=True)

    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable=False)
    application_date = Column(Date, nullable=False)
    requested_amount = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)
    interest_rate = Column(Float, nullable=False)
    model_risk_score = Column(Float, nullable=False)
    approval_threshold = Column(Float, nullable=False)
    approval_decision = Column(String, nullable=False)
    predicted_profit = Column(Float)
    predicted_loss = Column(Float)
    segment = Column(String)
    channel = Column(String)

    # Relationships
    customer = relationship("Customer", back_populates="loan_applications")
    loan = relationship("Loan", back_populates="application")


class Loan(Base):
    __tablename__ = "loans"
    loan_id = Column(Integer, primary_key=True, index=True)
    application_id = Column(Integer,ForeignKey("loan_applications.application_id"), nullable=False)
    approved_amount = Column(Float, nullable=False)
    disbursed_date = Column(Date, nullable=False)
    expected_total_return = Column(Float, nullable=False)
    loan_status = Column(String, nullable=False)


    # Relationships
    application = relationship("LoanApplication",back_populates = "loan")
    repayments = relationship("Repayments",back_populates="loan")

class Repayments(Base):
    __tablename__  = "repayments"

    repayment_id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.loan_id"), nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float)
    days_late = Column(Integer)
    payment_status = Column(String)
    # Relationships
    loan = relationship("Loan",back_populates="repayments")
    
    
class DecisionAuditLog(Base):
    __tablename__ = "decision_audit_logs"
    audit_id = Column(String,primary_key=True, index=True)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    model_name = Column(String)
    model_threshold = Column(Float)

    policy_version = Column(String)

    age = Column(Integer)
    annual_income = Column(Float)
    existing_debt = Column(Float)
    credit_score = Column(Integer)
    employment_status = Column(String)
    region = Column(String)
    segment = Column(String)
    channel = Column(String)

    requested_amount = Column(Float)
    loan_term_months = Column(Integer)
    interest_rate = Column(Float)

    is_secured = Column(Boolean)
    collateral_type = Column(String)
    collateral_value = Column(Float)
    collateral_coverage_ratio = Column(Float)

    raw_probability_of_default = Column(Float)
    adjusted_probability_of_default = Column(Float)
    loss_given_default = Column(Float)
    loss_given_default_percent = Column(Float)
    lgd_reason_code = Column(String)

    term_risk_multiplier = Column(Float)
    adjustment_reason_code = Column(String)

    expected_loss = Column(Float)
    expected_interest_income = Column(Float)
    risk_adjusted_income = Column(Float)
    cost_of_capital = Column(Float)
    risk_adjusted_net_profit = Column(Float)
    is_profitable = Column(Boolean)

    policy_status = Column(String)
    policy_passed = Column(Boolean)
    requires_manual_review = Column(Boolean)

    final_decision = Column(String)

    primary_reason_codes = Column(Text)
    rejection_reason_codes = Column(Text)
    review_reason_codes = Column(Text)
    passed_rules = Column(Text)
    evaluated_thresholds = Column(Text)
    