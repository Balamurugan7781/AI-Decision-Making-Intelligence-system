"""
Audit Repository

Persists decision audit records into the database.
"""

import json
from typing import Any

from db.database import SessionLocal
from db.models import DecisionAuditLog


def save_decision_audit_record(
    audit_record: dict[str, Any],
) -> str:
    """
    Save one decision audit record into the database.
    """

    db = SessionLocal()

    try:
        applicant = audit_record["applicant"]
        loan = audit_record["loan"]
        risk = audit_record["risk"]
        lgd = audit_record["lgd"]
        financials = audit_record["financials"]
        policy = audit_record["policy"]
        decision = audit_record["decision"]

        db_record = DecisionAuditLog(
            audit_id=audit_record["audit_id"],
            model_name=audit_record.get("model_name"),
            model_threshold=audit_record.get("model_threshold"),
            policy_version=audit_record.get("policy_version"),

            age=applicant.get("age"),
            annual_income=applicant.get("annual_income"),
            existing_debt=applicant.get("existing_debt"),
            credit_score=applicant.get("credit_score"),
            employment_status=applicant.get("employment_status"),
            region=applicant.get("region"),
            segment=applicant.get("segment"),
            channel=applicant.get("channel"),

            requested_amount=loan.get("requested_amount"),
            loan_term_months=loan.get("loan_term_months"),
            interest_rate=loan.get("interest_rate"),
            is_secured = loan.get("is_secured"),
            collateral_type = loan.get("collateral_type"),
            collateral_value = loan.get("collateral_value"),
            collateral_coverage_ratio = loan.get("collateral_coverage_ratio"),

            loss_given_default = lgd.get("loss_given_default"),
            loss_given_default_percent = lgd.get("loss_given_default_percent"),
            lgd_reason_code = lgd.get("lgd_reason_code"),

            raw_probability_of_default=risk.get(
                "raw_probability_of_default"
            ),
            adjusted_probability_of_default=risk.get(
                "adjusted_probability_of_default"
            ),
            term_risk_multiplier=risk.get("term_risk_multiplier"),
            adjustment_reason_code=risk.get(
                "adjustment_reason_code"
            ),

            expected_loss=financials.get("expected_loss"),
            expected_interest_income=financials.get(
                "expected_interest_income"
            ),
            risk_adjusted_income=financials.get(
                "risk_adjusted_income"
            ),
            cost_of_capital=financials.get("cost_of_capital"),
            risk_adjusted_net_profit=financials.get(
                "risk_adjusted_net_profit"
            ),
            is_profitable=financials.get("is_profitable"),

            policy_status=policy.get("policy_status"),
            policy_passed=policy.get("policy_passed"),
            requires_manual_review=policy.get(
                "requires_manual_review"
            ),

            final_decision=decision.get("final_decision"),

            primary_reason_codes=json.dumps(
                decision.get("primary_reason_codes", [])
            ),
            rejection_reason_codes=json.dumps(
                policy.get("rejection_reason_codes", [])
            ),
            review_reason_codes=json.dumps(
                policy.get("review_reason_codes", [])
            ),
            passed_rules=json.dumps(
                policy.get("passed_rules", [])
            ),
            evaluated_thresholds=json.dumps(
                policy.get("evaluated_thresholds", {})
            ),
        )

        db.add(db_record)
        db.commit()

        return audit_record["audit_id"]

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()