# Skill classification schema

Use this schema when reviewing or adding a skill.

## Required fields
- name
- description
- primary_domain
- subdomain
- risk_level
- threat_dimensions
- capability_tags

## Optional fields
- secondary_domains
- trigger_keywords
- exclusion_notes
- known_fallbacks
- review_status

## Review checklist
1. What user task triggers this skill?
2. What object does it mainly operate on?
3. Is it read-only, write-capable, or control-capable?
4. Can it send data outside the machine or organization?
5. Can it change permissions, credentials, money, infra, or devices?
6. Is there a narrower existing skill that should be preferred over it?
7. Does it deserve a new subdomain or fit an existing one?
