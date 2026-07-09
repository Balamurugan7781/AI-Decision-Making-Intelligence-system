"""

Loan Decision Engine

This module combines:
- Probability of Default from the ML model
- Financial evaluation from financial_engine.py
- Policy evaluation from policy_engine.py

It produces the final lending decision:
APPROVE, REVIEW, or REJECT.

"""

from typing import Any

################################

# Final Decision Engine

################################

def make_decision(pd: float,financial_result:dict[str, Any] ,policy_result:dict[str, Any],) -> dict[str,Any]:
   """
    Combine model risk, financial outcome and policy status
    into a final loan decision.

    Args:
        probability_of_default:
            Predicted probability that the loan will default.

        financial_result:
            Output from core.financial_engine.evaluate_loan_financials().

        policy_result:
            Output from core.policy_engine.evaluate_credit_policy().

    Returns:
        Final decision dictionary with decision, reason codes,
        policy version and supporting metrics."""
   
   rejection_reason_codes = list(policy_result.get("rejection_reason_codes", []))

   review_reason_codes = list(policy_result.get("review_reason_codes", []))

   final_reason_codes = [] 


   # Hard policy feature.....

   # checking the policy result of the loan application, if it is fail, then we are rejecting it..

   if policy_result.get("policy_status")=="FAIL":
         final_decision = "REJECT"
         final_reason_codes.extend(rejection_reason_codes)

   # checking the policy result is review or not.....

   elif policy_result.get("policy_status")=="REVIEW":
        final_decision = "REVIEW"
        final_reason_codes.extend(review_reason_codes)

    # now checking with the financial results of the loan application.....
    

   elif financial_result.get("risk_adjusted_net_profit")<=0:
        final_decision = "REJECT"
        final_reason_codes.append("NEGATIVE_RISK_ADJUSTED_NET_PROFIT")
    
    # Elevated risk review check .....

   elif pd>=0.30:
        
        final_decision = "REVIEW"
        final_reason_codes.append("ELEVATED_RISK_REVIEW")

    # Else "approve" logic......
   else:
        final_decision = "APPROVE"
        final_reason_codes.append("RISK ADJUSTMENTS AND POLICY CHECKS PASSED")


   return {"decision":final_decision,
            "primary_reason_codes":final_reason_codes,
            "probability_of_default":round(pd,4),
            "financial_result":financial_result,
            "probability_of_default_percentage":round(pd*100,2),
            "expected_loss": financial_result[
            "expected_loss"
        ],
        "expected_interest_income": financial_result[
            "expected_interest_income"
        ],
        "risk_adjusted_income": financial_result[
            "risk_adjusted_income"
        ],
        "cost_of_capital": financial_result[
            "cost_of_capital"
        ],
        "risk_adjusted_net_profit": financial_result[
            "risk_adjusted_net_profit"
        ],
        "is_profitable": financial_result[
            "is_profitable"
        ],
        "policy_status": policy_result[
            "policy_status"
        ],
        "policy_version": policy_result[
            "policy_version"
        ],
        "policy_passed": policy_result[
            "policy_passed"
        ],
        "requires_manual_review": policy_result[
            "requires_manual_review"
        ],
        "rejection_reason_codes": rejection_reason_codes,
        "review_reason_codes": review_reason_codes,
        "passed_policy_rules": policy_result.get(
            "passed_rules",
            [],
        ),
    }



if __name__ == "__main__":
    sample_financial_result = {
        "probability_of_default": 0.5937,
        "probability_of_default_percent": 59.37,
        "exposure_at_default": 15000,
        "loss_given_default": 0.60,
        "loss_given_default_percent": 60.0,
        "expected_loss": 5343.30,
        "expected_interest_income": 5400.00,
        "risk_adjusted_income": 2194.02,
        "cost_of_capital": 2250.00,
        "risk_adjusted_net_profit": -5399.28,
        "is_profitable": False,
    }
    sample_policy_result = {
        "policy_status": "FAIL",
        "policy_passed": False,
        "requires_manual_review": False,
        "policy_version": "credit-policy-v1",
        "rejection_reason_codes": [
            "PD_ABOVE_MAXIMUM_POLICY_THRESHOLD",
            "NEGATIVE_RISK_ADJUSTED_NET_PROFIT",
            "EXPECTED_LOSS_EXCEEDS_ALLOWED_INCOME_RATIO",
        ],
        "review_reason_codes": [],
        "passed_rules": [
            "DTI_WITHIN_POLICY_THRESHOLD",
            "LTI_WITHIN_POLICY_THRESHOLD",
            "CREDIT_SCORE_REQUIREMENT_MET",
        ],
    }
    decision_result = make_decision(
        pd=0.5937,
        financial_result=sample_financial_result,
        policy_result=sample_policy_result,
    )

    print("\nLoan Decision")
    print("=" * 60)

    for key, value in decision_result.items():
        print(f"{key}: {value}")



    

   


