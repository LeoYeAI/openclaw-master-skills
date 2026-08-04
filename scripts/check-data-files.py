#!/usr/bin/env python3
r"""Report shipped .json / .yaml files that no parser will accept.

Extension of check-syntax.py (which covers .py and .sh) to the data files a
skill's own code reads at runtime. A malformed config.json breaks for every user
on every platform, the same universal failure, provable the same way.

Getting the parsers right matters more than the scan here. A naive pass over
3870 files reported 16 findings and 14 were the checker's fault:

  * tsconfig.json is JSONC by convention -- // comments and trailing commas are
    legal and the TypeScript compiler accepts them. Strip comments before
    judging any .json whose name says JSONC.
  * Multi-document YAML ('---' separators) is valid YAML. yaml.safe_load
    rejects a second document; safe_load_all is the correct call.
  * A .json holding one object per line is JSONL, which fails as a single
    document and parses fine line by line.
  * Files carrying {{placeholder}} markers are templates, so being invalid is
     the point.
  * A leading '---' block followed by markdown prose is frontmatter, the same
    shape as SKILL.md. Parse only the block, not the body.
  * Some .yml files are pure markdown under a YAML name (a FUNDING.yml written
    as a sponsor page). Wrong extension, not a broken parse, and no user hits a
    failure over it.

One genuine defect survived that filtering (ka88-agent-shield's patterns.yaml,
fixed in 906b0fdb). Report-only, for a reason worth recording: deciding whether
a malformed data file actually matters requires knowing if anything loads it,
and that cannot be answered by grepping for the filename. patterns.yaml is
named in quick-scan.sh only as an unused variable assignment, and
cann-review/skill.yaml appears solely inside a comment. A filename mention is
not a load, so this gate reports and leaves the judgement to a human.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

TEMPLATE = re.compile(r'\{\{[^}]+\}\}|<<<[A-Z_]+>>>|YOUR_[A-Z_]+_HERE|'
                      r'__[A-Z]+_PLACEHOLDER__|\{%[^%]+%\}|'
                      # A bracketed placeholder standing in for a key name,
                      # e.g. an OpenAPI skeleton whose schema is "[resource]:".
                      r'^\s*\[[^\]\n]{1,40}\]\s*:', re.M)

# A markdown heading or fenced block at the start of a line: prose, not YAML.
MARKDOWN_BODY = re.compile(r'^(#{1,6} |```|\[!\[|\| )', re.M)


def frontmatter(text: str):
    """Return the YAML frontmatter block if the file is '---' + markdown body.

    Files shaped like SKILL.md (a delimited YAML header followed by prose) are
    valid; only the header is meant to parse.
    """
    if not text.startswith('---'):
        return None
    end = re.search(r'^---\s*$', text[3:], re.M)
    if not end:
        return None
    head = text[3:3 + end.start()]
    body = text[3 + end.end():]
    return head if MARKDOWN_BODY.search(body) else None


# Names conventionally parsed as JSONC (comments + trailing commas allowed).
JSONC_NAME = re.compile(r'^(tsconfig|jsconfig)(\..+)?\.json$|^\.eslintrc\.json$'
                        r'|^devcontainer\.json$')


def strip_jsonc(text: str) -> str:
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)
    text = re.sub(r'(^|[^:"\w])//[^\n]*', r'\1', text)
    return re.sub(r',(\s*[}\]])', r'\1', text)


def main():
    if not (REPO_ROOT / '.git').exists():
        print('not a git repository; skipping data-file check')
        return 0

    try:
        import yaml
    except ImportError:
        yaml = None

    tracked = subprocess.run(['git', 'ls-files', 'skills'], cwd=REPO_ROOT,
                             capture_output=True, text=True,
                             check=True).stdout.split('\n')

    broken = []
    skipped = {'template': 0, 'jsonc': 0, 'jsonl': 0, 'multidoc': 0,
               'frontmatter': 0, 'markdown': 0}
    n = 0

    for rel in tracked:
        if not rel:
            continue
        p = Path(rel)
        ext = p.suffix.lower()
        if ext not in {'.json', '.yaml', '.yml'}:
            continue
        try:
            text = (REPO_ROOT / rel).read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            continue
        n += 1
        if not text.strip():
            continue

        err = None
        if ext == '.json':
            try:
                json.loads(text)
            except json.JSONDecodeError as e:
                if JSONC_NAME.match(p.name):
                    try:
                        json.loads(strip_jsonc(text))
                        skipped['jsonc'] += 1
                        continue
                    except json.JSONDecodeError:
                        pass
                # Markdown under a .json name: wrong extension, not a defect
                # any user trips over.
                if MARKDOWN_BODY.match(text.lstrip()[:80] or ' '):
                    skipped['markdown'] += 1
                    continue
                rows = [l for l in text.split('\n') if l.strip()]
                if len(rows) > 1:
                    try:
                        for row in rows:
                            json.loads(row)
                        skipped['jsonl'] += 1
                        continue
                    except json.JSONDecodeError:
                        pass
                err = f'line {e.lineno}: {e.msg}'
        elif yaml is not None:
            try:
                list(yaml.safe_load_all(text))
            except Exception as e:
                head = frontmatter(text)
                if head is not None:
                    try:
                        yaml.safe_load(head)
                        skipped['frontmatter'] += 1
                        continue
                    except Exception:
                        pass
                # Pure markdown under a .yml name: wrong extension, not a
                # parse defect anyone hits at runtime.
                if MARKDOWN_BODY.match(text.lstrip()[:80] or ' '):
                    skipped['markdown'] += 1
                    continue
                err = ' '.join(str(e).split())[:120]

        if err is None:
            continue
        if TEMPLATE.search(text):
            skipped['template'] += 1
            continue
        broken.append((rel, err))

    print(f'checked {n} json/yaml files under skills/')
    print(f'unparseable data files: {len(broken)}')
    print(f'  excluded: {skipped["template"]} templates, {skipped["jsonc"]} jsonc, '
          f'{skipped["jsonl"]} jsonl, {skipped["frontmatter"]} frontmatter+prose, '
          f'{skipped["markdown"]} markdown-misnamed')

    for rel, err in broken:
        print(f'  {rel}')
        print(f'      {err}')

    if broken:
        print('\nReport-only: whether a malformed data file matters depends on '
              'something loading it, and a filename mention in code is not a '
              'load.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
