# Import shared types - do not redefine these locally.
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "shared_schemas"))
from models import Case, Charge, EligibilityResult  # noqa
