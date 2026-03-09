#!/usr/bin/env python3
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from secrets import token_hex
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE_PATH = ROOT / 'state.json'
RUNTIME_DIR = ROOT / 'runtime'
MONITOR_STATE_PATH = RUNTIME_DIR / 'monitor.json'
PID_PATH = RUNTIME_DIR / 'monitor.pid'
LOG_PATH = RUNTIME_DIR / 'monitor.log'
DEFAULT_BASE = os.environ.get('CW_BASE_URL', 'http://127.0.0.1:18080')
DEFAULT_AGENT_ID = os.environ.get('CW_AGENT_ID', 'agent')
DEFAULT_DISPLAY_NAME = os.environ.get('CW_DISPLAY_NAME', 'Agent')
DEFAULT_OWNER_ID = os.environ.get('CW_OWNER_ID', 'owner')
DEFAULT_INTERVAL = 3.0
DEFAULT_HEARTBEAT = 30.0
QUEUE_LIMIT = 200
RUNNING = True


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def approx_tokens(text):
    text = str(text or '')
    return max(1, (len(text) + 3) // 4)


def read_json(method, url, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode()
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


def read_agent_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {
        'baseUrl': DEFAULT_BASE,
        'agentId': DEFAULT_AGENT_ID,
        'displayName': DEFAULT_DISPLAY_NAME,
        'ownerId': DEFAULT_OWNER_ID,
        'maxContext': 1200,
        'activeRoomId': None,
    }


def default_monitor_state():
    agent = read_agent_state()
    return {
        'running': False,
        'pid': None,
        'roomId': agent.get('activeRoomId'),
        'baseUrl': agent.get('baseUrl', DEFAULT_BASE),
        'agentId': agent.get('agentId', DEFAULT_AGENT_ID),
        'intervalSec': DEFAULT_INTERVAL,
        'heartbeatSec': DEFAULT_HEARTBEAT,
        'mentionsOnly': False,
        'lastEventCount': 0,
        'queue': [],
        'queueApproxTokens': 0,
        'startedAt': None,
        'stoppedAt': None,
        'lastPollAt': None,
        'lastHeartbeatAt': None,
        'heartbeatCount': 0,
        'lastHeartbeatPostedAt': None,
        'heartbeatPostedCount': 0,
        'lastMessageAt': None,
        'lastMessageText': None,
        'preparedBatch': None,
        'agentStatus': 'paused',
    }


def read_monitor_state():
    if MONITOR_STATE_PATH.exists():
        return json.loads(MONITOR_STATE_PATH.read_text())
    return default_monitor_state()


def write_monitor_state(state):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    state['queueApproxTokens'] = sum(approx_tokens(m.get('text')) for m in state.get('queue', []))
    MONITOR_STATE_PATH.write_text(json.dumps(state, indent=2))


def append_log(entry):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open('a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def current_pid():
    if not PID_PATH.exists():
        return None
    try:
        return int(PID_PATH.read_text().strip())
    except Exception:
        return None


def fetch_events(base_url, room_id):
    out = read_json('GET', f'{base_url}/rooms/{room_id}/events')
    return out.get('events', [])


def set_agent_status(base_url, room_id, agent_id, status):
    if not room_id or not agent_id:
        return None
    return read_json('POST', f'{base_url}/rooms/{room_id}/agents/{agent_id}', {'status': status})


def continue_agent(base_url, room_id, agent_id, turns):
    if not room_id or not agent_id:
        return None
    return read_json('POST', f'{base_url}/rooms/{room_id}/agents/{agent_id}/continue', {'turns': turns})


def pause_agent(base_url, room_id, agent_id):
    if not room_id or not agent_id:
        return None
    return read_json('POST', f'{base_url}/rooms/{room_id}/agents/{agent_id}/pause', {})


def send_agent_message(base_url, room_id, sender_id, to_id, text):
    if not room_id or not sender_id:
        return None
    payload = {
        'senderId': sender_id,
        'text': text,
        'kind': 'agent',
        'a2a': {
            'protocol': 'cw.a2a.v1',
            'from': {'agentId': sender_id},
            'to': {'agentId': to_id or DEFAULT_OWNER_ID},
            'type': 'chat',
            'text': text,
            'meta': {'channelMessage': True, 'surface': 'telegram'}
        }
    }
    return read_json('POST', f'{base_url}/rooms/{room_id}/messages', payload)


def filter_channel_messages(events, mentions_only=False, agent_id=DEFAULT_AGENT_ID):
    out = []
    needle = '@' + str(agent_id or DEFAULT_AGENT_ID).lower()
    for ev in events:
        if ev.get('type') != 'message_posted':
            continue
        payload = ev.get('payload') or {}
        if payload.get('kind') != 'channel':
            continue
        text = str(payload.get('text') or '')
        if mentions_only and needle not in text.lower():
            continue
        out.append(payload)
    return out


def enqueue_messages(state, msgs):
    queue = state.get('queue', [])
    known = {m.get('id') for m in queue}
    for msg in msgs:
        if msg.get('id') in known:
            continue
        queue.append({
            'id': msg.get('id'),
            'senderId': msg.get('senderId'),
            'sender': msg.get('sender'),
            'kind': msg.get('kind'),
            'text': msg.get('text'),
            'createdAt': msg.get('createdAt'),
            'approxTokens': approx_tokens(msg.get('text')),
        })
    if len(queue) > QUEUE_LIMIT:
        queue = queue[-QUEUE_LIMIT:]
    state['queue'] = queue
    state['queueApproxTokens'] = sum(m.get('approxTokens', approx_tokens(m.get('text'))) for m in queue)
    return state


def trim_queue_for_context(queue, max_context):
    total = 0
    selected = []
    for msg in reversed(queue):
        cost = int(msg.get('approxTokens') or approx_tokens(msg.get('text')))
        if selected and total + cost > max_context:
            continue
        if not selected and cost > max_context:
            selected.append(msg)
            total = cost
            break
        selected.append(msg)
        total += cost
        if total >= max_context:
            break
    selected.reverse()
    dropped = max(0, len(queue) - len(selected))
    return selected, total, dropped


def make_prepared_batch(room_id, max_context, queue, selected, approx_total, dropped, source):
    return {
        'id': f'prepared-{token_hex(6)}',
        'createdAt': now_iso(),
        'roomId': room_id,
        'source': source,
        'maxContext': max_context,
        'queueLengthBefore': len(queue),
        'selectedCount': len(selected),
        'droppedHeadCount': dropped,
        'approxTokens': approx_total,
        'messages': selected,
        'promptText': '\n'.join(f"{m.get('sender')}: {m.get('text')}" for m in selected),
    }


def heartbeat_due(state):
    hb_sec = float(state.get('heartbeatSec', DEFAULT_HEARTBEAT) or 0)
    if hb_sec <= 0:
        return False
    last = state.get('lastHeartbeatPostedAt')
    if not last:
        return True
    try:
        prev = datetime.fromisoformat(last.replace('Z', '+00:00'))
        return (datetime.now(timezone.utc) - prev).total_seconds() >= hb_sec
    except Exception:
        return True


def heartbeat_summary(state):
    return (
        f"[cw heartbeat] {state.get('agentId', 'agent')} {state.get('agentStatus', 'listening')}"
        f" • room {state.get('roomId') or '-'}"
        f" • queue {len(state.get('queue', []))} msgs"
        f" • ~{state.get('queueApproxTokens', 0)} tok"
    )


def cmd_next(args):
    state = read_monitor_state()
    agent = read_agent_state()
    room_id = state.get('roomId') or agent.get('activeRoomId')
    max_context = args.max_context or int(agent.get('maxContext', 1200) or 1200)
    queue = state.get('queue', [])
    status = state.get('agentStatus', 'listening')

    if status == 'paused':
        if heartbeat_due(state):
            text = heartbeat_summary(state)
            state['lastHeartbeatPostedAt'] = now_iso()
            state['heartbeatPostedCount'] = int(state.get('heartbeatPostedCount', 0) or 0) + 1
            write_monitor_state(state)
            print(json.dumps({
                'ok': True,
                'action': 'heartbeat',
                'roomId': room_id,
                'modelContextExcluded': True,
                'telegramText': text,
                'queueLength': len(queue),
                'queueApproxTokens': state.get('queueApproxTokens', 0),
                'agentStatus': status,
            }, indent=2))
            return
        print(json.dumps({
            'ok': True,
            'action': 'queued-paused' if queue else 'noop',
            'roomId': room_id,
            'modelContextExcluded': True,
            'queueLength': len(queue),
            'queueApproxTokens': state.get('queueApproxTokens', 0),
            'agentStatus': status,
        }, indent=2))
        return

    if queue:
        selected, approx_total, dropped = trim_queue_for_context(queue, max_context)
        state['queue'] = []
        state['queueApproxTokens'] = 0
        state['agentStatus'] = 'thinking'
        prepared = make_prepared_batch(room_id, max_context, queue, selected, approx_total, dropped, 'next')
        state['preparedBatch'] = prepared
        write_monitor_state(state)
        try:
            set_agent_status(state.get('baseUrl', DEFAULT_BASE), room_id, state.get('agentId', DEFAULT_AGENT_ID), 'thinking')
        except Exception as e:
            append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'thinking'})
        prompt_lines = [f"{m.get('sender')}: {m.get('text')}" for m in selected]
        print(json.dumps({
            'ok': True,
            'action': 'batch',
            'roomId': room_id,
            'maxContext': max_context,
            'queueLengthBefore': len(queue),
            'selectedCount': len(selected),
            'droppedHeadCount': dropped,
            'approxTokens': approx_total,
            'messages': selected,
            'promptText': '\n'.join(prompt_lines),
            'preparedBatch': prepared,
        }, indent=2))
        return

    if heartbeat_due(state):
        text = heartbeat_summary(state)
        state['lastHeartbeatPostedAt'] = now_iso()
        state['heartbeatPostedCount'] = int(state.get('heartbeatPostedCount', 0) or 0) + 1
        write_monitor_state(state)
        print(json.dumps({
            'ok': True,
            'action': 'heartbeat',
            'roomId': room_id,
            'modelContextExcluded': True,
            'telegramText': text,
            'queueLength': 0,
            'queueApproxTokens': 0,
            'agentStatus': status,
        }, indent=2))
        return

    print(json.dumps({
        'ok': True,
        'action': 'noop',
        'roomId': room_id,
        'modelContextExcluded': True,
        'queueLength': 0,
        'queueApproxTokens': 0,
        'agentStatus': status,
    }, indent=2))


def cmd_start(args):
    pid = current_pid()
    if pid and pid_alive(pid):
        state = read_monitor_state()
        state['running'] = True
        state['pid'] = pid
        write_monitor_state(state)
        print(json.dumps({'ok': True, 'action': 'monitor-start', 'running': True, 'pid': pid, 'roomId': state.get('roomId'), 'alreadyRunning': True}, indent=2))
        return
    if pid and not pid_alive(pid):
        try:
            PID_PATH.unlink()
        except FileNotFoundError:
            pass

    agent = read_agent_state()
    room_id = args.room_id or agent.get('activeRoomId')
    if not room_id:
        raise SystemExit('No active room')
    base_url = agent.get('baseUrl', DEFAULT_BASE)
    agent_id = agent.get('agentId', DEFAULT_AGENT_ID)
    events = fetch_events(base_url, room_id)

    state = read_monitor_state()
    state.update({
        'running': False,
        'pid': None,
        'roomId': room_id,
        'baseUrl': base_url,
        'agentId': agent_id,
        'intervalSec': args.interval,
        'heartbeatSec': args.heartbeat_sec,
        'mentionsOnly': args.mentions_only,
        'lastEventCount': len(events) if args.from_now else int(state.get('lastEventCount', 0) or 0),
        'startedAt': now_iso(),
        'stoppedAt': None,
        'lastPollAt': None,
        'lastHeartbeatAt': None,
        'agentStatus': 'listening',
    })
    write_monitor_state(state)
    try:
        set_agent_status(base_url, room_id, agent_id, 'listening')
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'listening'})

    stderr = LOG_PATH.open('a', encoding='utf-8')
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__)), 'run', '--room-id', room_id, '--interval', str(args.interval), '--heartbeat-sec', str(args.heartbeat_sec)] + (['--mentions-only'] if args.mentions_only else []),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=stderr,
        start_new_session=True,
        close_fds=True,
    )
    PID_PATH.write_text(str(proc.pid))
    time.sleep(0.2)
    state['running'] = pid_alive(proc.pid)
    state['pid'] = proc.pid
    write_monitor_state(state)
    print(json.dumps({'ok': True, 'action': 'monitor-start', 'running': state['running'], 'pid': proc.pid, 'roomId': room_id, 'mentionsOnly': args.mentions_only, 'intervalSec': args.interval, 'heartbeatSec': args.heartbeat_sec}, indent=2))


