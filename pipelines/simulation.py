import sqlite3
from db.initt_db import db_path


# -------------------------------
# 1. Helper: Calculate Metrics
# -------------------------------
def calculate_metrics(threshold):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch relevant data
    cursor.execute("""
        SELECT 
            model_risk_score, 
            requested_amount, 
            interest_rate
        FROM loan_applications
    """)

    rows = cursor.fetchall()
    conn.close()

    total = len(rows)
    approved = 0
    total_pd = 0
    total_profit = 0
    total_loss = 0

    for pd, amount, rate in rows:
        total_pd += pd

        # Decision logic
        if pd < threshold:
            approved += 1

            # Simple financial assumptions
            profit = amount * rate
            loss = amount * pd

            total_profit += profit
            total_loss += loss

    approval_rate = approved / total if total > 0 else 0
    avg_pd = total_pd / total if total > 0 else 0
    net_profit = total_profit - total_loss

    return {
        "approval_rate": approval_rate,
        "avg_pd": avg_pd,
        "net_profit": net_profit
    }


# -------------------------------
# 2. Simulation Function
# -------------------------------
def simulate_threshold_change(new_threshold, baseline_threshold=0.5):

    # Baseline metrics
    baseline = calculate_metrics(baseline_threshold)

    # New scenario metrics
    new = calculate_metrics(new_threshold)

    # Calculate changes
    approval_change = new["approval_rate"] - baseline["approval_rate"]
    risk_change = new["avg_pd"] - baseline["avg_pd"]
    profit_change = new["net_profit"] - baseline["net_profit"]

    # Format output
    result = f"""
Simulation Result:

If approval threshold changes from {baseline_threshold:.2f} to {new_threshold:.2f}:

- Approval Rate: {baseline['approval_rate']*100:.2f}% → {new['approval_rate']*100:.2f}% ({approval_change*100:.2f}% change)
- Average Risk (PD): {baseline['avg_pd']:.2f} → {new['avg_pd']:.2f} ({risk_change:.2f} change)
- Net Profit: {baseline['net_profit']:.2f} → {new['net_profit']:.2f} ({profit_change:.2f} change)

Insight:
Lowering the threshold increases approvals but also raises overall risk exposure.
"""

    return result