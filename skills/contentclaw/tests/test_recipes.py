"""Tests for recipe YAML validation."""

from pathlib import Path

import yaml


RECIPES_DIR = Path(__file__).parent.parent / "recipes"
AGENTS_DIR = Path(__file__).parent.parent / "agents"

REQUIRED_FIELDS = ["name", "slug", "version", "status", "priority", "platforms", "blocks"]
VALID_STATUSES = ["wip", "needs-review", "ready", "draft"]
VALID_PRIORITIES = ["p0", "p1", "p2", "p3"]
VALID_PLATFORMS = ["linkedin", "reddit", "x", "email"]
VALID_FORMATS = ["text", "image", "video", "audio"]
VALID_ACTIONS = ["extract-text", "summarize", "generate-title", "extract-key-points", "research-context"]


def load_recipes():
    """Load all recipe YAML files (skip _schema.yaml)."""
    recipes = []
    for path in RECIPES_DIR.glob("*.yaml"):
        if path.name.startswith("_"):
            continue
        with open(path) as f:
            data = yaml.safe_load(f)
        recipes.append((path.name, data))
    return recipes


def test_recipes_exist():
    """At least one recipe exists."""
    recipes = load_recipes()
    assert len(recipes) > 0


def test_required_fields():
    """Every recipe has all required fields."""
    for name, recipe in load_recipes():
        for field in REQUIRED_FIELDS:
            assert field in recipe, f"{name} missing required field: {field}"


def test_slug_matches_filename():
    """Recipe slug matches its filename."""
    for name, recipe in load_recipes():
        expected_slug = name.replace(".yaml", "")
        assert recipe["slug"] == expected_slug, (
            f"{name}: slug '{recipe['slug']}' doesn't match filename '{expected_slug}'"
        )


def test_valid_status():
    """Recipe status is a recognized value."""
    for name, recipe in load_recipes():
        assert recipe["status"] in VALID_STATUSES, (
            f"{name}: invalid status '{recipe['status']}'"
        )


def test_valid_priority():
    """Recipe priority is a recognized value."""
    for name, recipe in load_recipes():
        assert recipe["priority"] in VALID_PRIORITIES, (
            f"{name}: invalid priority '{recipe['priority']}'"
        )


def test_valid_platforms():
    """Recipe platforms are all recognized."""
    for name, recipe in load_recipes():
        for platform in recipe["platforms"]:
            assert platform in VALID_PLATFORMS, (
                f"{name}: invalid platform '{platform}'"
            )


def test_blocks_have_required_fields():
    """Every block has name, format, and agent."""
    for name, recipe in load_recipes():
        for block in recipe["blocks"]:
            assert "name" in block, f"{name}: block missing 'name'"
            assert "format" in block, f"{name}/{block.get('name')}: missing 'format'"
            assert block["format"] in VALID_FORMATS, (
                f"{name}/{block['name']}: invalid format '{block['format']}'"
            )


def test_agent_files_exist():
    """Every referenced agent file exists."""
    for name, recipe in load_recipes():
        for block in recipe["blocks"]:
            agent = block.get("agent")
            if agent:
                agent_path = AGENTS_DIR / agent
                assert agent_path.exists(), (
                    f"{name}/{block['name']}: agent '{agent}' not found at {agent_path}"
                )


def test_prerequisites_valid_actions():
    """All prerequisite actions are recognized."""
    for name, recipe in load_recipes():
        for prereq in recipe.get("prerequisites", []):
            assert prereq["action"] in VALID_ACTIONS, (
                f"{name}: invalid prerequisite action '{prereq['action']}'"
            )


def test_brand_graph_structure():
    """Brand graph config has required and required_layers."""
    for name, recipe in load_recipes():
        bg = recipe.get("brand_graph", {})
        if bg:
            assert "required" in bg, f"{name}: brand_graph missing 'required'"
            assert "required_layers" in bg, f"{name}: brand_graph missing 'required_layers'"


def test_depends_on_references_valid_blocks():
    """Block depends_on references existing block names within the same recipe."""
    for name, recipe in load_recipes():
        block_names = {b["name"] for b in recipe["blocks"]}
        for block in recipe["blocks"]:
            deps = block.get("depends_on")
            if deps:
                for dep in deps:
                    assert dep in block_names, (
                        f"{name}/{block['name']}: depends_on '{dep}' not found in blocks"
                    )