def cmd_stop(args):
    pid = current_pid()
    state = read_monitor_state()
    if not pid:
        state['running'] = False
        state['pid'] = None
        state['stoppedAt'] = now_iso()
        state['agentStatus'] = 'paused'
        write_monitor_state(state)
        try:
            set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'paused')
        except Exception:
            pass
        print(json.dumps({'ok': True, 'action': 'monitor-stop', 'running': False, 'stopped': False, 'reason': 'not running'}, indent=2))
        return
    stopped = False
    if pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(20):
                if not pid_alive(pid):
                    stopped = True
                    break
                time.sleep(0.1)
        except OSError:
            stopped = True
    else:
        stopped = True
    try:
        PID_PATH.unlink()
    except FileNotFoundError:
        pass
    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    state['agentStatus'] = 'paused'
    write_monitor_state(state)
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'paused')
    except Exception:
        pass
    print(json.dumps({'ok': True, 'action': 'monitor-stop', 'running': False, 'stopped': stopped}, indent=2))


def cmd_status(args):
    pid = current_pid()
    state = read_monitor_state()
    running = bool(pid and pid_alive(pid))
    state['running'] = running
    state['pid'] = pid if running else None
    state['queueLength'] = len(state.get('queue', []))
    state['queueApproxTokens'] = sum(approx_tokens(m.get('text')) for m in state.get('queue', []))
    write_monitor_state({k: v for k, v in state.items() if k not in ('queueLength',)})
    print(json.dumps({'ok': True, 'action': 'monitor-status', **state}, indent=2))


