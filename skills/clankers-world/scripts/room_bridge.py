#!/usr/bin/env python3
import argparse
import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from secrets import token_hex

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = ROOT / 'runtime'
BRIDGE_STATE_PATH = RUNTIME_DIR / 'bridge.json'
BRIDGE_PID_PATH = RUNTIME_DIR / 'bridge.pid'
BRIDGE_LOG_PATH = RUNTIME_DIR / 'bridge.log'
BRIDGE_OUTBOX_PATH = RUNTIME_DIR / 'bridge_outbox.jsonl'
ROOM_MONITOR = ROOT / 'scripts' / 'room_monitor.py'
ROOM_CLIENT = ROOT / 'scripts' / 'room_client.py'
DEFAULT_INTERVAL = 3.0
RUNNING = True


def now_iso():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def read_json_file(path, default):
    if path.exists():
        return json.loads(path.read_text())
    return default


def append_jsonl(path, item):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')


def load_outbox():
    if not BRIDGE_OUTBOX_PATH.exists():
        return []
    items = []
    with BRIDGE_OUTBOX_PATH.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def default_bridge_state():
    return {
        'running': False,
        'pid': None,
        'intervalSec': DEFAULT_INTERVAL,
        'startedAt': None,
        'stoppedAt': None,
        'lastTickAt': None,
        'lastDecision': None,
        'lastDecisionAt': None,
        'lastOutboxItemId': None,
        'pendingBatch': None,
        'ackedItemIds': [],
        'lastReplyAt': None,
    }


def read_bridge_state():
    return read_json_file(BRIDGE_STATE_PATH, default_bridge_state())


def write_bridge_state(state):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    BRIDGE_STATE_PATH.write_text(json.dumps(state, indent=2))


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def current_pid():
    if not BRIDGE_PID_PATH.exists():
        return None
    try:
        return int(BRIDGE_PID_PATH.read_text().strip())
    except Exception:
        return None


def append_log(entry):
    append_jsonl(BRIDGE_LOG_PATH, entry)


def run_json(args):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f'command failed: {args}')
    out = proc.stdout.strip()
    if not out:
        return {}
    return json.loads(out)


def pending_items(state, item_types=None):
    acked = set(state.get('ackedItemIds', []))
    items = [it for it in load_outbox() if it.get('id') not in acked]
    if item_types:
        allowed = set(item_types)
        items = [it for it in items if it.get('type') in allowed]
    return items


def ack_item(state, item_id):
    acked = list(state.get('ackedItemIds', []))
    if item_id not in acked:
        acked.append(item_id)
    state['ackedItemIds'] = acked
    return state


def make_item(item_type, payload):
    return {
        'id': f'{item_type}-{token_hex(6)}',
        'type': item_type,
        'createdAt': now_iso(),
        **payload,
    }


def emit_outbox(item, state):
    append_jsonl(BRIDGE_OUTBOX_PATH, item)
    state['lastOutboxItemId'] = item['id']
    return item


def tick_once(max_context=None):
    state = read_bridge_state()
    state['lastTickAt'] = now_iso()
    pending = state.get('pendingBatch')
    monitor_state = read_json_file(ROOT / 'runtime' / 'monitor.json', {})
    prepared = monitor_state.get('preparedBatch')
    if pending:
        state['lastDecision'] = 'awaiting-reply'
        state['lastDecisionAt'] = now_iso()
        write_bridge_state(state)
        return {
            'ok': True,
            'action': 'awaiting-reply',
            'pendingBatch': pending,
        }
    if prepared:
        ticket = make_item('model_batch', {
            'roomId': prepared.get('roomId'),
            'promptText': prepared.get('promptText', ''),
            'messages': prepared.get('messages', []),
            'maxContext': prepared.get('maxContext'),
            'selectedCount': prepared.get('selectedCount'),
            'droppedHeadCount': prepared.get('droppedHeadCount'),
            'approxTokens': prepared.get('approxTokens'),
            'preparedBatchId': prepared.get('id'),
            'source': prepared.get('source'),
        })
        state['pendingBatch'] = ticket
        emit_outbox(ticket, state)
        state['lastDecision'] = 'batch'
        state['lastDecisionAt'] = now_iso()
        write_bridge_state(state)
        return {'ok': True, 'action': 'batch', 'outboxItem': ticket, 'source': 'preparedBatch'}

    cmd = [sys.executable, str(ROOM_MONITOR), 'next']
    if max_context is not None:
        cmd += ['--max-context', str(max_context)]
    out = run_json(cmd)
    action = out.get('action')
    state['lastDecision'] = action
    state['lastDecisionAt'] = now_iso()

    if action == 'heartbeat':
        item = make_item('telegram_heartbeat', {
            'roomId': out.get('roomId'),
            'text': out.get('telegramText'),
            'modelContextExcluded': True,
            'queueLength': out.get('queueLength', 0),
            'queueApproxTokens': out.get('queueApproxTokens', 0),
            'agentStatus': out.get('agentStatus'),
        })
        emit_outbox(item, state)
        write_bridge_state(state)
        return {'ok': True, 'action': 'heartbeat', 'outboxItem': item}

    if action == 'batch':
        ticket = make_item('model_batch', {
            'roomId': out.get('roomId'),
            'promptText': out.get('promptText', ''),
            'messages': out.get('messages', []),
            'maxContext': out.get('maxContext'),
            'selectedCount': out.get('selectedCount'),
            'droppedHeadCount': out.get('droppedHeadCount'),
            'approxTokens': out.get('approxTokens'),
        })
        state['pendingBatch'] = ticket
        emit_outbox(ticket, state)
        write_bridge_state(state)
        return {'ok': True, 'action': 'batch', 'outboxItem': ticket}

    write_bridge_state(state)
    return out


