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

ROOT = Path(__file__).resolve().parent.parent
RUNTIME_DIR = ROOT / 'runtime'
STATE_PATH = ROOT / 'state.json'
WORKER_STATE_PATH = RUNTIME_DIR / 'worker.json'
WORKER_PID_PATH = RUNTIME_DIR / 'worker.pid'
WORKER_LOG_PATH = RUNTIME_DIR / 'worker.log'
ROOM_BRIDGE = ROOT / 'scripts' / 'room_bridge.py'
DEFAULT_INTERVAL = 2.0
DEFAULT_AGENT_ID = os.environ.get('CW_AGENT_ID', 'agent')
DEFAULT_OWNER_ID = os.environ.get('CW_OWNER_ID', 'owner')
DEFAULT_TELEGRAM_TARGET = os.environ.get('CW_TELEGRAM_TARGET', '')
DEFAULT_TELEGRAM_CHANNEL = os.environ.get('CW_TELEGRAM_CHANNEL', 'telegram')
DEFAULT_TELEGRAM_ACCOUNT_ID = os.environ.get('CW_TELEGRAM_ACCOUNT_ID', '')
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


def append_log(entry):
    append_jsonl(WORKER_LOG_PATH, entry)


def default_worker_state():
    return {
        'running': False,
        'pid': None,
        'intervalSec': DEFAULT_INTERVAL,
        'startedAt': None,
        'stoppedAt': None,
        'lastPollAt': None,
        'lastHandledType': None,
        'lastHandledItemId': None,
        'lastMessageSentAt': None,
        'lastModelReplyAt': None,
        'telegramTarget': DEFAULT_TELEGRAM_TARGET,
        'telegramChannel': DEFAULT_TELEGRAM_CHANNEL,
        'telegramAccountId': DEFAULT_TELEGRAM_ACCOUNT_ID,
        'runtimeAgentId': 'main',
        'deliverReplyImmediately': True,
    }


def read_worker_state():
    return read_json_file(WORKER_STATE_PATH, default_worker_state())


def write_worker_state(state):
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    WORKER_STATE_PATH.write_text(json.dumps(state, indent=2))


def read_agent_state():
    return read_json_file(STATE_PATH, {'agentId': DEFAULT_AGENT_ID})


def pid_alive(pid):
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def current_pid():
    if not WORKER_PID_PATH.exists():
        return None
    try:
        return int(WORKER_PID_PATH.read_text().strip())
    except Exception:
        return None


def run_json(args):
    proc = subprocess.run(args, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f'command failed: {args}')
    out = proc.stdout.strip()
    if not out:
        return {}
    lines = [ln for ln in out.splitlines() if ln.strip()]
    for i in range(len(lines)):
        candidate = '\n'.join(lines[i:])
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    raise RuntimeError(f'Expected JSON output, got: {out[:500]}')


def openclaw_message_send(channel, target, message_text, account_id=None):
    cmd = ['openclaw', 'message', 'send', '--channel', channel, '--target', target, '--message', message_text, '--json']
    if account_id:
        cmd[3:3] = ['--account', account_id]
    return run_json(cmd)


def openclaw_agent_batch(agent_id, session_id, prompt_text):
    instruction = (
        'You are handling a Clawd\'s World trimmed room batch. '\
        'Reply to the human naturally, briefly, and helpfully using ONLY the supplied batch text as conversational input. '\
        'Keep the voice lightweight and direct. '\
        'Do not mention internal tooling, queues, bridge items, heartbeats, or hidden metadata unless the batch explicitly asks about them. '\
        'Do not fabricate extra context beyond the batch.\n\n' + prompt_text
    )
    cmd = [
        'openclaw', 'agent',
        '--agent', agent_id,
        '--session-id', session_id,
        '--message', instruction,
        '--json',
        '--thinking', 'low',
        '--timeout', '90',
    ]
    return run_json(cmd)


def extract_reply_text(agent_result):
    if isinstance(agent_result, dict):
        result = agent_result.get('result')
        if isinstance(result, dict):
            payloads = result.get('payloads')
            if isinstance(payloads, list):
                for payload in payloads:
                    if isinstance(payload, dict):
                        value = payload.get('text')
                        if isinstance(value, str) and value.strip():
                            return value.strip()
            for key in ('reply', 'text', 'message', 'output'):
                value = result.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        for key in ('reply', 'text', 'message', 'output'):
            value = agent_result.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return json.dumps(agent_result, ensure_ascii=False)


