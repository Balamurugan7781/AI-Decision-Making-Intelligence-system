"""
Financial Evaluation Engine

This module calculates the expected financial outcome of a loan
using the predicted Probability of Default.

Core calculations:

Expected Loss
    = PD × LGD × EAD

Expected Interest Income
    = Loan Amount × Annual Interest Rate × Loan Term in Years

Risk-Adjusted Expected Income
    = Expected Interest Income × (1 - PD)

Cost of Capital
    = Loan Amount × Cost of Capital Rate × Loan Term in Years

Risk-Adjusted Net Profit
    = Risk-Adjusted Expected Income
      - Expected Loss
      - Cost of Capital
"""

from typing import Any


# ======================================================
# DEFAULT FINANCIAL ASSUMPTIONS
# ======================================================

DEFAULT_LGD = 0.60
DEFAULT_COST_OF_CAPITAL_RATE = 0.05


# ======================================================
# INPUT VALIDATION
# ======================================================

def validate_financial_inputs(
    probability_of_default: float,
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_months: int,
    loss_given_default: float,
    cost_of_capital_rate: float,
) -> None:
    """
    Validate all financial-engine inputs.
    """

    if not 0 <= probability_of_default <= 1:
        raise ValueError(
            "probability_of_default must be between 0 and 1."
        )

    if loan_amount <= 0:
        raise ValueError(
            "loan_amount must be greater than zero."
        )

    if not 0 <= annual_interest_rate <= 1:
        raise ValueError(
            "annual_interest_rate must be expressed as a decimal "
            "between 0 and 1. For example, use 0.12 for 12%."
        )

    if loan_term_months <= 0:
        raise ValueError(
            "loan_term_months must be greater than zero."
        )

    if not 0 <= loss_given_default <= 1:
        raise ValueError(
            "loss_given_default must be between 0 and 1."
        )

    if not 0 <= cost_of_capital_rate <= 1:
        raise ValueError(
            "cost_of_capital_rate must be between 0 and 1."
        )


# ======================================================
# EXPECTED LOSS
# ======================================================

def calculate_expected_loss(
    probability_of_default: float,
    exposure_at_default: float,
    loss_given_default: float,
) -> float:
    """
    Calculate expected credit loss.

    Expected Loss = PD × LGD × EAD
    """

    return (
        probability_of_default
        * loss_given_default
        * exposure_at_default
    )


# ======================================================
# EXPECTED INTEREST INCOME
# ======================================================

def calculate_expected_interest_income(
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_months: int,
) -> float:
    """
    Calculate total contractual interest income using
    a simplified simple-interest assumption.
    """

    loan_term_years = loan_term_months / 12

    return (
        loan_amount
        * annual_interest_rate
        * loan_term_years
    )


# ======================================================
# RISK-ADJUSTED INCOME
# ======================================================

def calculate_risk_adjusted_income(
    expected_interest_income: float,
    probability_of_default: float,
) -> float:
    """
    Adjust expected interest income for the probability
    that the customer will successfully repay.
    """

    survival_probability = 1 - probability_of_default

    return (
        expected_interest_income
        * survival_probability
    )


# ======================================================
# COST OF CAPITAL
# ======================================================

def calculate_cost_of_capital(
    loan_amount: float,
    cost_of_capital_rate: float,
    loan_term_months: int,
) -> float:
    """
    Calculate the simplified cost of funding the loan.
    """

    loan_term_years = loan_term_months / 12

    return (
        loan_amount
        * cost_of_capital_rate
        * loan_term_years
    )


# ======================================================
# COMPLETE FINANCIAL EVALUATION
# ======================================================

def evaluate_loan_financials(
    probability_of_default: float,
    loan_amount: float,
    annual_interest_rate: float,
    loan_term_months: int,
    loss_given_default: float = DEFAULT_LGD,
    cost_of_capital_rate: float = DEFAULT_COST_OF_CAPITAL_RATE,
) -> dict[str, Any]:
    """
    Calculate the complete risk-adjusted financial outcome
    of a loan application.

    Args:
        probability_of_default:
            Predicted default probability between 0 and 1.

        loan_amount:
            Requested or approved loan exposure.

        annual_interest_rate:
            Annual interest rate expressed as a decimal.

        loan_term_months:
            Loan duration in months.

        loss_given_default:
            Percentage of exposure expected to be lost
            if the customer defaults.

        cost_of_capital_rate:
            Annual cost of funding the loan.

    Returns:
        Dictionary containing expected loss, income,
        capital cost and risk-adjusted net profit.
    """

    validate_financial_inputs(
        probability_of_default=probability_of_default,
        loan_amount=loan_amount,
        annual_interest_rate=annual_interest_rate,
        loan_term_months=loan_term_months,
        loss_given_default=loss_given_default,
        cost_of_capital_rate=cost_of_capital_rate,
    )

    exposure_at_default = loan_amount

    expected_loss = calculate_expected_loss(
        probability_of_default=probability_of_default,
        exposure_at_default=exposure_at_default,
        loss_given_default=loss_given_default,
    )

    expected_interest_income = calculate_expected_interest_income(
        loan_amount=loan_amount,
        annual_interest_rate=annual_interest_rate,
        loan_term_months=loan_term_months,
    )

    risk_adjusted_income = calculate_risk_adjusted_income(
        expected_interest_income=expected_interest_income,
        probability_of_default=probability_of_default,
    )

    cost_of_capital = calculate_cost_of_capital(
        loan_amount=loan_amount,
        cost_of_capital_rate=cost_of_capital_rate,
        loan_term_months=loan_term_months,
    )

    risk_adjusted_net_profit = (
        risk_adjusted_income
        - expected_loss
        - cost_of_capital
    )

    return {
        "probability_of_default": round(
            probability_of_default,
            4,
        ),
        "probability_of_default_percent": round(
            probability_of_default * 100,
            2,
        ),
        "exposure_at_default": round(
            exposure_at_default,
            2,
        ),
        "loss_given_default": round(
            loss_given_default,
            4,
        ),
        "loss_given_default_percent": round(
            loss_given_default * 100,
            2,
        ),
        "expected_loss": round(
            expected_loss,
            2,
        ),
        "expected_interest_income": round(
            expected_interest_income,
            2,
        ),
        "risk_adjusted_income": round(
            risk_adjusted_income,
            2,
        ),
        "cost_of_capital": round(
            cost_of_capital,
            2,
        ),
        "risk_adjusted_net_profit": round(
            risk_adjusted_net_profit,
            2,
        ),
        "is_profitable": (
            risk_adjusted_net_profit > 0
        ),
    }


# ======================================================
# LOCAL TEST
# ======================================================

if __name__ == "__main__":
    sample_result = evaluate_loan_financials(
        probability_of_default=0.5937,
        loan_amount=15000,
        annual_interest_rate=0.12,
        loan_term_months=36,
    )

    print("\nFinancial Evaluation")
    print("=" * 55)

    for key, value in sample_result.items():
        print(f"{key}: {value}")