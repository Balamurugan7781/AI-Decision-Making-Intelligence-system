from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random

from db.database import SessionLocal
from db.models import Customer, LoanApplication, Loan, Repayments

# ======================================================
# CONFIGURATION
# ======================================================

NUM_CUSTOMERS = 1000
MAX_APPLICATIONS_PER_CUSTOMER = 3

regions = [
    "London",
    "Manchester",
    "Birmingham",
    "Leeds",
    "Liverpool"
]

employment_statuses = [
    "employed",
    "self-employed",
    "unemployed"
]

segments = [
    "prime",
    "near_prime",
    "subprime"
]

channels = [
    "mobile_app",
    "web",
    "branch"
]

# ======================================================
# CREATE DATABASE SESSION
# ======================================================

db: Session = SessionLocal()

# ======================================================
# MAIN EXECUTION
# ======================================================

try:

    print("Starting synthetic data generation...")

    # ==================================================
    # GENERATE CUSTOMERS
    # ==================================================

    customers = []

    for _ in range(NUM_CUSTOMERS):

        employment_status = random.choice(employment_statuses)

        # ----------------------------------------------
        # EMPLOYMENT YEARS
        # ----------------------------------------------

        if employment_status == "unemployed":
            employment_years = 0

        else:
            employment_years = random.randint(1, 20)

        # ----------------------------------------------
        # CREDIT SCORE
        # ----------------------------------------------

        credit_score = random.randint(520, 850)

        # ----------------------------------------------
        # ANNUAL INCOME
        # ----------------------------------------------

        annual_income = random.randint(20000, 150000)

        # ----------------------------------------------
        # EXISTING DEBT
        # ----------------------------------------------

        existing_debt = round(random.uniform(0, annual_income * 0.7),2)

        customer = Customer(

            age=random.randint(21, 65),

            employment_status=employment_status,

            employment_years=employment_years,

            annual_income=annual_income,

            existing_debt=existing_debt,

            credit_score=credit_score,

            region=random.choice(regions),

            signup_date=(
                datetime.now() - timedelta(
                    days=random.randint(100, 2000)
                )
            ).date()
        )

        customers.append(customer)

    # ==================================================
    # INSERT CUSTOMERS
    # ==================================================

    db.add_all(customers)

    db.commit()

    print(f"{NUM_CUSTOMERS} customers inserted successfully.")

    # ==================================================
    # FETCH CUSTOMERS
    # ==================================================

    customers = db.query(Customer).all()

    print(f"Fetched {len(customers)} customers.")

    # ==================================================
    # GENERATE LOAN APPLICATIONS
    # ==================================================

    for customer in customers:

        num_applications = random.randint(
            1,
            MAX_APPLICATIONS_PER_CUSTOMER
        )

        for _ in range(num_applications):

            # ------------------------------------------
            # LOAN DETAILS
            # ------------------------------------------

            requested_amount = random.randint(
                2000,
                30000
            )

            loan_term_months = random.choice(
                [12, 24, 36]
            )

            interest_rate = round(
                random.uniform(5, 18),
                2
            )

            # ------------------------------------------
            # DERIVED FINANCIAL FEATURES
            # ------------------------------------------

            debt_to_income_ratio = round(
                customer.existing_debt /
                customer.annual_income,
                3
            )

            loan_to_income_ratio = round(
                requested_amount /
                customer.annual_income,
                3
            )

            # ------------------------------------------
            # DEFAULT PROBABILITY
            # ------------------------------------------

            default_probability = (

                ((850 - customer.credit_score) / 850) * 0.5

                +

                (debt_to_income_ratio * 0.3)

                +

                (loan_to_income_ratio * 0.2)

            )

            default_probability = round(
                min(max(default_probability, 0.01), 0.95),
                3
            )
            # model_risk_score = default_probability

            # ------------------------------------------
            # APPROVAL DECISION
            # ------------------------------------------

            approval_decision = (

                "approved"

                if default_probability < 0.35

                else "rejected"
            )

            # ------------------------------------------
            # PROFIT / LOSS ESTIMATION
            # ------------------------------------------

            predicted_loss = round(
                requested_amount *
                default_probability,
                2
            )

            predicted_profit = round(
                (
                    requested_amount *
                    interest_rate / 100
                ) - predicted_loss,
                2
            )

            # ------------------------------------------
            # CREATE LOAN APPLICATION
            # ------------------------------------------

            application = LoanApplication(

                customer_id=customer.customer_id,

                application_date=(
                    datetime.now() - timedelta(
                        days=random.randint(0, 365)
                    )
                ).date(),

                requested_amount=requested_amount,

                loan_term_months=loan_term_months,

                interest_rate=interest_rate,
                
                model_risk_score=default_probability,

                approval_threshold=0.35,

                approval_decision=approval_decision,

                predicted_profit=predicted_profit,

                predicted_loss=predicted_loss,

                segment=random.choice(segments),

                channel=random.choice(channels)
            )

            db.add(application)

            db.commit()

            db.refresh(application)

            # ------------------------------------------
            # CREATE LOAN IF APPROVED
            # ------------------------------------------

            if approval_decision == "approved":

                # --------------------------------------
                # LOAN STATUS
                # --------------------------------------

                if default_probability > 0.5:

                    loan_status = random.choices(
                        ["active", "defaulted"],
                        weights=[0.3, 0.7]
                    )[0]

                else:

                    loan_status = random.choices(
                        ["active", "completed"],
                        weights=[0.7, 0.3]
                    )[0]

                # --------------------------------------
                # EXPECTED RETURN
                # --------------------------------------

                expected_total_return = round(
                    requested_amount *
                    (1 + interest_rate / 100),
                    2
                )

                # --------------------------------------
                # CREATE LOAN
                # --------------------------------------

                loan = Loan(

                    application_id=application.application_id,

                    approved_amount=requested_amount,

                    disbursed_date=(
                        application.application_date
                        + timedelta(days=2)
                    ),

                    expected_total_return=expected_total_return,

                    loan_status=loan_status
                )

                db.add(loan)

                db.commit()

                db.refresh(loan)

                # --------------------------------------
                # MONTHLY REPAYMENTS
                # --------------------------------------

                monthly_due = round(
                    expected_total_return /
                    loan_term_months,
                    2
                )

                for month in range(loan_term_months):

                    due_date = (

                        loan.disbursed_date
                        + timedelta(days=30 * month)
                    )

                    # ----------------------------------
                    # DEFAULT BEHAVIOUR
                    # ----------------------------------

                    if (
                        loan_status == "defaulted"
                        and month > loan_term_months * 0.5
                    ):

                        amount_paid = 0

                        paid_date = None

                        days_late = None

                    else:

                        delay_days = random.randint(0, 10)

                        paid_date = (
                            due_date
                            + timedelta(days=delay_days)
                        )

                        amount_paid = monthly_due

                        days_late = delay_days

                    repayment = Repayments(

                        loan_id=loan.loan_id,

                        due_date=due_date,

                        paid_date=paid_date,

                        amount_due=monthly_due,

                        amount_paid=amount_paid,

                        days_late=days_late
                    )

                    db.add(repayment)

                db.commit()

    # ==================================================
    # SUCCESS MESSAGE
    # ==================================================

    print("Synthetic fintech dataset generated successfully.")

# ======================================================
# ERROR HANDLING
# ======================================================

except Exception as e:

    print("\nERROR OCCURRED:")
    print(e)

# ======================================================
# CLOSE DATABASE
# ======================================================

finally:

    db.close()

    print("Database session closed.")