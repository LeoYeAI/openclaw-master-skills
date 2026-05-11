"""Tests for image generation (spec-to-prompt conversion only, no API calls)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.generate_image import spec_to_prompt


def test_infographic_spec_to_prompt():
    """Infographic spec produces a prompt with key content."""
    spec = {
        "title": "Test Infographic",
        "subtitle": "A test subtitle",
        "sections": [
            {"heading": "Point 1", "content": "Detail 1", "visual_hint": "chart"},
            {"heading": "Point 2", "content": "Detail 2", "visual_hint": "icon"},
        ],
        "source": "Test Source",
        "style": {
            "layout": "vertical-flow",
            "primary_color": "#4A90E2",
            "accent_color": "#E94E77",
            "tone": "professional",
        },
    }
    prompt = spec_to_prompt(spec)
    assert "Test Infographic" in prompt
    assert "Point 1" in prompt
    assert "Point 2" in prompt
    assert "infographic" in prompt.lower()
    assert "professional" in prompt


def test_diagram_spec_to_prompt():
    """Diagram spec produces a prompt with components and connections."""
    spec = {
        "title": "System Architecture",
        "diagram_type": "pipeline",
        "components": [
            {"label": "Input", "description": "Raw data"},
            {"label": "Process", "description": "Transform"},
        ],
        "connections": [
            {"from": "Input", "to": "Process", "label": "feeds"},
        ],
        "style": {"tone": "technical"},
    }
    prompt = spec_to_prompt(spec)
    assert "pipeline" in prompt.lower()
    assert "Input" in prompt
    assert "Process" in prompt
    assert "feeds" in prompt


def test_poster_spec_to_prompt():
    """Poster spec produces a prompt with headline and CTA."""
    spec = {
        "title": "Big Event 2026",
        "details": ["March 20", "San Francisco", "Free entry"],
        "call_to_action": "Register now",
        "style": {"layout": "poster", "tone": "casual"},
    }
    prompt = spec_to_prompt(spec)
    assert "Big Event 2026" in prompt
    assert "Register now" in prompt
    assert "poster" in prompt.lower()


def test_empty_spec():
    """Empty spec doesn't crash."""
    prompt = spec_to_prompt({})
    assert isinstance(prompt, str)
    assert len(prompt) > 0


def test_spec_with_brand_colors():
    """Brand colors appear in the prompt."""
    spec = {
        "title": "Branded Content",
        "style": {
            "primary_color": "#FF0000",
            "accent_color": "#00FF00",
            "tone": "professional",
        },
    }
    prompt = spec_to_prompt(spec)
    assert "#FF0000" in prompt
    assert "#00FF00" in prompt