def cmd_drain(args):
    state = read_monitor_state()
    queue = state.get('queue', [])
    agent = read_agent_state()
    max_context = args.max_context or int(agent.get('maxContext', 1200) or 1200)
    selected, approx_total, dropped = trim_queue_for_context(queue, max_context)
    state['queue'] = []
    state['queueApproxTokens'] = 0
    state['agentStatus'] = 'thinking'
    prepared = make_prepared_batch(state.get('roomId'), max_context, queue, selected, approx_total, dropped, 'drain')
    state['preparedBatch'] = prepared
    write_monitor_state(state)
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'thinking')
    except Exception:
        pass
    prompt_lines = [f"{m.get('sender')}: {m.get('text')}" for m in selected]
    print(json.dumps({
        'ok': True,
        'action': 'monitor-drain',
        'roomId': state.get('roomId'),
        'maxContext': max_context,
        'queueLengthBefore': len(queue),
        'selectedCount': len(selected),
        'droppedHeadCount': dropped,
        'approxTokens': approx_total,
        'messages': selected,
        'promptText': '\n'.join(prompt_lines),
        'preparedBatch': prepared,
    }, indent=2))


def cmd_pause(args):
    state = read_monitor_state()
    state['agentStatus'] = 'paused'
    write_monitor_state(state)
    participant = None
    try:
        participant = pause_agent(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID))
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'pause_error', 'error': str(e)})
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'paused')
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'paused'})
    append_log({'ts': now_iso(), 'type': 'monitor_paused', 'roomId': state.get('roomId'), 'queueLength': len(state.get('queue', [])), 'queueApproxTokens': state.get('queueApproxTokens', 0)})
    print(json.dumps({'ok': True, 'action': 'monitor-pause', 'roomId': state.get('roomId'), 'queueLength': len(state.get('queue', [])), 'queueApproxTokens': state.get('queueApproxTokens', 0), 'participant': participant}, indent=2))


