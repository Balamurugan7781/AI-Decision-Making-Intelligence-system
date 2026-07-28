"""
LGD Logic Engine

This module calculates Loss Given Default (LGD) based on whether
the loan is secured and how much collateral covers the requested amount.

LGD = Loss Given Default
It represents the percentage of exposure the lender expects to lose
if the borrower defaults.
"""

from typing import Any


def calculate_collateral_coverage_ratio(
    collateral_value: float,
    requested_amount: float,
) -> float:
    """
    Calculate collateral coverage ratio.

    Example:
    collateral_value = 9000
    requested_amount = 8000

    coverage_ratio = 9000 / 8000 = 1.125
    """

    if requested_amount <= 0:
        raise ValueError("requested_amount must be greater than zero.")

    if collateral_value < 0:
        raise ValueError("collateral_value cannot be negative.")

    return collateral_value / requested_amount


def calculate_lgd(
    is_secured: bool,
    collateral_coverage_ratio: float,
) -> dict[str, Any]:
    """
    Calculate LGD using secured/unsecured status and collateral coverage.
    """

    if collateral_coverage_ratio < 0:
        raise ValueError("collateral_coverage_ratio cannot be negative.")

    if not is_secured:
        lgd = 0.75
        reason_code = "UNSECURED_LOAN_HIGH_LGD"

    elif collateral_coverage_ratio >= 1.0:
        lgd = 0.30
        reason_code = "FULLY_COLLATERALISED_LOW_LGD"

    elif collateral_coverage_ratio >= 0.50:
        lgd = 0.45
        reason_code = "PARTIALLY_COLLATERALISED_MODERATE_LGD"

    else:
        lgd = 0.60
        reason_code = "LOW_COLLATERAL_COVERAGE_HIGH_LGD"

    return {
        "is_secured": is_secured,
        "loss_given_default": lgd,
        "loss_given_default_percent": round(lgd * 100, 2),
        "collateral_coverage_ratio": round(
            collateral_coverage_ratio,
            4,
        ),
        "collateral_coverage_percent": round(
            collateral_coverage_ratio * 100,
            2,
        ),
        "lgd_reason_code": reason_code,
    }


def estimate_lgd_from_collateral(
    is_secured: bool,
    collateral_type: str,
    collateral_value: float,
    requested_amount: float,
) -> dict[str, Any]:
    """
    End-to-end LGD estimation from collateral details.
    """

    collateral_coverage_ratio = calculate_collateral_coverage_ratio(
        collateral_value=collateral_value,
        requested_amount=requested_amount,
    )

    lgd_result = calculate_lgd(
        is_secured=is_secured,
        collateral_coverage_ratio=collateral_coverage_ratio,
    )

    lgd_result["collateral_type"] = collateral_type.strip().lower()
    lgd_result["collateral_value"] = round(collateral_value, 2)

    return lgd_result