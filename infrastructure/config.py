# infrastructure/config.py

from pathlib import Path

# Project Root
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/business.db"

# ML
RANDOM_STATE = 42
TEST_SIZE = 0.2

# Decision Engine
DEFAULT_APPROVAL_THRESHOLD = 0.35

# Logging
LOG_LEVEL = "INFO"