def cmd_resume(args):
    state = read_monitor_state()
    queue = state.get('queue', [])
    agent = read_agent_state()
    max_context = args.max_context or int(agent.get('maxContext', 1200) or 1200)
    turns = args.turns if args.turns is not None else 1
    participant = None
    try:
        participant = continue_agent(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), turns)
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'resume_error', 'error': str(e), 'turns': turns})
    selected, approx_total, dropped = trim_queue_for_context(queue, max_context)
    state['queue'] = []
    state['queueApproxTokens'] = 0
    state['agentStatus'] = 'thinking'
    prepared = make_prepared_batch(state.get('roomId'), max_context, queue, selected, approx_total, dropped, 'resume')
    state['preparedBatch'] = prepared
    write_monitor_state(state)
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'thinking')
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'thinking'})
    append_log({'ts': now_iso(), 'type': 'monitor_resumed', 'roomId': state.get('roomId'), 'turns': turns, 'selectedCount': len(selected), 'droppedHeadCount': dropped, 'approxTokens': approx_total})
    prompt_lines = [f"{m.get('sender')}: {m.get('text')}" for m in selected]
    print(json.dumps({
        'ok': True,
        'action': 'monitor-resume',
        'roomId': state.get('roomId'),
        'turns': turns,
        'maxContext': max_context,
        'queueLengthBefore': len(queue),
        'selectedCount': len(selected),
        'droppedHeadCount': dropped,
        'approxTokens': approx_total,
        'participant': participant,
        'messages': selected,
        'promptText': '\n'.join(prompt_lines),
        'preparedBatch': prepared,
    }, indent=2))


