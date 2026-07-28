"""
Decision Impact Analysis

This module analyses saved decision audit logs from the database.

It helps convert individual loan decisions into portfolio-level
business insights.

Outputs include:
- total decisions
- approve/review/reject counts
- approval, review and rejection rates
- average raw and adjusted PD
- total expected loss
- total risk-adjusted net profit
- decision breakdown by segment
- top reason codes

This is the bridge between the core decision engine and the future
LLM-to-SQL analytics layer.
"""

import json
import sqlite3
from pathlib import Path

import pandas as pd


# ======================================================
# CONFIGURATION
# ======================================================

DB_PATH = Path("data/business.db")
TABLE_NAME = "decision_audit_logs"


# ======================================================
# DATA LOADING
# ======================================================

def load_decision_audit_logs() -> pd.DataFrame:
    """
    Load decision audit logs from the SQLite database.
    """

    if not DB_PATH.exists():
        raise FileNotFoundError(
            f"Database file was not found: {DB_PATH}"
        )

    conn = sqlite3.connect(DB_PATH)

    try:
        query = f"""
        SELECT
            audit_id,
            created_at,
            model_name,
            policy_version,

            age,
            annual_income,
            existing_debt,
            credit_score,
            employment_status,
            region,
            segment,
            channel,

            requested_amount,
            loan_term_months,
            interest_rate,

            raw_probability_of_default,
            adjusted_probability_of_default,
            term_risk_multiplier,
            adjustment_reason_code,

            expected_loss,
            expected_interest_income,
            risk_adjusted_income,
            cost_of_capital,
            risk_adjusted_net_profit,
            is_profitable,

            policy_status,
            policy_passed,
            requires_manual_review,

            final_decision,
            primary_reason_codes,
            rejection_reason_codes,
            review_reason_codes,
            passed_rules,
            evaluated_thresholds
        FROM {TABLE_NAME}
        """

        df = pd.read_sql_query(query, conn)

    finally:
        conn.close()

    return df


# ======================================================
# BASIC PORTFOLIO SUMMARY
# ======================================================

def calculate_portfolio_summary(
    df: pd.DataFrame,
) -> dict:
    """
    Calculate high-level decision portfolio metrics.
    """

    if df.empty:
        return {
            "total_decisions": 0,
            "message": "No decision audit logs found.",
        }

    total_decisions = len(df)

    decision_counts = (
        df["final_decision"]
        .value_counts()
        .to_dict()
    )

    approve_count = decision_counts.get("APPROVE", 0)
    review_count = decision_counts.get("REVIEW", 0)
    reject_count = decision_counts.get("REJECT", 0)

    summary = {
        "total_decisions": total_decisions,

        "approve_count": approve_count,
        "review_count": review_count,
        "reject_count": reject_count,

        "approval_rate_percent": round(
            approve_count / total_decisions * 100,
            2,
        ),
        "review_rate_percent": round(
            review_count / total_decisions * 100,
            2,
        ),
        "rejection_rate_percent": round(
            reject_count / total_decisions * 100,
            2,
        ),

        "average_raw_pd_percent": round(
            df["raw_probability_of_default"].mean() * 100,
            2,
        ),
        "average_adjusted_pd_percent": round(
            df["adjusted_probability_of_default"].mean() * 100,
            2,
        ),

        "total_expected_loss": round(
            df["expected_loss"].sum(),
            2,
        ),
        "total_expected_interest_income": round(
            df["expected_interest_income"].sum(),
            2,
        ),
        "total_cost_of_capital": round(
            df["cost_of_capital"].sum(),
            2,
        ),
        "total_risk_adjusted_net_profit": round(
            df["risk_adjusted_net_profit"].sum(),
            2,
        ),

        "average_risk_adjusted_net_profit": round(
            df["risk_adjusted_net_profit"].mean(),
            2,
        ),
    }

    return summary


# ======================================================
# DECISION BREAKDOWN
# ======================================================