def cmd_tick(args):
    out = tick_once(args.max_context)
    print(json.dumps(out, indent=2))


def cmd_submit_reply(args):
    state = read_bridge_state()
    pending = state.get('pendingBatch')
    if not pending:
        raise SystemExit('No pending batch')
    if args.ticket_id != pending.get('id'):
        raise SystemExit(f'ticket mismatch: expected {pending.get("id")}')

    monitor_state = read_json_file(ROOT / 'runtime' / 'monitor.json', {})
    agent_state = run_json([sys.executable, str(ROOM_CLIENT), 'state', 'show'])
    room_id = pending.get('roomId') or monitor_state.get('roomId') or agent_state.get('activeRoomId')
    sender_id = args.sender_id or monitor_state.get('agentId') or agent_state.get('agentId', os.environ.get('CW_AGENT_ID', 'agent'))
    to_id = args.to_id or agent_state.get('ownerId', os.environ.get('CW_OWNER_ID', 'owner'))

    out = run_json([
        sys.executable, str(ROOM_MONITOR), 'reply-finish', args.text,
        '--room-id', str(room_id),
        '--sender-id', str(sender_id),
        '--to-id', str(to_id),
        '--next-status', args.next_status,
    ])

    item = make_item('telegram_reply', {
        'roomId': room_id,
        'text': args.text,
        'ticketId': pending.get('id'),
        'nextStatus': args.next_status,
    })
    emit_outbox(item, state)
    state['pendingBatch'] = None
    state['lastReplyAt'] = now_iso()
    state['lastDecision'] = 'reply-finished'
    state['lastDecisionAt'] = now_iso()
    write_bridge_state(state)
    print(json.dumps({'ok': True, 'action': 'submit-reply', 'ticketId': args.ticket_id, 'reply': out, 'outboxItem': item}, indent=2))


def cmd_outbox(args):
    items = load_outbox()
    if args.limit:
        items = items[-args.limit:]
    state = read_bridge_state()
    pending = pending_items(state, args.types)
    print(json.dumps({'ok': True, 'action': 'outbox', 'count': len(items), 'pendingCount': len(pending), 'pendingBatchId': (state.get('pendingBatch') or {}).get('id'), 'items': items}, indent=2))


def cmd_pull(args):
    state = read_bridge_state()
    items = pending_items(state, args.types)
    item = items[0] if items else None
    print(json.dumps({'ok': True, 'action': 'pull', 'found': bool(item), 'item': item, 'pendingCount': len(items)}, indent=2))


def cmd_ack(args):
    state = read_bridge_state()
    state = ack_item(state, args.item_id)
    write_bridge_state(state)
    print(json.dumps({'ok': True, 'action': 'ack', 'itemId': args.item_id, 'ackedCount': len(state.get('ackedItemIds', []))}, indent=2))


def cmd_status(args):
    state = read_bridge_state()
    pid = current_pid()
    running = bool(pid and pid_alive(pid))
    state['running'] = running
    state['pid'] = pid if running else None
    write_bridge_state(state)
    items = load_outbox()
    pending = pending_items(state)
    print(json.dumps({'ok': True, 'action': 'bridge-status', **state, 'outboxCount': len(items), 'pendingOutboxCount': len(pending), 'pendingBatchId': (state.get('pendingBatch') or {}).get('id')}, indent=2))


