# This code is for checking the analysis of each loan applications and the customers' behavior in the portfolio. It includes functions for calculating various metrics such as default rates, average loan amounts, and customer demographics.

# Now we are going to discuss the working flow of this script...
# Portfolio analytics metrics....
""" 1) How many customers are in the portfolio?
 2) Total Loan applications in the portfolio ?
 3) Total loans approved in the portfolio ?
 4) Approval rate in the portfolio?
 5) Total loan amount disbursed in the portfolio ?



 Workflow of this analytics script:
 business.db
 ||
 ||
 ||
 SQLAlchemy Session
    ||
    ||
    Customer Table, LoanApplication Table, Loan Table
    || 
    ||
    Calculate KPIs and Metrics
    ||
    ||
    Output Results (e.g., print statements, visualizations, etc.)
 """ 
# before that we have to import the necessary libraries to check whether everything is working or not. 
from sqlalchemy import func

from db.database import SessionLocal
from db.models import Customer,LoanApplication,Loan

# print("Importing necessary libraries...")
def calculate_portfolio_metrics():
      session = SessionLocal()
      try:
      # 1) How many customers are there in the portfolio? 
         total_customers = session.query(Customer).count()

      # 2) Total Loan applications in the portfolio ?
         total_loan_applications = session.query(LoanApplication).count()

         # 3) Total Loan Applications approved in the portfolio?
         total_loan_applications_approved = session.query(Loan).count()

         # Approval rate...
         approval_rate = (total_loan_applications_approved/total_loan_applications)*100

         # total loan amnt disbured....
         total_disbursed_amount = (session.query(func.sum(Loan.approved_amount)).scalar() or 0)

         # average loan amount disbursed....
         average_loan_amount_disbursed = (session.query(func.avg(Loan.approved_amount)).scalar() or 0)


         return {"total_customers": total_customers,
                  "total_loan_applications": total_loan_applications,
                  "total_loan_applications_approved": total_loan_applications_approved,
                  "approval_rate": approval_rate,
                  "total_disbursed_amount": total_disbursed_amount,
                  "average_loan_amount_disbursed": average_loan_amount_disbursed }
      finally:
       session.close()



if __name__ == "__main__":
    metrics = calculate_portfolio_metrics()

    print("\nPortfolio Analytics")
    print("=" * 50)

    for key, value in metrics.items():
        print(f"{key}: {value}")

