"""  This script is created for the purpose of saving all the outputs given by FastAPI endpoints.

The audit record is designed to support:
- traceability
- portfolio analytics
- LLM-to-SQL querying
- RAG-supported explanations
- model and policy governance."""

from datetime import datetime,timezone
from typing import Any
from uuid import uuid4

def create_decision_audit_record(application_data:dict[str,Any], prediction_result: dict[str,Any], risk_adjustment_result:dict[str,Any], lgd_result:dict[str,Any], financial_result:dict[str,Any], policy_result:dict[str,Any], decision_result: dict[str,Any] )-> dict[str,Any]:
    """Create a clean audit record for single loan decision. """
    return {
        "audit_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),

        "model_name": prediction_result.get("model_name"),
        "model_threshold": prediction_result.get("model_threshold"),

        "policy_version": policy_result.get("policy_version"),

        "applicant": {
            "age": application_data.get("age"),
            "annual_income": application_data.get("annual_income"),
            "existing_debt": application_data.get("existing_debt"),
            "credit_score": application_data.get("credit_score"),
            "employment_status": application_data.get("employment_status"),
            "region": application_data.get("region"),
            "segment": application_data.get("segment"),
            "channel": application_data.get("channel"),
        },

        "loan": {
            "requested_amount": application_data.get("requested_amount"),
            "loan_term_months": application_data.get("loan_term_months"),
            "interest_rate": application_data.get("interest_rate"),
            "is_secured":lgd_result.get("is_secured"),
            "collateral_type":lgd_result.get("collateral_type"),
            "collateral_value":lgd_result.get("collateral_value"),
            "collateral_coverage_ratio":lgd_result.get("collateral_coverage_ratio"),

        },
        "lgd":{
            "loss_given_default":lgd_result.get("loss_given_default"),
            "loss_given_default_percent":lgd_result.get("loss_given_default_percent"),
            "lgd_reason_code":lgd_result.get("lgd_reason_code"),
        },

        "risk": {
            "raw_probability_of_default": risk_adjustment_result.get(
                "raw_probability_of_default"
            ),
            "adjusted_probability_of_default": risk_adjustment_result.get(
                "adjusted_probability_of_default"
            ),
            "term_risk_multiplier": risk_adjustment_result.get(
                "term_risk_multiplier"
            ),
            "adjustment_reason_code": risk_adjustment_result.get(
                "adjustment_reason_code"
            ),
        },

        "financials": {
            "expected_loss": financial_result.get("expected_loss"),
            "expected_interest_income": financial_result.get(
                "expected_interest_income"
            ),
            "risk_adjusted_income": financial_result.get(
                "risk_adjusted_income"
            ),
            "cost_of_capital": financial_result.get("cost_of_capital"),
            "risk_adjusted_net_profit": financial_result.get(
                "risk_adjusted_net_profit"
            ),
            "is_profitable": financial_result.get("is_profitable"),
        },

        "policy": {
            "policy_status": policy_result.get("policy_status"),
            "policy_passed": policy_result.get("policy_passed"),
            "requires_manual_review": policy_result.get(
                "requires_manual_review"
            ),
            "rejection_reason_codes": policy_result.get(
                "rejection_reason_codes",
                [],
            ),
            "review_reason_codes": policy_result.get(
                "review_reason_codes",
                [],
            ),
            "passed_rules": policy_result.get("passed_rules", []),
            "evaluated_thresholds": policy_result.get(
                "evaluated_thresholds",
                {},
            ),
        },

        "decision": {
            "final_decision": decision_result.get("decision"),
            "primary_reason_codes": decision_result.get(
                "primary_reason_codes",
                [],
            ),
        },
    } 

