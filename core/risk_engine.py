def calculate_pd(credit_score,income):
    credit_factor = (850-credit_score)/550
    income_factor  = 1 - min(income/10000 , 1)
    pd = 0.6*credit_factor + 0.4*income_factor
    return round(pd,2)