def cmd_reply_finish(args):
    state = read_monitor_state()
    agent = read_agent_state()
    room_id = args.room_id or state.get('roomId') or agent.get('activeRoomId')
    agent_id = args.sender_id or state.get('agentId') or agent.get('agentId', DEFAULT_AGENT_ID)
    to_id = args.to_id or agent.get('ownerId', DEFAULT_OWNER_ID)
    text = args.text.strip()
    if not room_id:
        raise SystemExit('No room provided')
    if not text:
        raise SystemExit('Reply text required')

    state['agentStatus'] = 'writing'
    write_monitor_state(state)
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), room_id, agent_id, 'writing')
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'writing'})

    msg = send_agent_message(state.get('baseUrl', DEFAULT_BASE), room_id, agent_id, to_id, text)

    next_status = args.next_status
    state['agentStatus'] = next_status
    state['preparedBatch'] = None
    state['lastReplyAt'] = msg.get('createdAt') if isinstance(msg, dict) else now_iso()
    state['lastReplyText'] = text
    write_monitor_state(state)
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), room_id, agent_id, next_status)
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': next_status})

    append_log({'ts': now_iso(), 'type': 'reply_finished', 'roomId': room_id, 'messageId': msg.get('id') if isinstance(msg, dict) else None, 'nextStatus': next_status})
    print(json.dumps({
        'ok': True,
        'action': 'reply-finish',
        'roomId': room_id,
        'message': msg,
        'nextStatus': next_status,
    }, indent=2))


def _handle_signal(signum, frame):
    global RUNNING
    RUNNING = False


