"""
    This script loads the version control Lending rules for yaml file
    and evaluvates a loan application against the rules.

    It does not make the final decision on the loan application, 
    it returns a policy status and reason codes for decision.py



"""

from pathlib import Path
import yaml
from typing import Any

###################

# POLICY PATH

####################

PROJECT_ROOT = Path(__file__).resolve().parent.parent
POLICY_PATH = (PROJECT_ROOT /"policies"/"credit_policy.yaml")

####################

# LOAD POLICY

####################

def load_policy() -> Any:
    """
    Load the policy from the yaml file.
    """
    with open(POLICY_PATH, "r") as f:
        policy = yaml.safe_load(f)
    return policy


