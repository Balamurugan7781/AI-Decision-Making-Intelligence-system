# This script is for analysing the remaining risk with loan portfolios. It includes the remaining table repayments.
"""This script answers how risk is our portfolio? 
So, we would be using KPIs for risk calculation such as:
1) Default Rate: Number of loans defaulted / total number of loans
2) Delinquency Rate: Number of loans delinquent / total number of loans ( Number of loans that were paid late)
3) Average Days late: How late does customers usually pay?
4) Loan Status Distribution: How many loans are active? Completed? Defaulted? Delinquent?
5) Portfolio at Risk(PAP): what proportion of our portfolio is at risk of defaulting ? (Total approved amount on default loans)/ (Total approved amount on all loans)
"""

from sqlalchemy import func

from db.database import SessionLocal
from db.models import Loan,Repayments


def calculate_risk_metrics():
    session = SessionLocal()
    # Total Loans
    total_loans = session.query(Loan).count()

    # defaulted loans 
    defaulted_loans = session.query(Loan).filter(Loan.loan_status=="defaulted").count()

    # Default Rate....
    default_rate = (defaulted_loans/total_loans)*100 if total_loans >0 else 0

    # Deliquency Rate...
    total_repayments = session.query(Repayments).count()
    late_repayments = session.query(Repayments).filter(Repayments.days_late > 0 , Repayments.amount_due > 0).count()

    delinquency_rate = (late_repayments/total_repayments)*100 if total_repayments > 0  else 0


    # Average days late...
    average_days_late = session.query(func.avg(Repayments.days_late)).filter(Repayments.days_late>0).scalar() or 0

    # Loan Status Distribution...
    loan_status_distribution = session.query(Loan.loan_status, func.count(Loan.loan_id)).group_by(Loan.loan_status).all()

    # Portfolio at Risk (PAR)...
    # This tells about the 
    total_exposure = session.query(func.sum(Loan.approved_amount)).scalar() or 0
    risk_exposure = session.query(func.sum(Loan.approved_amount)).filter(Loan.loan_status=="defaulted").scalar() or 0

    portfolio_at_risk = (risk_exposure/total_exposure)*100 if total_exposure> 0 else 0
    #Close the session
    session.close()

    return {
            "total_loans": total_loans,
            "defaulted_loans": defaulted_loans,
            "default_rate": round(default_rate, 2),
            "total_repayments": total_repayments,
            "late_repayments": late_repayments,
            "delinquency_rate": round(delinquency_rate, 2),
            "average_days_late": round(average_days_late, 2),
            "portfolio_at_risk": round(portfolio_at_risk, 2),
            "loan_status_distribution": loan_status_distribution,
        }
    

if __name__ == "__main__":
    metrics = calculate_risk_metrics()

    print("\nRisk Analytics")
    print("=" * 50)

    for key, value in metrics.items():
        print(f"{key}: {value}")