def calculate_decision_breakdown(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count decisions by final decision category.
    """

    if df.empty:
        return pd.DataFrame()

    breakdown = (
        df.groupby("final_decision", as_index=False)
        .agg(
            decision_count=("audit_id", "count"),
            average_adjusted_pd=(
                "adjusted_probability_of_default",
                "mean",
            ),
            total_expected_loss=("expected_loss", "sum"),
            total_net_profit=(
                "risk_adjusted_net_profit",
                "sum",
            ),
        )
    )

    breakdown["average_adjusted_pd_percent"] = (
        breakdown["average_adjusted_pd"] * 100
    ).round(2)

    breakdown["total_expected_loss"] = (
        breakdown["total_expected_loss"].round(2)
    )

    breakdown["total_net_profit"] = (
        breakdown["total_net_profit"].round(2)
    )

    return breakdown[["final_decision","decision_count","average_adjusted_pd_percent","total_expected_loss","total_net_profit",]]


# ======================================================
# SEGMENT ANALYSIS
# ======================================================

def calculate_segment_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Summarise decision behaviour by customer segment.
    """

    if df.empty:
        return pd.DataFrame()

    segment_summary = (
        df.groupby("segment", as_index=False)
        .agg(
            total_decisions=("audit_id", "count"),
            average_adjusted_pd=(
                "adjusted_probability_of_default",
                "mean",
            ),
            total_expected_loss=("expected_loss", "sum"),
            total_net_profit=(
                "risk_adjusted_net_profit",
                "sum",
            ),
            average_credit_score=("credit_score", "mean"),
            average_income=("annual_income", "mean"),
        )
    )

    segment_summary["average_adjusted_pd_percent"] = (
        segment_summary["average_adjusted_pd"] * 100
    ).round(2)

    segment_summary["total_expected_loss"] = (
        segment_summary["total_expected_loss"].round(2)
    )

    segment_summary["total_net_profit"] = (
        segment_summary["total_net_profit"].round(2)
    )

    segment_summary["average_credit_score"] = (
        segment_summary["average_credit_score"].round(0)
    )

    segment_summary["average_income"] = (
        segment_summary["average_income"].round(2)
    )

    return segment_summary[["segment","total_decisions","average_adjusted_pd_percent","total_expected_loss","total_net_profit","average_credit_score","average_income",]]


# ======================================================
# REASON CODE ANALYSIS
# ======================================================

def parse_reason_codes(value) -> list[str]:
    """
    Convert JSON string reason-code fields into Python lists.
    """

    if value is None:
        return []

    if isinstance(value, list):
        return value

    try:
        parsed = json.loads(value)

        if isinstance(parsed, list):
            return parsed

        return []

    except json.JSONDecodeError:
        return []


def calculate_reason_code_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Count how often each primary reason code appears.
    """

    if df.empty:
        return pd.DataFrame()

    reason_counts: dict[str, int] = {}

    for value in df["primary_reason_codes"]:
        reason_codes = parse_reason_codes(value)

        for reason_code in reason_codes:
            reason_counts[reason_code] = (
                reason_counts.get(reason_code, 0) + 1
            )

    if not reason_counts:
        return pd.DataFrame(
            columns=["reason_code", "count"]
        )

    reason_summary = pd.DataFrame(
        [
            {
                "reason_code": reason_code,
                "count": count,
            }
            for reason_code, count in reason_counts.items()
        ]
    )

    reason_summary = reason_summary.sort_values(
        by="count",
        ascending=False,
    ).reset_index(drop=True)

    return reason_summary


# ======================================================
# DISPLAY FUNCTIONS
# ======================================================

def print_dictionary(
    title: str,
    values: dict,
) -> None:
    """
    Nicely print a dictionary.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    for key, value in values.items():
        print(f"{key}: {value}")


def print_dataframe(
    title: str,
    dataframe: pd.DataFrame,
) -> None:
    """
    Nicely print a DataFrame.
    """

    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)

    if dataframe.empty:
        print("No data available.")
        return

    print(dataframe.to_string(index=False))


# ======================================================
# MAIN RUNNER
# ======================================================

def run_decision_impact_analysis() -> None:
    """
    Run full decision impact analysis.
    """

    df = load_decision_audit_logs()

    portfolio_summary = calculate_portfolio_summary(df)
    decision_breakdown = calculate_decision_breakdown(df)
    segment_summary = calculate_segment_summary(df)
    reason_code_summary = calculate_reason_code_summary(df)

    print_dictionary(
        title="Portfolio Decision Summary",
        values=portfolio_summary,
    )

    print_dataframe(
        title="Decision Breakdown",
        dataframe=decision_breakdown,
    )

    print_dataframe(
        title="Segment Summary",
        dataframe=segment_summary,
    )

    print_dataframe(
        title="Top Primary Reason Codes",
        dataframe=reason_code_summary,
    )


if __name__ == "__main__":
    run_decision_impact_analysis()