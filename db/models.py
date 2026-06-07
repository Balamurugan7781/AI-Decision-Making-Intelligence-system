from sqlalchemy import (Column, Integer, String, Float, Date, ForeignKey)

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
    
    
