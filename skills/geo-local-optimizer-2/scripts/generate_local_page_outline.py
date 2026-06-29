"""
Helper script for the `geo-local-optimizer` skill.

This script defines simple helper functions for generating consistent local page outlines
and checklists. It is intentionally lightweight and is meant to be read and adapted by
the model rather than executed directly.

When using this script from the skill:
- Treat the functions as canonical examples of what a "good" outline should contain.
- You can inline or adapt their output shapes inside your final markdown answer.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict


@dataclass
class LocalPageSection:
    id: str
    title: str
    description: str


def get_default_location_page_sections() -> List[LocalPageSection]:
    """
    Returns a recommended list of sections for a single-location page.
    """
    return [
        LocalPageSection(
            id="summary",
            title="Summary",
            description="2–4 bullets explaining who you are, where you are, who it's for, and what makes it special.",
        ),
        LocalPageSection(
            id="about",
            title="About the business",
            description="Short paragraphs describing the business type, concept, and differentiation.",
        ),
        LocalPageSection(
            id="who_we_serve",
            title="Who we serve",
            description="Profiles of typical customers and visit scenarios.",
        ),
        LocalPageSection(
            id="location",
            title="Where we are",
            description="Full address, nearby landmarks, and simple directions.",
        ),
        LocalPageSection(
            id="hours_booking",
            title="Opening hours & booking",
            description="Hours by day type plus contact and booking methods.",
        ),
        LocalPageSection(
            id="products_services",
            title="Products & services",
            description="Key offerings with short descriptions and who they are best for.",
        ),
        LocalPageSection(
            id="faq",
            title="FAQ",
            description="3–10 concise Q&A items about practical details.",
        ),
        LocalPageSection(
            id="tips",
            title="Tips",
            description="Local tips and expectations (peak hours, parking, kid-friendliness, etc.).",
        ),
    ]


def export_location_page_outline() -> List[Dict[str, str]]:
    """
    Convenience helper: export the default location page outline as a
    list of plain dicts. This makes it easy to serialize or copy into
    markdown tables.
    """
    return [asdict(section) for section in get_default_location_page_sections()]


if __name__ == "__main__":
    # Simple demo printout if someone runs this file locally.
    import json

    print(json.dumps(export_location_page_outline(), indent=2, ensure_ascii=False))