def cmd_run(args):
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    state = read_monitor_state()
    pid = os.getpid()
    PID_PATH.write_text(str(pid))
    state.update({
        'running': True,
        'pid': pid,
        'roomId': args.room_id or state.get('roomId') or read_agent_state().get('activeRoomId'),
        'baseUrl': read_agent_state().get('baseUrl', state.get('baseUrl', DEFAULT_BASE)),
        'agentId': read_agent_state().get('agentId', state.get('agentId', DEFAULT_AGENT_ID)),
        'intervalSec': args.interval,
        'heartbeatSec': args.heartbeat_sec,
        'mentionsOnly': args.mentions_only,
        'agentStatus': 'listening',
    })
    write_monitor_state(state)
    append_log({'ts': now_iso(), 'type': 'monitor_started', 'pid': pid, 'roomId': state['roomId'], 'mentionsOnly': args.mentions_only, 'intervalSec': args.interval, 'heartbeatSec': args.heartbeat_sec})
    try:
        set_agent_status(state['baseUrl'], state['roomId'], state['agentId'], 'listening')
    except Exception as e:
        append_log({'ts': now_iso(), 'type': 'status_error', 'error': str(e), 'status': 'listening'})

    while RUNNING:
        try:
            fresh = read_monitor_state()
            state['agentStatus'] = fresh.get('agentStatus', state.get('agentStatus'))
            state['queue'] = fresh.get('queue', state.get('queue', []))
            state['queueApproxTokens'] = fresh.get('queueApproxTokens', state.get('queueApproxTokens', 0))
            state['heartbeatSec'] = fresh.get('heartbeatSec', state.get('heartbeatSec', DEFAULT_HEARTBEAT))
            state['mentionsOnly'] = fresh.get('mentionsOnly', state.get('mentionsOnly', args.mentions_only))
            events = fetch_events(state['baseUrl'], state['roomId'])
            last_count = int(state.get('lastEventCount', 0) or 0)
            if last_count < 0 or last_count > len(events):
                last_count = len(events)
            new_events = events[last_count:]
            msgs = filter_channel_messages(new_events, mentions_only=state.get('mentionsOnly', args.mentions_only), agent_id=state.get('agentId', DEFAULT_AGENT_ID))
            if msgs:
                enqueue_messages(state, msgs)
                for msg in msgs:
                    append_log({'ts': now_iso(), 'type': 'new_channel_message', 'roomId': state['roomId'], 'message': msg})
                state['lastMessageAt'] = msgs[-1].get('createdAt')
                state['lastMessageText'] = msgs[-1].get('text')
            state['lastEventCount'] = len(events)
            state['lastPollAt'] = now_iso()
            if state.get('heartbeatSec', DEFAULT_HEARTBEAT) > 0:
                last_hb = state.get('lastHeartbeatAt')
                due = True
                if last_hb:
                    try:
                        prev = datetime.fromisoformat(last_hb.replace('Z', '+00:00'))
                        due = (datetime.now(timezone.utc) - prev).total_seconds() >= float(state.get('heartbeatSec', DEFAULT_HEARTBEAT))
                    except Exception:
                        due = True
                if due:
                    state['lastHeartbeatAt'] = now_iso()
                    state['heartbeatCount'] = int(state.get('heartbeatCount', 0) or 0) + 1
                    append_log({
                        'ts': state['lastHeartbeatAt'],
                        'type': 'heartbeat',
                        'roomId': state['roomId'],
                        'queueLength': len(state.get('queue', [])),
                        'queueApproxTokens': state.get('queueApproxTokens', 0),
                        'agentStatus': state.get('agentStatus', 'listening'),
                        'note': 'heartbeat is out-of-band monitor state; not passed into model context',
                    })
            state['running'] = True
            state['pid'] = pid
            write_monitor_state(state)
        except Exception as e:
            append_log({'ts': now_iso(), 'type': 'monitor_error', 'error': str(e)})
        time.sleep(args.interval)

    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    state['agentStatus'] = 'paused'
    write_monitor_state(state)
    try:
        if current_pid() == pid:
            PID_PATH.unlink()
    except FileNotFoundError:
        pass
    try:
        set_agent_status(state.get('baseUrl', DEFAULT_BASE), state.get('roomId'), state.get('agentId', DEFAULT_AGENT_ID), 'paused')
    except Exception:
        pass
    append_log({'ts': now_iso(), 'type': 'monitor_stopped', 'pid': pid, 'roomId': state.get('roomId')})


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    s = sub.add_parser('start')
    s.add_argument('--room-id')
    s.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    s.add_argument('--heartbeat-sec', type=float, default=DEFAULT_HEARTBEAT)
    s.add_argument('--mentions-only', action='store_true')
    s.add_argument('--from-now', action='store_true')
    s.set_defaults(func=cmd_start)

    st = sub.add_parser('stop')
    st.set_defaults(func=cmd_stop)

    ss = sub.add_parser('status')
    ss.set_defaults(func=cmd_status)

    ps = sub.add_parser('pause')
    ps.set_defaults(func=cmd_pause)

    rs = sub.add_parser('resume')
    rs.add_argument('--turns', type=int)
    rs.add_argument('--max-context', type=int)
    rs.set_defaults(func=cmd_resume)

    rf = sub.add_parser('reply-finish')
    rf.add_argument('text')
    rf.add_argument('--room-id')
    rf.add_argument('--sender-id')
    rf.add_argument('--to-id')
    rf.add_argument('--next-status', default='listening')
    rf.set_defaults(func=cmd_reply_finish)

    nx = sub.add_parser('next')
    nx.add_argument('--max-context', type=int)
    nx.set_defaults(func=cmd_next)

    dr = sub.add_parser('drain')
    dr.add_argument('--max-context', type=int)
    dr.set_defaults(func=cmd_drain)

    r = sub.add_parser('run')
    r.add_argument('--room-id')
    r.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    r.add_argument('--heartbeat-sec', type=float, default=DEFAULT_HEARTBEAT)
    r.add_argument('--mentions-only', action='store_true')
    r.set_defaults(func=cmd_run)

    args = p.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