def _handle_signal(signum, frame):
    global RUNNING
    RUNNING = False


def cmd_run(args):
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    pid = os.getpid()
    BRIDGE_PID_PATH.write_text(str(pid))
    state = read_bridge_state()
    state.update({
        'running': True,
        'pid': pid,
        'intervalSec': args.interval,
        'startedAt': state.get('startedAt') or now_iso(),
        'stoppedAt': None,
    })
    write_bridge_state(state)
    append_log({'ts': now_iso(), 'type': 'bridge_started', 'pid': pid, 'intervalSec': args.interval})
    while RUNNING:
        try:
            out = tick_once(args.max_context)
            append_log({'ts': now_iso(), 'type': 'bridge_tick', 'result': out})
        except Exception as e:
            append_log({'ts': now_iso(), 'type': 'bridge_error', 'error': str(e)})
        time.sleep(args.interval)
    state = read_bridge_state()
    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    write_bridge_state(state)
    try:
        if current_pid() == pid:
            BRIDGE_PID_PATH.unlink()
    except FileNotFoundError:
        pass
    append_log({'ts': now_iso(), 'type': 'bridge_stopped', 'pid': pid})


def cmd_start(args):
    pid = current_pid()
    if pid and pid_alive(pid):
        state = read_bridge_state()
        state['running'] = True
        state['pid'] = pid
        write_bridge_state(state)
        print(json.dumps({'ok': True, 'action': 'bridge-start', 'running': True, 'pid': pid, 'alreadyRunning': True}, indent=2))
        return
    if pid and not pid_alive(pid):
        try:
            BRIDGE_PID_PATH.unlink()
        except FileNotFoundError:
            pass

    stderr = BRIDGE_LOG_PATH.open('a', encoding='utf-8')
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__)), 'run', '--interval', str(args.interval)] + ([ '--max-context', str(args.max_context)] if args.max_context is not None else []),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=stderr,
        start_new_session=True,
        close_fds=True,
    )
    BRIDGE_PID_PATH.write_text(str(proc.pid))
    time.sleep(0.2)
    state = read_bridge_state()
    state['running'] = pid_alive(proc.pid)
    state['pid'] = proc.pid if state['running'] else None
    state['intervalSec'] = args.interval
    if not state.get('startedAt'):
        state['startedAt'] = now_iso()
    write_bridge_state(state)
    print(json.dumps({'ok': True, 'action': 'bridge-start', 'running': state['running'], 'pid': proc.pid, 'intervalSec': args.interval, 'maxContext': args.max_context}, indent=2))


def cmd_stop(args):
    pid = current_pid()
    state = read_bridge_state()
    stopped = False
    if pid and pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            for _ in range(20):
                if not pid_alive(pid):
                    stopped = True
                    break
                time.sleep(0.1)
        except OSError:
            pass
    else:
        stopped = True
    try:
        BRIDGE_PID_PATH.unlink()
    except FileNotFoundError:
        pass
    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    write_bridge_state(state)
    print(json.dumps({'ok': True, 'action': 'bridge-stop', 'running': False, 'stopped': stopped}, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    st = sub.add_parser('start')
    st.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    st.add_argument('--max-context', type=int)
    st.set_defaults(func=cmd_start)

    sp = sub.add_parser('stop')
    sp.set_defaults(func=cmd_stop)

    ss = sub.add_parser('status')
    ss.set_defaults(func=cmd_status)

    tk = sub.add_parser('tick')
    tk.add_argument('--max-context', type=int)
    tk.set_defaults(func=cmd_tick)

    ob = sub.add_parser('outbox')
    ob.add_argument('--limit', type=int)
    ob.add_argument('--types', nargs='*')
    ob.set_defaults(func=cmd_outbox)

    pl = sub.add_parser('pull')
    pl.add_argument('--types', nargs='*')
    pl.set_defaults(func=cmd_pull)

    ak = sub.add_parser('ack')
    ak.add_argument('item_id')
    ak.set_defaults(func=cmd_ack)

    sr = sub.add_parser('submit-reply')
    sr.add_argument('ticket_id')
    sr.add_argument('text')
    sr.add_argument('--sender-id')
    sr.add_argument('--to-id')
    sr.add_argument('--next-status', default='listening')
    sr.set_defaults(func=cmd_submit_reply)

    rn = sub.add_parser('run')
    rn.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    rn.add_argument('--max-context', type=int)
    rn.set_defaults(func=cmd_run)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
