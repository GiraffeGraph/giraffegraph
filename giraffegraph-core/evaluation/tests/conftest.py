"""Make the standalone kit importable and locate the read-only pilot artefacts."""
import os
import sys
from pathlib import Path

import pytest

EVAL_DIR = Path(__file__).resolve().parents[1]
for p in (EVAL_DIR, EVAL_DIR / "annotation"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

# The pilot lives outside this repo, in the workspace that contains it.
PILOT_DIR = Path(
    os.environ.get("GIRAFFEGRAPH_PILOT_DIR", EVAL_DIR.parents[1] / "claude-science-results")
)


@pytest.fixture(scope="session")
def pilot_sample_path():
    path = PILOT_DIR / "pilot_sample.json"
    if not path.is_file():
        pytest.skip(f"pilot sample not found: {path}")
    return path


@pytest.fixture(scope="session")
def pilot_script_path():
    path = PILOT_DIR / "pilot_isnad.py"
    if not path.is_file():
        pytest.skip(f"pilot script not found: {path}")
    return path
