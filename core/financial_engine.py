""" This function is used to calculate the expected loss and expected profit...."""

def calculate_finances(pd, loan_amount,interest_rate):
    # for calculating expected loss, we would be using pd, LGD and  interest rate....
    # for calculating expected profit, we would be using the other logic of probabaility of default and income and interest rate.....
    # What is LGD = Loss given default  ( tells about the probability of loss by the lender from the borrower getting defaulted...)

    LGD = 0.6 # which is just assuming for our project....
    cost_of_captial = 0.02*loan_amount # which is also assuming for our project....
    pd = float(pd)
    loan_amount = float(loan_amount)
    interest_rate = float(interest_rate)
    expected_loss = pd*loan_amount*LGD
    expected_profit = loan_amount*interest_rate*round((1-pd),2)
    # expected_cost = cost_of_captial*loan_amount

    net_profit = expected_profit - expected_loss - cost_of_captial
    net_profit = float(round(net_profit,2))

    return expected_profit,expected_loss,cost_of_captial,net_profit