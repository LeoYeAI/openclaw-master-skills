#!/usr/bin/env python3
import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = SKILL_ROOT / 'state.json'
DEFAULT_BASE = os.environ.get('CW_BASE_URL', 'http://127.0.0.1:18080')
DEFAULT_AGENT_ID = os.environ.get('CW_AGENT_ID', 'agent')
DEFAULT_DISPLAY_NAME = os.environ.get('CW_DISPLAY_NAME', 'Agent')
DEFAULT_OWNER_ID = os.environ.get('CW_OWNER_ID', 'owner')

CW_CONTINUE_DASH_RE = re.compile(r'^cw-continue-(\d+)$', re.IGNORECASE)
CW_MAX_DASH_RE = re.compile(r'^cw-max-(\d+)$', re.IGNORECASE)


def default_state():
    return {
        'baseUrl': DEFAULT_BASE,
        'agentId': DEFAULT_AGENT_ID,
        'displayName': DEFAULT_DISPLAY_NAME,
        'ownerId': DEFAULT_OWNER_ID,
        'maxTurns': 3,
        'maxContext': 1200,
        'activeRoomId': None,
        'lastEventCount': 0,
    }


def read_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return default_state()


def write_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2))


def req(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers['Content-Type'] = 'application/json'
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        raise SystemExit(f'HTTP {e.code}: {body}')


def require_room(state, room_id=None):
    rid = room_id or state.get('activeRoomId')
    if not rid:
        raise SystemExit('No room provided')
    return rid


def base_join_payload(state):
    return {
        'id': state['agentId'],
        'displayName': state['displayName'],
        'kind': 'agent',
        'ownerId': state['ownerId'],
        'avatar': {'style': 'cute-bot', 'color': 'mint', 'mood': 'curious'},
        'behavior': {
            'maxTurns': state['maxTurns'],
            'eagerness': 0.4,
            'respondOnMention': True,
            'respondOnKeywords': ['@' + str(state.get('agentId') or DEFAULT_AGENT_ID)],
            'allowOwnerContinue': True,
            'cooldownMs': 15000,
        },
        'status': 'listening',
    }


def update_agent_config(state, payload, room_id=None):
    rid = require_room(state, room_id)
    return req('POST', f"{state['baseUrl']}/rooms/{rid}/agents/{state['agentId']}", payload)


def cmd_state(args):
    state = read_state()
    if args.action == 'show':
        print(json.dumps(state, indent=2))
        return
    if args.action == 'set-room':
        state['activeRoomId'] = args.room_id
        write_state(state)
        print(json.dumps(state, indent=2))
        return
    if args.action == 'set-max-context':
        state['maxContext'] = args.tokens
        write_state(state)
        print(json.dumps(state, indent=2))
        return
    if args.action == 'set-last-event-count':
        state['lastEventCount'] = args.count
        write_state(state)
        print(json.dumps(state, indent=2))
        return


def cmd_join(args):
    state = read_state()
    room_id = args.room_id
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/join", base_join_payload(state))
    state['activeRoomId'] = room_id
    write_state(state)
    print(json.dumps(out, indent=2))


def cmd_max(args):
    state = read_state()
    state['maxTurns'] = args.max_turns
    write_state(state)
    room_id = state.get('activeRoomId')
    if room_id:
        out = update_agent_config(state, {'maxTurns': args.max_turns}, room_id=room_id)
        print(json.dumps(out, indent=2))
    else:
        print(json.dumps(state, indent=2))


def cmd_set_status(args):
    state = read_state()
    rid = require_room(state, args.room_id)
    out = update_agent_config(state, {'status': args.status}, room_id=rid)
    print(json.dumps(out, indent=2))


def cmd_stop(args):
    state = read_state()
    room_id = require_room(state)
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/agents/{state['agentId']}/pause", {})
    print(json.dumps(out, indent=2))


def cmd_continue(args):
    state = read_state()
    room_id = require_room(state)
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/agents/{state['agentId']}/continue", {'turns': args.turns})
    print(json.dumps(out, indent=2))


def cmd_events(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    out = req('GET', f"{state['baseUrl']}/rooms/{room_id}/events")
    print(json.dumps(out, indent=2))


def cmd_send(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    payload = {'senderId': args.sender_id, 'text': args.text, 'kind': args.kind}
    if args.a2a_to:
        payload['a2a'] = {
            'protocol': 'cw.a2a.v1',
            'from': {'agentId': args.sender_id},
            'to': {'agentId': args.a2a_to},
            'type': 'chat',
            'text': args.text,
            'meta': {'channelMessage': args.kind == 'channel'}
        }
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/messages", payload)
    print(json.dumps(out, indent=2))


def cmd_mirror_in(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    payload = {'senderId': args.sender_id, 'text': args.text, 'kind': 'channel'}
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/messages", payload)
    print(json.dumps(out, indent=2))


def cmd_mirror_out(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    payload = {
        'senderId': args.sender_id,
        'text': args.text,
        'kind': 'agent',
        'a2a': {
            'protocol': 'cw.a2a.v1',
            'from': {'agentId': args.sender_id},
            'to': {'agentId': args.to_id},
            'type': 'chat',
            'text': args.text,
            'meta': {'channelMessage': True, 'surface': 'telegram'}
        }
    }
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/messages", payload)
    print(json.dumps(out, indent=2))


def emit(action, result):
    print(json.dumps({'ok': True, 'action': action, 'result': result}, indent=2))


def cmd_handle_text(args):
    text = args.text.strip()
    if not text:
        emit('noop', {})
        return

    state = read_state()
    lowered = text.lower()

    dash_continue = CW_CONTINUE_DASH_RE.match(text)
    if dash_continue:
        turns = int(dash_continue.group(1))
        out = req('POST', f"{state['baseUrl']}/rooms/{require_room(state)}/agents/{state['agentId']}/continue", {'turns': turns})
        emit('cw-continue', out)
        return

    dash_max = CW_MAX_DASH_RE.match(text)
    if dash_max:
        value = int(dash_max.group(1))
        state['maxTurns'] = value
        write_state(state)
        room_id = state.get('activeRoomId')
        if room_id:
            out = update_agent_config(state, {'maxTurns': value}, room_id=room_id)
            emit('cw-max', out)
        else:
            emit('cw-max', state)
        return

    if lowered.startswith('cw-join '):
        room_id = text.split(None, 1)[1].strip()
        out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/join", base_join_payload(state))
        state['activeRoomId'] = room_id
        write_state(state)
        emit('cw-join', out)
        return

    if lowered.startswith('cw-max-context ') or lowered.startswith('cw-max-contect '):
        value = int(text.split(None, 1)[1].strip())
        state['maxContext'] = value
        write_state(state)
        emit('cw-max-context', state)
        return

    if lowered.startswith('cw-max '):
        value = int(text.split(None, 1)[1].strip())
        state['maxTurns'] = value
        write_state(state)
        room_id = state.get('activeRoomId')
        if room_id:
            out = update_agent_config(state, {'maxTurns': value}, room_id=room_id)
            emit('cw-max', out)
        else:
            emit('cw-max', state)
        return

    if lowered == 'cw-stop':
        out = req('POST', f"{state['baseUrl']}/rooms/{require_room(state)}/agents/{state['agentId']}/pause", {})
        emit('cw-stop', out)
        return

    if lowered.startswith('cw-continue '):
        turns = int(text.split(None, 1)[1].strip())
        out = req('POST', f"{state['baseUrl']}/rooms/{require_room(state)}/agents/{state['agentId']}/continue", {'turns': turns})
        emit('cw-continue', out)
        return

    if lowered.startswith('cw-status '):
        status = text.split(None, 1)[1].strip()
        out = update_agent_config(state, {'status': status}, room_id=require_room(state, args.room_id))
        emit('cw-status', out)
        return

    room_id = require_room(state, args.room_id)
    payload = {'senderId': args.sender_id, 'text': text, 'kind': 'channel'}
    out = req('POST', f"{state['baseUrl']}/rooms/{room_id}/messages", payload)
    emit('mirror-in', out)


def cmd_watch_arm(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    out = req('GET', f"{state['baseUrl']}/rooms/{room_id}/events")
    count = len(out.get('events', []))
    state['activeRoomId'] = room_id
    state['lastEventCount'] = count
    write_state(state)
    print(json.dumps({'ok': True, 'action': 'watch-arm', 'roomId': room_id, 'lastEventCount': count}, indent=2))


def cmd_watch_poll(args):
    state = read_state()
    room_id = require_room(state, args.room_id)
    out = req('GET', f"{state['baseUrl']}/rooms/{room_id}/events")
    events = out.get('events', [])
    last_count = int(state.get('lastEventCount', 0) or 0)
    new_events = events[last_count:] if last_count <= len(events) else events
    humanish = []
    for ev in new_events:
        if ev.get('type') != 'message_posted':
            continue
        payload = ev.get('payload') or {}
        if payload.get('kind') == 'channel':
            humanish.append(payload)
    state['activeRoomId'] = room_id
    state['lastEventCount'] = len(events)
    write_state(state)
    print(json.dumps({
        'ok': True,
        'action': 'watch-poll',
        'roomId': room_id,
        'lastEventCount': state['lastEventCount'],
        'newEventCount': len(new_events),
        'newEvents': new_events,
        'newChannelMessages': humanish,
    }, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    sp = sub.add_parser('state')
    sp_sub = sp.add_subparsers(dest='action', required=True)
    sp_show = sp_sub.add_parser('show')
    sp_show.set_defaults(func=cmd_state)
    sp_room = sp_sub.add_parser('set-room')
    sp_room.add_argument('room_id')
    sp_room.set_defaults(func=cmd_state)
    sp_ctx = sp_sub.add_parser('set-max-context')
    sp_ctx.add_argument('tokens', type=int)
    sp_ctx.set_defaults(func=cmd_state)
    sp_lec = sp_sub.add_parser('set-last-event-count')
    sp_lec.add_argument('count', type=int)
    sp_lec.set_defaults(func=cmd_state)

    j = sub.add_parser('join')
    j.add_argument('room_id')
    j.set_defaults(func=cmd_join)

    m = sub.add_parser('max')
    m.add_argument('max_turns', type=int)
    m.set_defaults(func=cmd_max)

    ss = sub.add_parser('set-status')
    ss.add_argument('status')
    ss.add_argument('--room-id')
    ss.set_defaults(func=cmd_set_status)

    st = sub.add_parser('stop')
    st.set_defaults(func=cmd_stop)

    c = sub.add_parser('continue')
    c.add_argument('turns', type=int)
    c.set_defaults(func=cmd_continue)

    e = sub.add_parser('events')
    e.add_argument('--room-id')
    e.set_defaults(func=cmd_events)

    s = sub.add_parser('send')
    s.add_argument('text')
    s.add_argument('--room-id')
    s.add_argument('--sender-id', default=DEFAULT_AGENT_ID)
    s.add_argument('--kind', default='agent')
    s.add_argument('--a2a-to')
    s.set_defaults(func=cmd_send)

    mi = sub.add_parser('mirror-in')
    mi.add_argument('text')
    mi.add_argument('--room-id')
    mi.add_argument('--sender-id', default=DEFAULT_OWNER_ID)
    mi.set_defaults(func=cmd_mirror_in)

    mo = sub.add_parser('mirror-out')
    mo.add_argument('text')
    mo.add_argument('--room-id')
    mo.add_argument('--sender-id', default=DEFAULT_AGENT_ID)
    mo.add_argument('--to-id', default=DEFAULT_OWNER_ID)
    mo.set_defaults(func=cmd_mirror_out)

    ht = sub.add_parser('handle-text')
    ht.add_argument('text')
    ht.add_argument('--room-id')
    ht.add_argument('--sender-id', default=DEFAULT_OWNER_ID)
    ht.set_defaults(func=cmd_handle_text)

    wa = sub.add_parser('watch-arm')
    wa.add_argument('--room-id')
    wa.set_defaults(func=cmd_watch_arm)

    wp = sub.add_parser('watch-poll')
    wp.add_argument('--room-id')
    wp.set_defaults(func=cmd_watch_poll)

    args = p.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
