import sys
from pathlib import Path
import numpy as np
import pytest

ML_DIR = Path(__file__).parent.parent.parent / "ml"
sys.path.insert(0, str(ML_DIR))

from data_pipeline import json_events_to_numpy, load_json_data  # noqa: E402

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