def handle_item(item, state):
    item_type = item.get('type')
    item_id = item.get('id')
    state['lastHandledType'] = item_type
    state['lastHandledItemId'] = item_id

    if item_type == 'telegram_heartbeat':
        target = state.get('telegramTarget', DEFAULT_TELEGRAM_TARGET)
        if target:
            sent = openclaw_message_send(state.get('telegramChannel', DEFAULT_TELEGRAM_CHANNEL), target, item.get('text', ''), state.get('telegramAccountId') or None)
        else:
            sent = {'skipped': 'no_telegram_target_configured'}
        run_json([sys.executable, str(ROOM_BRIDGE), 'ack', item_id])
        state['lastMessageSentAt'] = now_iso()
        append_log({'ts': now_iso(), 'type': 'handled_heartbeat', 'itemId': item_id, 'sent': sent})
        return {'ok': True, 'action': 'handled-heartbeat', 'itemId': item_id, 'sent': sent}

    if item_type == 'telegram_reply':
        target = state.get('telegramTarget', DEFAULT_TELEGRAM_TARGET)
        if target:
            sent = openclaw_message_send(state.get('telegramChannel', DEFAULT_TELEGRAM_CHANNEL), target, item.get('text', ''), state.get('telegramAccountId') or None)
        else:
            sent = {'skipped': 'no_telegram_target_configured'}
        run_json([sys.executable, str(ROOM_BRIDGE), 'ack', item_id])
        state['lastMessageSentAt'] = now_iso()
        append_log({'ts': now_iso(), 'type': 'handled_telegram_reply', 'itemId': item_id, 'sent': sent})
        return {'ok': True, 'action': 'handled-telegram-reply', 'itemId': item_id, 'sent': sent}

    if item_type == 'model_batch':
        agent_state = read_agent_state()
        runtime_agent_id = state.get('runtimeAgentId', 'main')
        session_id = f"cw-room-batch-{item_id}"
        agent_result = openclaw_agent_batch(runtime_agent_id, session_id, item.get('promptText', ''))
        reply_text = extract_reply_text(agent_result)
        submitted = run_json([
            sys.executable, str(ROOM_BRIDGE), 'submit-reply', item_id, reply_text,
            '--sender-id', agent_state.get('agentId', DEFAULT_AGENT_ID),
            '--to-id', agent_state.get('ownerId', DEFAULT_OWNER_ID),
            '--next-status', 'listening',
        ])
        run_json([sys.executable, str(ROOM_BRIDGE), 'ack', item_id])
        reply_item = (submitted.get('outboxItem') or {}) if isinstance(submitted, dict) else {}
        sent = None
        if reply_item.get('id') and reply_item.get('text'):
            target = state.get('telegramTarget', DEFAULT_TELEGRAM_TARGET)
            if target:
                sent = openclaw_message_send(state.get('telegramChannel', DEFAULT_TELEGRAM_CHANNEL), target, reply_item.get('text', ''), state.get('telegramAccountId') or None)
            else:
                sent = {'skipped': 'no_telegram_target_configured'}
            run_json([sys.executable, str(ROOM_BRIDGE), 'ack', reply_item.get('id')])
            state['lastMessageSentAt'] = now_iso()
        state['lastModelReplyAt'] = now_iso()
        append_log({'ts': now_iso(), 'type': 'handled_model_batch', 'itemId': item_id, 'replyText': reply_text, 'submitted': submitted, 'sent': sent})
        return {'ok': True, 'action': 'handled-model-batch', 'itemId': item_id, 'replyText': reply_text, 'submitted': submitted, 'sent': sent}

    run_json([sys.executable, str(ROOM_BRIDGE), 'ack', item_id])
    append_log({'ts': now_iso(), 'type': 'handled_unknown', 'item': item})
    return {'ok': True, 'action': 'handled-unknown', 'itemId': item_id}


