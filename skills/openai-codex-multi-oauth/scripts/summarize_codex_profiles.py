#!/usr/bin/env python3
import argparse
import base64
import json
from datetime import datetime
from pathlib import Path
from typing import Any


DEFAULT_ACTIVE_SLOT_ID = 'openai-codex:default'


def load_json(path: Path | None):
    if path is None or not path.exists():
        return None
    with path.open('r', encoding='utf-8') as f:
        return json.load(f)


def decode_email(profile: dict[str, Any] | None):
    access = (profile or {}).get('access')
    if not isinstance(access, str) or access.count('.') < 2:
        return None
    try:
        payload = access.split('.')[1]
        payload += '=' * (-len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload.encode()).decode())
        return ((decoded.get('https://api.openai.com/profile') or {}).get('email'))
    except Exception:
        return None


def profile_signature(profile: dict[str, Any] | None):
    if not isinstance(profile, dict):
        return None
    return (
        profile.get('accountId'),
        profile.get('workspaceName') or profile.get('workspaceId') or profile.get('workspace'),
        profile.get('access'),
        profile.get('refreshToken'),
    )


def default_paths(
    state_dir: Path,
    agent: str,
    repo_path: str | None,
    helper_path: str | None,
    router_path: str | None,
):
    return {
        'saved': state_dir / 'codex_profile_id',
        'repo': Path(repo_path).expanduser() if repo_path else state_dir / 'codex-oauth-profiles.json',
        'helper': Path(helper_path).expanduser() if helper_path else state_dir / 'codex_profile',
        'router': Path(router_path).expanduser() if router_path else None,
        'auth': state_dir / 'agents' / agent / 'agent' / 'auth-profiles.json',
        'sessions': state_dir / 'agents' / agent / 'sessions' / 'sessions.json',
    }


def load_repo(paths: dict[str, Path | None], auth: dict[str, Any]):
    repo = load_json(paths['repo'])
    if isinstance(repo, dict):
        return repo
    profiles = {
        pid: cred
        for pid, cred in ((auth.get('profiles') or {}).items())
        if isinstance(pid, str) and pid.startswith('openai-codex:') and isinstance(cred, dict)
    }
    return {'profiles': profiles}


def detect_active_profile_id(auth: dict[str, Any], repo: dict[str, Any], active_slot_id: str):
    active = ((auth.get('profiles') or {}).get(active_slot_id))
    active_sig = profile_signature(active)
    if active_sig is None:
        return None
    for pid, profile in (repo.get('profiles') or {}).items():
        if not isinstance(pid, str) or not pid.startswith('openai-codex:'):
            continue
        if profile_signature(profile) == active_sig:
            return pid
    return None


def summarize_profiles(auth: dict[str, Any], repo: dict[str, Any]):
    profiles: list[dict[str, Any]] = []
    repo_profiles = repo.get('profiles') or {}
    auth_profiles = auth.get('profiles') or {}
    seen = set(repo_profiles) | {pid for pid in auth_profiles if str(pid).startswith('openai-codex:')}
    for pid in sorted(seen):
        source = repo_profiles.get(pid) or auth_profiles.get(pid) or {}
        token = source.get('access') or source.get('token')
        token_state = None
        if isinstance(token, str):
            token_state = 'jwt-like' if token.startswith('eyJ') else 'non-jwt'
        profiles.append({
            'profileId': pid,
            'accountId': source.get('accountId'),
            'email': source.get('email') or decode_email(source),
            'workspace': source.get('workspaceName') or source.get('workspaceId') or source.get('workspace'),
            'type': source.get('type'),
            'lastGood': source.get('lastGood'),
            'tokenState': token_state,
        })
    return profiles


def summarize_recent_sessions(sessions: dict[str, Any], limit: int, agent: str):
    items = []
    prefix = f'agent:{agent}:'
    for key, entry in sessions.items():
        if not isinstance(entry, dict):
            continue
        if not str(key).startswith(prefix):
            continue
        if ':subagent:' in str(key) or ':cron:' in str(key):
            continue
        items.append({
            'key': key,
            'updatedAt': int(entry.get('updatedAt') or 0),
            'channel': (entry.get('deliveryContext') or {}).get('channel') or entry.get('lastChannel') or (entry.get('origin') or {}).get('provider'),
            'chatType': entry.get('chatType') or (entry.get('origin') or {}).get('chatType'),
            'target': (entry.get('deliveryContext') or {}).get('to') or entry.get('lastTo') or (entry.get('origin') or {}).get('to'),
            'modelProvider': entry.get('modelProvider') or entry.get('providerOverride'),
            'model': entry.get('model'),
            'authProfileOverride': entry.get('authProfileOverride'),
            'authProfileOverrideSource': entry.get('authProfileOverrideSource'),
        })
    items.sort(key=lambda item: (item['updatedAt'], item['key']), reverse=True)
    return items[: max(1, limit)]


def format_ms(value: int | None):
    if not value:
        return '-'
    try:
        return datetime.fromtimestamp(value / 1000).isoformat(sep=' ', timespec='seconds')
    except Exception:
        return str(value)


def path_info(path: Path | None):
    if path is None:
        return None
    return {
        'path': str(path),
        'exists': path.exists(),
    }


