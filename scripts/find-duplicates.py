#!/usr/bin/env python3
"""Report skills already installed under more than one directory name.

collect.sh only dedups *incoming* candidates, so it cannot see copies that were
imported before that filter existed. As of v0.22.0 there are 83 such groups
covering 174 redundant directories, including a 42-member self-improvement
cluster.

Two skills count as duplicates only when the SKILL.md body, the frontmatter
`name` and the frontmatter `description` are all identical. Body-only matching
overcounts: the CreditClaw vendor skill ships one body under shop / stripe /
payment / amazon-checkout, each with its own name and description, which are
deliberate discovery aliases rather than accidents.

Read-only. Prints a report and exits 0; use --json for machine-readable output
and --strict to exit 1 when any duplicate group is found. The report also lists
name collisions: directories with different bodies that share a frontmatter
name, which cannot be collapsed but do make name-keyed lookups ambiguous.
"""

import argparse
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / 'skills'
README = REPO_ROOT / 'README.md'

# A row of the curated table in README.md: | [`slug`](skills/slug/) | desc |
CURATED_ROW = re.compile(r'^\|\s*\[`[^`]+`\]\(skills/([^)/]+)/\)\s*\|')

# Personal forks, numbered re-uploads and scratch names. Used only to pick which
# member of a group is canonical, never to delete anything.
#
# Markers must match anywhere in the slug, not just as a whole name or suffix:
# anchoring them let slug-wk, temp-skill-download and hsa-test3 win their groups
# over skill-creator-0-1-0 and ezviz-open-multimodal-analysis.
JUNK_NAME = re.compile(
    r'(^\d+$'
    r'|^(hi|aaaa|meng|pro|lex)$'
    r'|(^|-)(test|tmp|temp|bak|backup|old|copy|scratch|demo|sample|foo|bar)\d*(-|$)'
    r'|\d{4,}'
    r'|-v?\d+(-\d+)*$'
    r'|-(local|zh|custom|install|main|conflict)$)'
)

FRONTMATTER = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.S)
MIN_BODY = 200


def frontmatter_field(block, key):
    m = re.search(rf'^{key}:\s*(.+?)(?=\n[a-zA-Z_]+:|\Z)', block, re.M | re.S)
    if not m:
        return ''
    value = ' '.join(m.group(1).strip().split())
    value = re.sub(r'^[>|][+\-]?\s*', '', value)
    if len(value) >= 2 and value[0] == value[-1] and value[0] in '"\'':
        value = value[1:-1]
    return value.strip().strip('"\'').strip()


def load_curated():
    """Directory slugs listed in README.md's curated table.

    A name collision between two mirror forks (`agent-browser-5` vs
    `agent-browser-6`) is expected in a collection assembled from thousands of
    publishers. A collision between two rows of the curated table is different:
    that table is the index a user reads and installs from, so both spellings
    are advertised and whichever loads second wins. Separating the two lets the
    report lead with the part that reaches users.

    Returns an empty set if README.md is missing, so the check degrades to its
    previous repo-wide behaviour rather than failing.
    """
    if not README.is_file():
        return set()
    out = set()
    for line in README.read_text(encoding='utf-8', errors='replace').splitlines():
        m = CURATED_ROW.match(line)
        if m:
            out.add(m.group(1))
    return out


def load_skills():
    out = {}
    for d in sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir()):
        for fn in ('SKILL.md', 'skill.md'):
            f = d / fn
            if f.is_file():
                break
        else:
            continue
        text = f.read_text(encoding='utf-8', errors='ignore')
        m = FRONTMATTER.match(text)
        block = m.group(1) if m else ''
        body = FRONTMATTER.sub('', text, count=1).strip()
        if len(body) < MIN_BODY:
            continue  # stubs are not worth reporting as duplicates
        out[d.name] = {
            'hash': hashlib.sha1(body.encode()).hexdigest(),
            'name': frontmatter_field(block, 'name'),
            'description': frontmatter_field(block, 'description'),
        }
    return out


def name_affinity(slug, fm_name):
    """(tier, -overlap) describing how well a directory reflects the shared name.

    Groups often contain no directory equal to the frontmatter name (the
    skill-creator group has slug-wk and skill-creator-0-1-0 but no bare
    skill-creator), so exact matching alone is not enough.

    Tier 0 exact, 1 substring, 2 shared tokens, 3 unrelated.
    """
    if not fm_name:
        return (3, 0.0)
    if slug == fm_name:
        return (0, 0.0)
    if fm_name in slug or slug in fm_name:
        return (1, 0.0)
    slug_tokens = set(re.split(r'[-_]', slug))
    name_tokens = set(re.split(r'[-_]', fm_name))
    shared = slug_tokens & name_tokens
    if shared:
        return (2, -len(shared) / max(len(name_tokens), 1))
    return (3, 0.0)


