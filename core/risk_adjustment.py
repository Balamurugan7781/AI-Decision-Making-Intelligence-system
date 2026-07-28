
""" This function is created to improve the risk adjustment. before implementing this logic , the system says the loan application tends to be safe
    if the loan term months is higher. This is not applicable for every loan applications. This is because the person who applied for loan ....
    -- may lose the job and unable to pay the loan amount.
    -- may face some emergency situations and lose money to be paid for the loan.
    
    So, going with this logic can backfire the code. 
    So, I am creating this script to ensure that the term risk multiplier gets increases based on the loan term months...
    """

from typing import Any





def adjust_pd_for_term(probability_of_default:float,loan_term_months:int, ) -> dict:
    """
    Apply a conservative term-risk adjustment to the raw model PD.

    This is a transparent MVP assumption. In a production system,
    this adjustment should be validated using historical default data
    and approved by credit-risk teams.
    """
    if 0<=probability_of_default>=1:
        raise ValueError("probability_of_default should be within the range from 0 to 1.")
    
    if loan_term_months<=0:
        raise ValueError("loan_term_months must be greater than zero.")
    
    if loan_term_months<=24:
        multiplier = 1.00
        reason_code = "Standard Term No PD adjustment."
    
    elif loan_term_months> 24 and loan_term_months<=36:
        multiplier=1.05
        reason_code = "Moderate Term Risk Adjustment."

    elif loan_term_months > 36 and loan_term_months<=60:
        multiplier=1.15
        reason_code = "Long Term Risk Adjustment."
    
    else:
        multiplier = 1.25
        reason_code = "Extended Term risk adjustment."

    
    adjusted_pd = min(probability_of_default*multiplier,1.0)


    return {"raw_probability_of_default": round(
            probability_of_default,
            4,
        ),
        "adjusted_probability_of_default": round(
            adjusted_pd,
            4,
        ),
        "raw_probability_of_default_percent": round(
            probability_of_default * 100,
            2,
        ),
        "adjusted_probability_of_default_percent": round(
            adjusted_pd * 100,
            2,
        ),
        "term_risk_multiplier": multiplier,
        "loan_term_months": loan_term_months,
        "adjustment_reason_code": reason_code,
    }