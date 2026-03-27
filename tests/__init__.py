"""
Floramigo test suite.

Run all tests with: pytest tests/ -v
Run with coverage: pytest tests/ -v --cov=floramigo --cov=api
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
