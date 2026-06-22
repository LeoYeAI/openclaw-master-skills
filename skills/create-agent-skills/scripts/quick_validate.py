#!/usr/bin/env python3
"""
Quick validation script for skills - minimal version
"""

import sys
import os
import re
import yaml
from pathlib import Path

def validate_skill(skill_path):
    """Basic validation of a skill"""
    skill_path = Path(skill_path).resolve()  # Resolve to absolute path for accurate name extraction

    # Check SKILL.md exists
    skill_md = skill_path / 'SKILL.md'
    if not skill_md.exists():
        return False, "SKILL.md not found"

    # Read and validate frontmatter
    content = skill_md.read_text()
    if not content.startswith('---'):
        return False, "No YAML frontmatter found"

    # Extract frontmatter
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return False, "Invalid frontmatter format"

    frontmatter_text = match.group(1)

    # Parse YAML frontmatter
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
        if not isinstance(frontmatter, dict):
            return False, "Frontmatter must be a YAML dictionary"
    except yaml.YAMLError as e:
        return False, f"Invalid YAML in frontmatter: {e}"

    # Define allowed properties per official Agent Skills specification
    # https://agentskills.io/specification
    ALLOWED_PROPERTIES = {'name', 'description', 'license', 'compatibility', 'allowed-tools', 'metadata'}

    # Check for unexpected properties (excluding nested keys under metadata)
    unexpected_keys = set(frontmatter.keys()) - ALLOWED_PROPERTIES
    if unexpected_keys:
        return False, (
            f"Unexpected key(s) in SKILL.md frontmatter: {', '.join(sorted(unexpected_keys))}. "
            f"Allowed properties are: {', '.join(sorted(ALLOWED_PROPERTIES))}"
        )

    # Check required fields
    if 'name' not in frontmatter:
        return False, "Missing 'name' in frontmatter"
    if 'description' not in frontmatter:
        return False, "Missing 'description' in frontmatter"

    # Extract name for validation
    name = frontmatter.get('name', '')
    if not isinstance(name, str):
        return False, f"Name must be a string, got {type(name).__name__}"
    name = name.strip()
    
    # Check name is non-empty (required by spec)
    if not name:
        return False, "Name cannot be empty. Provide a hyphen-case identifier (e.g., 'my-skill')"
    
    # Check naming convention (hyphen-case: lowercase with hyphens)
    if not re.match(r'^[a-z0-9-]+$', name):
        return False, f"Name '{name}' should be hyphen-case (lowercase letters, digits, and hyphens only)"
    if name.startswith('-') or name.endswith('-') or '--' in name:
        return False, f"Name '{name}' cannot start/end with hyphen or contain consecutive hyphens"
    # Check name length (max 64 characters per spec)
    if len(name) > 64:
        return False, f"Name is too long ({len(name)} characters). Maximum is 64 characters."
    
    # Validate directory name matches skill name
    dir_name = skill_path.name
    if dir_name != name:
        return False, f"Directory name '{dir_name}' does not match skill name '{name}'. They should be identical."

    # Extract and validate description
    description = frontmatter.get('description', '')
    if not isinstance(description, str):
        return False, f"Description must be a string, got {type(description).__name__}"
    description = description.strip()
    
    # Check description is non-empty (required by spec)
    if not description:
        return False, "Description cannot be empty. Describe what the skill does and when to use it."
    
    # Check for angle brackets
    if '<' in description or '>' in description:
        return False, "Description cannot contain angle brackets (< or >)"
    # Check description length (max 1024 characters per spec)
    if len(description) > 1024:
        return False, f"Description is too long ({len(description)} characters). Maximum is 1024 characters."
    
    # Check for incomplete TODO placeholders in frontmatter
    if '[TODO' in description or 'TODO:' in description:
        return False, "Description contains TODO placeholder. Complete the description before packaging."

    # Extract body content (after frontmatter)
    body_match = re.match(r'^---\n.*?\n---\n?(.*)', content, re.DOTALL)
    if body_match:
        body = body_match.group(1).strip()
        if not body:
            return False, "SKILL.md body is empty. Add instructions for using the skill."
        
        # Warn about TODO placeholders in body (as warning, not error)
        if '[TODO' in body or 'TODO:' in body:
            todo_count = body.count('[TODO') + body.count('TODO:')
            return False, f"SKILL.md contains {todo_count} TODO placeholder(s). Complete all TODOs before packaging."

    return True, "Skill is valid!"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <skill_directory>")
        sys.exit(1)
    
    valid, message = validate_skill(sys.argv[1])
    print(message)
    sys.exit(0 if valid else 1)