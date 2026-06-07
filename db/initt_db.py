import os     # this one is for folder creation
import sqlite3   # this one is for making connection with Database....

""" Defining the correct database path"""
CUR_DIR = os.path.dirname(os.path.abspath(__file__))

# 
Project_dir = os.path.dirname(CUR_DIR)
Data_path = os.path.join(Project_dir, "data")
db_path = os.path.join(Data_path, "business.db")

"""Now ensure /data folder exists"""
os.makedirs(Data_path, exist_ok=True)


# now create the database 

def create_connection():
    if not os.path.exists(Data_path):
        os.makedirs(Data_path)

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

""" Now we are going to create tables and datas for the relationships...."""

def create_tables(conn):
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id INTEGER PRIMARY KEY,
        age INTEGER NOT NULL,
        employment_status TEXT NOT NULL,
        employment_years INTEGER NOT NULL,
        annual_income REAL NOT NULL,
        existing_debt REAL NOT NULL,
        credit_score INTEGER NOT NULL,
        region TEXT NOT NULL,
        signup_date DATE NOT NULL
    );
    """)

    # -------------------------------
    # Loan Applications (Decision Layer)
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loan_applications (
        application_id INTEGER PRIMARY KEY,
        customer_id INTEGER NOT NULL,
        application_date DATE NOT NULL,
        requested_amount REAL NOT NULL,
        loan_term_months INTEGER NOT NULL,
        interest_rate REAL NOT NULL,
        model_risk_score REAL NOT NULL,
        approval_threshold REAL NOT NULL,
        approval_decision TEXT NOT NULL CHECK(approval_decision IN ('approved', 'rejected')),
        predicted_profit REAL,
        predicted_loss REAL,
        segment TEXT,
        channel TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    );
    """)

    # -------------------------------
    # Loans (Approved Outcomes)
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY,
        application_id INTEGER NOT NULL,
        approved_amount REAL NOT NULL,
        disbursed_date DATE NOT NULL,
        expected_total_return REAL NOT NULL,
        loan_status TEXT NOT NULL CHECK(loan_status IN ('active', 'completed', 'defaulted')),
        FOREIGN KEY (application_id) REFERENCES loan_applications(application_id)
    );
    """)

    # -------------------------------
    # Repayments (Behaviour Layer)
    # -------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repayments (
        repayment_id INTEGER PRIMARY KEY,
        loan_id INTEGER NOT NULL,
        due_date DATE NOT NULL,
        paid_date DATE,
        amount_due REAL NOT NULL,
        amount_paid REAL,
        days_late INTEGER,
        FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
    );
    """)
    conn.commit()
    print("All fintech tables created successfully.")


if __name__ == "__main__":
    connection = create_connection()
    create_tables(connection)
    connection.close()