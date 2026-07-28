"""
Credit Policy Engine

This module implements policy-as-code for the FinTech Decision
Intelligence System.

It loads lending thresholds from:

    policies/credit_policy.yaml

Then it evaluates a loan application against those configurable
rules and returns:

- PASS / REVIEW / FAIL
- rejection reason codes
- review reason codes
- passed policy checks
- policy version
- evaluated thresholds

Important:
The thresholds in the YAML file are project assumptions for a
portfolio system. They do not represent the policy of a real
financial institution.
"""

from pathlib import Path
from typing import Any

import yaml


# ======================================================
# POLICY FILE PATH
# ======================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

POLICY_PATH = (
    PROJECT_ROOT
    / "policies"
    / "credit_policy.yaml"
)


# ======================================================
# LOAD POLICY
# ======================================================

def load_policy() -> dict[str, Any]:
    """
    Load the credit policy YAML file.

    Returns:
        Dictionary containing policy rules and thresholds.
    """

    if not POLICY_PATH.exists():
        raise FileNotFoundError(
            f"Policy file not found at: {POLICY_PATH}"
        )

    with open(
        POLICY_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        policy = yaml.safe_load(file)

    if not policy:
        raise ValueError(
            "Policy file is empty or invalid."
        )

    required_sections = [
        "policy_version",
        "risk_rules",
        "affordability_rules",
        "credit_rules",
        "financial_rules",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in policy
    ]

    if missing_sections:
        raise ValueError(
            f"Missing policy sections: {missing_sections}"
        )

    return policy


# ======================================================
# VALIDATE INPUTS
# ======================================================

def validate_policy_inputs(
    probability_of_default: float,
    debt_to_income_ratio: float,
    loan_to_income_ratio: float,
    credit_score: int,
    expected_loss: float,
    risk_adjusted_income: float,
    risk_adjusted_net_profit: float,
) -> None:
    """
    Validate all input values before applying policy rules.
    """

    if not 0 <= probability_of_default <= 1:
        raise ValueError(
            "probability_of_default must be between 0 and 1."
        )

    if debt_to_income_ratio < 0:
        raise ValueError(
            "debt_to_income_ratio cannot be negative."
        )

    if loan_to_income_ratio < 0:
        raise ValueError(
            "loan_to_income_ratio cannot be negative."
        )

    if not 300 <= credit_score <= 850:
        raise ValueError(
            "credit_score must be between 300 and 850."
        )

    if expected_loss < 0:
        raise ValueError(
            "expected_loss cannot be negative."
        )

    if risk_adjusted_income < 0:
        raise ValueError(
            "risk_adjusted_income cannot be negative."
        )

    # risk_adjusted_net_profit can be negative, so no validation
    # is applied for lower bound.


# ======================================================
# MAIN POLICY EVALUATION FUNCTION
# ======================================================

def evaluate_policy(
    probability_of_default: float,
    debt_to_income_ratio: float,
    loan_to_income_ratio: float,
    credit_score: int,
    expected_loss: float,
    risk_adjusted_income: float,
    risk_adjusted_net_profit: float,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Evaluate a loan application against the configured policy.

    Args:
        probability_of_default:
            Predicted Probability of Default from the ML model.

        debt_to_income_ratio:
            Existing debt divided by annual income.

        loan_to_income_ratio:
            Requested loan amount divided by annual income.

        credit_score:
            Applicant credit score.

        expected_loss:
            Expected credit loss from the financial engine.

        risk_adjusted_income:
            Risk-adjusted income from the financial engine.

        risk_adjusted_net_profit:
            Final risk-adjusted net profit from the financial engine.

        policy:
            Optional policy dictionary. If not provided, the YAML
            policy file will be loaded automatically.

    Returns:
        Policy evaluation result containing policy status,
        reason codes, passed checks and thresholds.
    """

    validate_policy_inputs(
        probability_of_default=probability_of_default,
        debt_to_income_ratio=debt_to_income_ratio,
        loan_to_income_ratio=loan_to_income_ratio,
        credit_score=credit_score,
        expected_loss=expected_loss,
        risk_adjusted_income=risk_adjusted_income,
        risk_adjusted_net_profit=risk_adjusted_net_profit,
    )

    if policy is None:
        policy = load_policy()

    # --------------------------------------------------
    # Read YAML sections
    # --------------------------------------------------

    risk_rules = policy["risk_rules"]
    affordability_rules = policy["affordability_rules"]
    credit_rules = policy["credit_rules"]
    financial_rules = policy["financial_rules"]

    # --------------------------------------------------
    # Extract thresholds
    # --------------------------------------------------

    maximum_pd_for_approval = float(
        risk_rules["maximum_pd_for_approval"]
    )

    maximum_pd_for_review = float(
        risk_rules["maximum_pd_for_review"]
    )

    maximum_debt_to_income_ratio = float(
        affordability_rules[
            "maximum_debt_to_income_ratio"
        ]
    )

    maximum_loan_to_income_ratio = float(
        affordability_rules[
            "maximum_loan_to_income_ratio"
        ]
    )

    minimum_credit_score = int(
        credit_rules["minimum_credit_score"]
    )

    minimum_risk_adjusted_net_profit = float(
        financial_rules[
            "minimum_risk_adjusted_net_profit"
        ]
    )

    maximum_expected_loss_to_income_ratio = float(
        financial_rules[
            "maximum_expected_loss_to_income_ratio"
        ]
    )

    # --------------------------------------------------
    # Containers for audit output
    # --------------------------------------------------

    rejection_reason_codes: list[str] = []
    review_reason_codes: list[str] = []
    passed_rules: list[str] = []

    # ==================================================
    # RULE 1: Probability of Default
    # ==================================================

    if probability_of_default > maximum_pd_for_review:
        rejection_reason_codes.append(
            "PD_ABOVE_MAXIMUM_POLICY_THRESHOLD"
        )

    elif probability_of_default > maximum_pd_for_approval:
        review_reason_codes.append(
            "PD_REQUIRES_MANUAL_REVIEW"
        )

    else:
        passed_rules.append(
            "PD_WITHIN_APPROVAL_THRESHOLD"
        )

    # ==================================================
    # RULE 2: Debt-to-Income Ratio
    # ==================================================

    if debt_to_income_ratio > maximum_debt_to_income_ratio:
        rejection_reason_codes.append(
            "DTI_ABOVE_POLICY_THRESHOLD"
        )

    else:
        passed_rules.append(
            "DTI_WITHIN_POLICY_THRESHOLD"
        )

    # ==================================================
    # RULE 3: Loan-to-Income Ratio
    # ==================================================

    if loan_to_income_ratio > maximum_loan_to_income_ratio:
        rejection_reason_codes.append(
            "LTI_ABOVE_POLICY_THRESHOLD"
        )

    else:
        passed_rules.append(
            "LTI_WITHIN_POLICY_THRESHOLD"
        )

    # ==================================================
    # RULE 4: Credit Score
    # ==================================================

    if credit_score < minimum_credit_score:
        rejection_reason_codes.append(
            "CREDIT_SCORE_BELOW_MINIMUM"
        )

    else:
        passed_rules.append(
            "CREDIT_SCORE_REQUIREMENT_MET"
        )

    # ==================================================
    # RULE 5: Risk-Adjusted Net Profit
    # ==================================================

    if (
        risk_adjusted_net_profit
        <= minimum_risk_adjusted_net_profit
    ):
        rejection_reason_codes.append(
            "NEGATIVE_RISK_ADJUSTED_NET_PROFIT"
        )

    else:
        passed_rules.append(
            "MINIMUM_PROFITABILITY_REQUIREMENT_MET"
        )

    # ==================================================
    # RULE 6: Expected Loss to Income Ratio
    # ==================================================

    if risk_adjusted_income == 0:
        expected_loss_to_income_ratio = None

        rejection_reason_codes.append(
            "NO_RISK_ADJUSTED_INCOME"
        )

    else:
        expected_loss_to_income_ratio = (
            expected_loss / risk_adjusted_income
        )

        if (
            expected_loss_to_income_ratio
            > maximum_expected_loss_to_income_ratio
        ):
            rejection_reason_codes.append(
                "EXPECTED_LOSS_EXCEEDS_ALLOWED_INCOME_RATIO"
            )

        else:
            passed_rules.append(
                "EXPECTED_LOSS_WITHIN_ALLOWED_INCOME_RATIO"
            )

    # ==================================================
    # FINAL POLICY STATUS
    # ==================================================

    if rejection_reason_codes:
        policy_status = "FAIL"

    elif review_reason_codes:
        policy_status = "REVIEW"

    else:
        policy_status = "PASS"

    return {
        "policy_status": policy_status,
        "policy_passed": policy_status == "PASS",
        "requires_manual_review": policy_status == "REVIEW",
        "policy_version": policy["policy_version"],
        "rejection_reason_codes": rejection_reason_codes,
        "review_reason_codes": review_reason_codes,
        "passed_rules": passed_rules,
        "expected_loss_to_income_ratio": (
            None
            if expected_loss_to_income_ratio is None
            else round(
                expected_loss_to_income_ratio,
                4,
            )
        ),
        "evaluated_thresholds": {
            "maximum_pd_for_approval": (
                maximum_pd_for_approval
            ),
            "maximum_pd_for_review": (
                maximum_pd_for_review
            ),
            "maximum_debt_to_income_ratio": (
                maximum_debt_to_income_ratio
            ),
            "maximum_loan_to_income_ratio": (
                maximum_loan_to_income_ratio
            ),
            "minimum_credit_score": (
                minimum_credit_score
            ),
            "minimum_risk_adjusted_net_profit": (
                minimum_risk_adjusted_net_profit
            ),
            "maximum_expected_loss_to_income_ratio": (
                maximum_expected_loss_to_income_ratio
            ),
        },
    }


# ======================================================
# BACKWARD-COMPATIBLE ALIAS
# ======================================================

def evaluate_credit_policy(
    probability_of_default: float,
    debt_to_income_ratio: float,
    loan_to_income_ratio: float,
    credit_score: int,
    expected_loss: float,
    risk_adjusted_income: float,
    risk_adjusted_net_profit: float,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Alias for evaluate_policy().

    This lets other files call either:
        evaluate_policy()
    or:
        evaluate_credit_policy()
    """

    return evaluate_policy(
        probability_of_default=probability_of_default,
        debt_to_income_ratio=debt_to_income_ratio,
        loan_to_income_ratio=loan_to_income_ratio,
        credit_score=credit_score,
        expected_loss=expected_loss,
        risk_adjusted_income=risk_adjusted_income,
        risk_adjusted_net_profit=risk_adjusted_net_profit,
        policy=policy,
    )


# ======================================================
# LOCAL TEST
# ======================================================

if __name__ == "__main__":
    sample_result = evaluate_policy(
        probability_of_default=0.5937,
        debt_to_income_ratio=0.20,
        loan_to_income_ratio=0.25,
        credit_score=690,
        expected_loss=5343.30,
        risk_adjusted_income=2194.02,
        risk_adjusted_net_profit=-5399.28,
    )

    print("\nCredit Policy Evaluation")
    print("=" * 60)

    for key, value in sample_result.items():
        print(f"{key}: {value}")