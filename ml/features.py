def create_features(data):
    dti = data['loan_amount'] / max(data['income'],1)

    return{
        "credit score":data['credit_score'],
        "income":data['income'],
        "loan_amount":data['loan_amount'],
        "dti":dti
    }