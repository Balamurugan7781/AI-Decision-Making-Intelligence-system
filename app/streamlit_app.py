import streamlit as st
import math

from ml.predict import predict
from core.risk_engine import calculate_pd
from core.decision import make_decision
# This script is for Frontend implementation....

st.title("AI FinTech Decision Intelligence system")


st.write("This system evaluvates loan applications based on Credit risk and Profitability")

# Now asking User details....

st.header("Enter the Loan Details")

# these are the inputs....

income = st.number_input(" Enter the user income.... (£)",min_value=1000, value=30000)
loan_amount = st.number_input(" Loan Amount (£)",min_value=500, value=10000)
interest_rate = st.slider("Interest rate %",1,2,10)/100
credit_score = st.slider("Credit Score ",300,850,650)



#  Risk Model (PD) calculation
"""
def calculate_pd(credit_Score,income):
    credit_factor = (850 - credit_Score)/550
    income_factor = 1/(1+income/5000)
    pd = 0.6*credit_factor + 0.4*income_factor
    # this line would be returning PD....
    return max(0,min(pd,1))


# now creating decision logic.....

def make_decision(pd, loan_amount,interest_rate):
     This function is created check if the loan needs to be approved based on the threshold of PD. 
        We are creating 3 classes to label our loan application. Instead of 2 classes, sometimes overlabelling leads us to a loss of business values in future.
    expected_profit = loan_amount*interest_rate*(1-pd)
    expected_loss = pd* loan_amount
    if pd < 0.3 and expected_profit>expected_loss:  # the second condition is more important in 
        decision= "APPROVE"
    elif pd>0.6:
        decision="REJECT"
    else:
        decision="REVIEW"

    return decision,expected_profit,expected_loss

"""


# Run Model......

if st.button("Evaluvate Loan"):
    pd = calculate_pd(credit_score,loan_amount)
    decision,profit,loss = make_decision(pd,loan_amount,interest_rate)

    # Output section....

    st.header("📊 Results")
    # PD value.....
    st.write(f"**Probability of Default (PD):**",{round(pd,2)})
    st.write(f"** Expected Loss:**",{round(loss,2)})
    st.write(f"** Expected Profit:**",{round(profit,2)})


    # Decision Display.....
    
    if decision == "APPROVE":
        st.success(f"Decision: {decision}")
    elif decision == "REVIEW":
        st.warning(f"Decision: {decision}")
    else:
        st.error(f"Decision: {decision}")



# Here comes the game changing part.....
 # Explanaiability.....
    st.subheader("Why this decision? 🧠")
    st.write("DEBUG")
    st.write(f"PD:{pd}")
    st.write(f"Expected Loss:{loss}")
    st.write(f"Expected Profit:{profit}")
    if decision=="REJECT":
        st.write("High risk due to low income or credit score.💣📉")
    elif decision=="APPROVE":
        st.write("Low risk and ready to approve the loan. 🥳📈")
    else:
        st.write("This needs human review to work better. 👀🧐")
