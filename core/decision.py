""" This code is for making decision to approve or review or reject based on the pd and various factors..."""

def make_decision(pd, net_profit):
    net_profit = float(net_profit)
    if pd<0.3 and net_profit>0:
        return "APPROVE"
    elif pd>=0.3 and pd<=0.6:
        return "REVIEW"
    else:
        return "REJECT"