def rank(slug, meta, group):
    """Lower sorts first. The winner is proposed as canonical.

    Affinity to the frontmatter name is the primary key and the junk marker is
    only a tie-break inside the same tier. Scoring them on one additive scale
    let a +50 version-suffix penalty beat a -40 substring match, so
    wangkang-skill-c won over skill-creator-0-1-0.
    """
    tier, overlap = name_affinity(slug, meta['name'])
    sibling_is_canonical = bool(
        meta['name'] and slug != meta['name'] and meta['name'] in group
    )
    return (
        tier,
        overlap,
        1 if sibling_is_canonical else 0,
        1 if JUNK_NAME.search(slug) else 0,
        len(slug),
        slug,
    )


def find_groups(skills):
    buckets = collections.defaultdict(list)
    for slug, meta in skills.items():
        buckets[(meta['hash'], meta['name'], meta['description'])].append(slug)

    groups = []
    for members in buckets.values():
        if len(members) < 2:
            continue
        ordered = sorted(members, key=lambda s: rank(s, skills[s], members))
        groups.append({'keep': ordered[0], 'redundant': ordered[1:]})
    groups.sort(key=lambda g: (-len(g['redundant']), g['keep']))
    return groups


def find_name_collisions(skills, groups):
    """Frontmatter names claimed by more than one surviving directory.

    Distinct from a duplicate group: these have different bodies, so collapsing
    them would lose content. They still matter because anything that keys on the
    frontmatter name rather than the directory (a loader, an index, a registry)
    has to pick one arbitrarily. 155 names are shared by 451 directories, led by
    50 directories all calling themselves self-improvement.

    Directories that are already reported as redundant are excluded, so this
    counts only collisions that survive a full duplicate cleanup.

    Each collision records whether more than one of its directories appears in
    README.md's curated table (`curated`). Those are the ones a user can hit
    from the published index: both spellings are advertised as separate skills,
    yet a name-keyed loader can only resolve one.
    """
    redundant = {s for g in groups for s in g['redundant']}
    by_name = collections.defaultdict(list)
    for slug, meta in skills.items():
        if slug in redundant or not meta['name']:
            continue
        by_name[meta['name']].append(slug)
    curated = load_curated()
    out = []
    for n, v in by_name.items():
        if len(v) < 2:
            continue
        dirs = sorted(v)
        in_curated = sorted(s for s in dirs if s in curated)
        out.append({'name': n, 'dirs': dirs, 'curated_dirs': in_curated,
                    'curated': len(in_curated) > 1})
    # Collisions inside the curated table first: those are the ones a user can
    # actually hit from the published index.
    out.sort(key=lambda c: (not c['curated'], -len(c['dirs']), c['name']))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 if duplicates exist')
    args = ap.parse_args()

    skills = load_skills()
    groups = find_groups(skills)
    redundant = sum(len(g['redundant']) for g in groups)
    collisions = find_name_collisions(skills, groups)
    colliding_dirs = sum(len(c['dirs']) for c in collisions)
    curated_collisions = [c for c in collisions if c['curated']]

    if args.json:
        print(json.dumps({'scanned': len(skills), 'groups': groups,
                          'redundant': redundant,
                          'name_collisions': collisions,
                          'curated_name_collisions': len(curated_collisions)},
                         indent=2, ensure_ascii=False))
    else:
        print(f'scanned {len(skills)} skills with a real body')
        print(f'duplicate groups: {len(groups)}  redundant directories: {redundant}')
        if groups:
            print(f'collapsing them would leave '
                  f'{len(list(SKILLS_DIR.iterdir())) - redundant} skills\n')
            for g in groups:
                print(f"  keep {g['keep']}  ({len(g['redundant'])} redundant)")
                print(f"       {', '.join(g['redundant'])}")
        print(f'\nname collisions after cleanup: {len(collisions)} names '
              f'across {colliding_dirs} directories')
        print('  (different bodies, same frontmatter name: not safe to collapse)')
        # Lead with the collisions a user can hit from the published table.
        print(f'curated-index collisions: {len(curated_collisions)} names where '
              f'2+ colliding directories are both listed in README.md')
        for c in curated_collisions:
            print(f"  {c['name']}")
            print(f"        {', '.join(c['curated_dirs'])}")
        rest = [c for c in collisions if not c['curated']]
        if rest:
            print(f'\nmirror-only collisions: {len(rest)} names '
                  f'(at most one side is in the curated index)')
            for c in rest[:10]:
                shown = ', '.join(c['dirs'][:6])
                more = (f" (+{len(c['dirs']) - 6} more)"
                        if len(c['dirs']) > 6 else '')
                print(f"  {len(c['dirs']):3}x  {c['name']}")
                print(f"        {shown}{more}")
            if len(rest) > 10:
                print(f'  ... {len(rest) - 10} more names')

    return 1 if (args.strict and groups) else 0


if __name__ == '__main__':
    sys.exit(main())