def tick_once(types=None):
    state = read_worker_state()
    state['lastPollAt'] = now_iso()
    out = run_json([sys.executable, str(ROOM_BRIDGE), 'pull'] + ([ '--types', *types ] if types else []))
    item = out.get('item')
    if not item:
        write_worker_state(state)
        return {'ok': True, 'action': 'noop'}
    result = handle_item(item, state)
    write_worker_state(state)
    return result


def cmd_tick(args):
    out = tick_once(args.types)
    print(json.dumps(out, indent=2))


def cmd_status(args):
    state = read_worker_state()
    pid = current_pid()
    running = bool(pid and pid_alive(pid))
    state['running'] = running
    state['pid'] = pid if running else None
    write_worker_state(state)
    print(json.dumps({'ok': True, 'action': 'worker-status', **state}, indent=2))


def _handle_signal(signum, frame):
    global RUNNING
    RUNNING = False


def cmd_run(args):
    signal.signal(signal.SIGTERM, _handle_signal)
    signal.signal(signal.SIGINT, _handle_signal)
    pid = os.getpid()
    WORKER_PID_PATH.write_text(str(pid))
    state = read_worker_state()
    state.update({
        'running': True,
        'pid': pid,
        'intervalSec': args.interval,
        'startedAt': state.get('startedAt') or now_iso(),
        'stoppedAt': None,
    })
    write_worker_state(state)
    append_log({'ts': now_iso(), 'type': 'worker_started', 'pid': pid, 'intervalSec': args.interval})
    while RUNNING:
        try:
            out = tick_once(args.types)
            append_log({'ts': now_iso(), 'type': 'worker_tick', 'result': out})
        except Exception as e:
            append_log({'ts': now_iso(), 'type': 'worker_error', 'error': str(e)})
        time.sleep(args.interval)
    state = read_worker_state()
    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    write_worker_state(state)
    try:
        if current_pid() == pid:
            WORKER_PID_PATH.unlink()
    except FileNotFoundError:
        pass
    append_log({'ts': now_iso(), 'type': 'worker_stopped', 'pid': pid})


def cmd_start(args):
    pid = current_pid()
    if pid and pid_alive(pid):
        state = read_worker_state()
        state['running'] = True
        state['pid'] = pid
        write_worker_state(state)
        print(json.dumps({'ok': True, 'action': 'worker-start', 'running': True, 'pid': pid, 'alreadyRunning': True}, indent=2))
        return
    if pid and not pid_alive(pid):
        try:
            WORKER_PID_PATH.unlink()
        except FileNotFoundError:
            pass
    stderr = WORKER_LOG_PATH.open('a', encoding='utf-8')
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__)), 'run', '--interval', str(args.interval)] + ([ '--types', *args.types ] if args.types else []),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=stderr,
        start_new_session=True,
        close_fds=True,
    )
    WORKER_PID_PATH.write_text(str(proc.pid))
    time.sleep(0.2)
    state = read_worker_state()
    state['running'] = pid_alive(proc.pid)
    state['pid'] = proc.pid if state['running'] else None
    state['intervalSec'] = args.interval
    write_worker_state(state)
    print(json.dumps({'ok': True, 'action': 'worker-start', 'running': state['running'], 'pid': proc.pid, 'intervalSec': args.interval, 'types': args.types}, indent=2))


def cmd_stop(args):
    pid = current_pid()
    state = read_worker_state()
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
        WORKER_PID_PATH.unlink()
    except FileNotFoundError:
        pass
    state['running'] = False
    state['pid'] = None
    state['stoppedAt'] = now_iso()
    write_worker_state(state)
    print(json.dumps({'ok': True, 'action': 'worker-stop', 'running': False, 'stopped': stopped}, indent=2))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd', required=True)

    st = sub.add_parser('start')
    st.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    st.add_argument('--types', nargs='*')
    st.set_defaults(func=cmd_start)

    sp = sub.add_parser('stop')
    sp.set_defaults(func=cmd_stop)

    ss = sub.add_parser('status')
    ss.set_defaults(func=cmd_status)

    tk = sub.add_parser('tick')
    tk.add_argument('--types', nargs='*')
    tk.set_defaults(func=cmd_tick)

    rn = sub.add_parser('run')
    rn.add_argument('--interval', type=float, default=DEFAULT_INTERVAL)
    rn.add_argument('--types', nargs='*')
    rn.set_defaults(func=cmd_run)

    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
