"""Feature Engineering to build a PD model.
   
This model builds a machine-learning ready database from the relational database

Objective:
Predict whether a approved loan will default or not. 

Target:
target_default = 1 if loan_status = 'defaulted' else 0

only pre-approval/application time features are used to predict the target variable.
Repayment history features are not used h ere because it results in data leakage.

"""
