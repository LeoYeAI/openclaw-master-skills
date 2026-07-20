"""Make emotion_model importable by adding parent to sys.path."""
import sys
from pathlib import Path

# Add the repo root (parent of emotion_model/) to sys.path so that
# "import emotion_model" resolves correctly.
parent = Path(__file__).parent.parent
if str(parent) not in sys.path:
    sys.path.insert(0, str(parent))
