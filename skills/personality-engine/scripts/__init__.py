"""Personality Engine — 6-system behavior framework for OpenClaw agents."""

__version__ = "1.0.0"
__author__ = "KingMadeLLC"

from .engine import PersonalityEngine
from .editorial_voice import EditorialVoice
from .selective_silence import SelectiveSilence
from .variable_timing import VariableTiming
from .micro_initiations import MicroInitiations
from .context_buffer import ContextBuffer
from .response_tracker import ResponseTracker

__all__ = [
    "PersonalityEngine",
    "EditorialVoice",
    "SelectiveSilence",
    "VariableTiming",
    "MicroInitiations",
    "ContextBuffer",
    "ResponseTracker",
]
