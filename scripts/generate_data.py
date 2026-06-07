import sqlite3
import random
from datetime import datetime, timedelta
from db.initt_db import db_path

# print(db_path)
# -----------------------------
# DATABASE CONNECTION
# -----------------------------

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

NUM_CUSTOMERS = 1000
MAX_APPLICATIONS_PER_CUSTOMER = 3

regions = ["London", "Manchester", "Birmingham", "Leeds", "Liverpool"]
employment_status = ["employed", "self-employed", "unemployed"]
segments = ["prime", "near_prime", "subprime"]
channels = ["mobile_app", "web", "branch"]

# -----------------------------
# RISK SCORE FUNCTION
# -----------------------------

def calculate_risk_score(credit_score, income):

    credit_component = (850 - credit_score) / 350
    income_component = max(0, 1 - income / 150000)

    risk_score = (credit_component * 0.7) + (income_component * 0.3)

    return round(min(max(risk_score, 0.01), 0.6), 3)

# -----------------------------
# GENERATE CUSTOMERS
# -----------------------------

for customer_id in range(1, NUM_CUSTOMERS + 1):

    age = random.randint(21, 65)
    income = random.randint(20000, 120000)

    signup_date = datetime.now() - timedelta(days=random.randint(100, 2000))

    cursor.execute("""
        INSERT INTO customers
        (customer_id, age, employment_status, annual_income, region, signup_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        customer_id,
        age,
        random.choice(employment_status),
        income,
        random.choice(regions),
        signup_date.date()
    ))

# -----------------------------
# GENERATE LOAN APPLICATIONS
# -----------------------------

cursor.execute("SELECT customer_id, annual_income FROM customers")
customers = cursor.fetchall()

application_id = 1
loan_id = 1
repayment_id = 1

for customer in customers:

    customer_id, income = customer

    num_apps = random.randint(1, MAX_APPLICATIONS_PER_CUSTOMER)

    for _ in range(num_apps):

        credit_score = random.randint(520, 820)

        requested_amount = random.randint(2000, 25000)

        loan_term = random.choice([12, 24, 36])

        interest_rate = round(random.uniform(5, 18), 2)

        risk_score = calculate_risk_score(credit_score, income)

        approval_threshold = 0.25

        approval_decision = "approved" if risk_score < approval_threshold else "rejected"

        predicted_loss = requested_amount * risk_score
        predicted_profit = (requested_amount * interest_rate / 100) - predicted_loss

        application_date = datetime.now() - timedelta(days=random.randint(0, 365))

        cursor.execute("""
            INSERT INTO loan_applications
            (application_id, customer_id, application_date, requested_amount,
             loan_term_months, interest_rate, model_risk_score,
             approval_threshold, approval_decision,
             predicted_profit, predicted_loss, segment, channel)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            application_id,
            customer_id,
            application_date.date(),
            requested_amount,
            loan_term,
            interest_rate,
            risk_score,
            approval_threshold,
            approval_decision,
            predicted_profit,
            predicted_loss,
            random.choice(segments),
            random.choice(channels)
        ))

        # -----------------------------
        # CREATE LOAN IF APPROVED
        # -----------------------------

        if approval_decision == "approved":

            disbursed_date = application_date + timedelta(days=2)

            loan_status = random.choices(
                ["active", "completed", "defaulted"],
                weights=[0.6, 0.3, 0.1]
            )[0]

            expected_return = requested_amount * (1 + interest_rate / 100)

            cursor.execute("""
                INSERT INTO loans
                (loan_id, application_id, approved_amount, disbursed_date,
                 expected_total_return, loan_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                loan_id,
                application_id,
                requested_amount,
                disbursed_date.date(),
                expected_return,
                loan_status
            ))

            # -----------------------------
            # GENERATE REPAYMENTS
            # -----------------------------

            for i in range(loan_term):

                due_date = disbursed_date + timedelta(days=30 * i)

                amount_due = expected_return / loan_term

                if loan_status == "defaulted" and i > loan_term * 0.5:

                    amount_paid = 0
                    paid_date = None
                    days_late = None

                else:

                    paid_date = due_date + timedelta(days=random.randint(0, 5))
                    amount_paid = amount_due
                    days_late = (paid_date - due_date).days

                cursor.execute("""
                    INSERT INTO repayments
                    (repayment_id, loan_id, due_date, paid_date,
                     amount_due, amount_paid, days_late)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    repayment_id,
                    loan_id,
                    due_date.date(),
                    paid_date.date() if paid_date else None,
                    amount_due,
                    amount_paid,
                    days_late
                ))

                repayment_id += 1

            loan_id += 1

        application_id += 1


conn.commit()
conn.close()

print("Synthetic fintech dataset generated successfully.")