def summarize(
    state_dir: Path,
    agent: str,
    session_key: str | None,
    recent_sessions_limit: int,
    active_slot_id: str,
    repo_path: str | None,
    helper_path: str | None,
    router_path: str | None,
):
    paths = default_paths(state_dir, agent, repo_path, helper_path, router_path)
    auth = load_json(paths['auth']) or {}
    sessions = load_json(paths['sessions']) or {}
    repo = load_repo(paths, auth)
    saved_profile = paths['saved'].read_text(encoding='utf-8').strip() if paths['saved'].exists() else None
    auth_order = ((auth.get('order') or {}).get('openai-codex') or [])
    active_profile = detect_active_profile_id(auth, repo, active_slot_id)
    explicit_session = None
    if session_key:
        entry = sessions.get(session_key)
        if entry:
            explicit_session = {
                'key': session_key,
                'updatedAt': int(entry.get('updatedAt') or 0),
                'channel': (entry.get('deliveryContext') or {}).get('channel') or entry.get('lastChannel') or (entry.get('origin') or {}).get('provider'),
                'chatType': entry.get('chatType') or (entry.get('origin') or {}).get('chatType'),
                'target': (entry.get('deliveryContext') or {}).get('to') or entry.get('lastTo') or (entry.get('origin') or {}).get('to'),
                'modelProvider': entry.get('modelProvider') or entry.get('providerOverride'),
                'model': entry.get('model'),
                'authProfileOverride': entry.get('authProfileOverride'),
                'authProfileOverrideSource': entry.get('authProfileOverrideSource'),
            }

    return {
        'stateDir': str(state_dir),
        'agent': agent,
        'activeSlotId': active_slot_id,
        'savedProfile': saved_profile,
        'activeProfileId': active_profile,
        'authOrder': auth_order,
        'profiles': summarize_profiles(auth, repo),
        'recentSessions': summarize_recent_sessions(sessions, recent_sessions_limit, agent),
        'session': explicit_session,
        'paths': {
            name: path_info(path)
            for name, path in paths.items()
        },
    }


def print_human(summary: dict[str, Any]):
    print(f"state_dir: {summary['stateDir']}")
    print(f"agent: {summary['agent']}")
    print(f"active_slot_id: {summary['activeSlotId']}")
    print(f"saved_profile: {summary['savedProfile'] or '<missing>'}")
    print(f"active_profile: {summary['activeProfileId'] or '<unresolved>'}")
    print('auth_order:', ', '.join(summary['authOrder']) if summary['authOrder'] else '<none>')
    print('profiles:')
    if not summary['profiles']:
        print('  <none>')
    for item in summary['profiles']:
        print(
            '  - '
            f"{item['profileId']} | "
            f"accountId={item['accountId'] or '-'} | "
            f"email={item['email'] or '-'} | "
            f"workspace={item['workspace'] or '-'} | "
            f"type={item['type'] or '-'} | "
            f"token={item['tokenState'] or '-'} | "
            f"lastGood={item['lastGood'] or '-'}"
        )
    print('recent_sessions:')
    if not summary['recentSessions']:
        print('  <none>')
    for item in summary['recentSessions']:
        print(
            '  - '
            f"{item['key']} | "
            f"channel={item['channel'] or '-'} | "
            f"chatType={item['chatType'] or '-'} | "
            f"target={item['target'] or '-'} | "
            f"modelProvider={item['modelProvider'] or '-'} | "
            f"authProfileOverride={item['authProfileOverride'] or '-'} | "
            f"source={item['authProfileOverrideSource'] or '-'} | "
            f"updated={format_ms(item['updatedAt'])}"
        )
    if summary['session']:
        s = summary['session']
        print('session:')
        print(f"  key: {s['key']}")
        print(f"  channel: {s['channel'] or '-'}")
        print(f"  chatType: {s['chatType'] or '-'}")
        print(f"  target: {s['target'] or '-'}")
        print(f"  modelProvider: {s['modelProvider'] or '-'}")
        print(f"  model: {s['model'] or '-'}")
        print(f"  authProfileOverride: {s['authProfileOverride'] or '-'}")
        print(f"  authProfileOverrideSource: {s['authProfileOverrideSource'] or '-'}")
        print(f"  updated: {format_ms(s['updatedAt'])}")
    print('paths:')
    for name, info in summary['paths'].items():
        if info is None:
            print(f'  {name}: <unset>')
        else:
            print(f"  {name}: {info['path']} ({'exists' if info['exists'] else 'missing'})")


def main():
    parser = argparse.ArgumentParser(description='Summarize OpenClaw Codex multi-OAuth state.')
    parser.add_argument('--state-dir', default='~/.openclaw', help='OpenClaw state directory (default: ~/.openclaw)')
    parser.add_argument('--agent', default='main', help='Agent id to inspect (default: main)')
    parser.add_argument('--session-key', default=None, help='Optional exact session key from sessions.json')
    parser.add_argument('--recent-sessions', type=int, default=6, help='Number of recent user-facing sessions to print (default: 6)')
    parser.add_argument('--active-slot-id', default=DEFAULT_ACTIVE_SLOT_ID, help='Active slot profile id for external-router setups (default: openai-codex:default)')
    parser.add_argument('--repo-path', default=None, help='Optional external profile repo path (for external-router setups)')
    parser.add_argument('--helper-path', default=None, help='Optional local helper command path')
    parser.add_argument('--router-path', default=None, help='Optional router script path')
    parser.add_argument('--json', action='store_true', help='Print JSON instead of human-readable output')
    args = parser.parse_args()

    summary = summarize(
        Path(args.state_dir).expanduser(),
        args.agent,
        args.session_key,
        args.recent_sessions,
        args.active_slot_id,
        args.repo_path,
        args.helper_path,
        args.router_path,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print_human(summary)


if __name__ == '__main__':
    main()
