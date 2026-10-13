"""One-shot scheduled FIR execution, with a real scheduler/model preflight."""
from __future__ import annotations

import argparse
import importlib.util
import json
import msvcrt
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from datetime import datetime

ROOT = Path(__file__).resolve().parent
CFG = json.loads((ROOT / 'config.json').read_text(encoding='utf-8'))
TARGET = datetime.fromisoformat(CFG['not_before'])
FLAGS = subprocess.CREATE_NO_WINDOW
STATUS = ROOT / 'status.json'
STOP = ROOT / 'STOP_REQUESTED'
CLOSEOUT = ROOT / 'CLOSEOUT_REQUESTED.txt'


def now():
    return datetime.now(TARGET.tzinfo).isoformat(timespec='seconds')


def save(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
    os.replace(temporary, path)


def event(name, **values):
    with (ROOT / 'scheduler.jsonl').open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'time': now(), 'event': name, **values}, ensure_ascii=False) + '\n')


def state(phase, **values):
    save(STATUS, {'phase': phase, 'updated_at': now(), 'not_before': CFG['not_before'], **values})


def quota():
    spec = importlib.util.spec_from_file_location('ai_rnd_quota', CFG['quota_checker'])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    response = module.read_rate_limits(CFG['codex'])
    limits = response.get('rateLimits') or response.get('rateLimitsByLimitId', {}).get('codex')
    if not isinstance(limits, dict):
        raise RuntimeError('Quota bucket unavailable')
    result = {}
    for label, key in [('five_hour', 'primary'), ('weekly', 'secondary')]:
        window = limits.get(key) or {}
        if window.get('usedPercent') is None:
            raise RuntimeError('Quota percentage unavailable: ' + label)
        result[label] = max(0, 100 - float(window['usedPercent']))
        result[label + '_reset'] = window.get('resetsAt')
    return result


def command(output, *, probe=False, resume=None):
    args = [CFG['codex'], 'exec', '-C', CFG['workspace'],
            '-s', 'read-only' if probe else 'danger-full-access',
            '-c', 'approval_policy="never"',
            '-c', 'model_reasoning_effort="low"' if probe else 'model_reasoning_effort="medium"',
            *(['resume', resume] if resume else []),
            '--disable', 'hooks', '--skip-git-repo-check', '-m', CFG['model'],
            '--json', '-o', str(output), '-']
    if probe:
        args.insert(-1, '--ephemeral')
    return args


def invoke(label, prompt, *, probe=False, resume=None):
    messages = queue.Queue()
    final = ROOT / (label + '.last.md')
    env = os.environ.copy()
    env['CODEX_CLI_PATH'] = CFG['codex']
    env['PYTHONIOENCODING'] = 'utf-8'
    env['AI_RND_SCHEDULED_RUN'] = CFG['task_name']
    env.pop('CODEX_THREAD_ID', None)
    env.pop('CODEX_SESSION_ID', None)
    with (ROOT / (label + '.stderr.log')).open('w', encoding='utf-8') as stderr, \
         (ROOT / (label + '.jsonl')).open('w', encoding='utf-8') as output:
        process = subprocess.Popen(command(final, probe=probe, resume=resume),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr,
            text=True, encoding='utf-8', errors='replace', cwd=CFG['workspace'],
            creationflags=FLAGS, env=env)
        state('preflight_running' if probe else 'working', worker_pid=process.pid, log=str(output.name))
        process.stdin.write(prompt)
        process.stdin.close()

        def read():
            for line in process.stdout:
                messages.put(line)
        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        started = time.monotonic()
        check_at = started + 120
        actual_thread = None
        completed = False
        while process.poll() is None or reader.is_alive() or not messages.empty():
            try:
                line = messages.get(timeout=0.5)
                try:
                    value = json.loads(line)
                except json.JSONDecodeError:
                    value = {'type': 'non_json', 'text': line.strip()}
                if (value.get('item') or {}).get('type') == 'reasoning':
                    continue
                if value.get('type') == 'thread.started':
                    actual_thread = value.get('thread_id')
                    state('preflight_running' if probe else 'working',
                          worker_pid=process.pid, actual_thread=actual_thread, log=str(output.name))
                if value.get('type') == 'turn.completed':
                    completed = True
                output.write(json.dumps(value, ensure_ascii=False) + '\n')
                output.flush()
            except queue.Empty:
                pass
            if probe and time.monotonic() - started > 180 and process.poll() is None:
                process.kill()
                event('preflight_timeout')
            if not probe and time.monotonic() >= check_at and process.poll() is None:
                try:
                    q = quota()
                    event('quota_during_execution', **q)
                    if min(q['five_hour'], q['weekly']) <= CFG['closeout_percent'] or STOP.exists():
                        CLOSEOUT.write_text('Finish current safe step, verify minimally, save incomplete handoff, stop.\n', encoding='utf-8')
                    if q['five_hour'] <= 20:
                        event('hard_quota_stop', **q)
                        process.terminate()
                except Exception as exc:
                    event('quota_unavailable', reason=str(exc))
                    CLOSEOUT.write_text('Quota unavailable. Save checkpoint and incomplete handoff before more long work.\n', encoding='utf-8')
                check_at = time.monotonic() + 120
        process.wait()
        reader.join(timeout=2)
    event('process_finished', label=label, exit_code=process.returncode,
          turn_completed=completed, actual_thread=actual_thread)
    return process.returncode, completed, actual_thread, final


def preflight():
    checks = {key: Path(CFG[key]).exists() for key in ['codex', 'quota_checker', 'workspace']}
    if not all(checks.values()):
        raise RuntimeError('Missing paths: ' + repr(checks))
    q = quota()
    # Only a tiny model response. No assignment work occurs before TARGET.
    rc, completed, thread, final = invoke('preflight',
        'This is ONLY a scheduled-launch connectivity preflight authorized by the user. '
        'Do not begin the course presentation work. Do not use tools or modify any files. '
        'Your final answer must be exactly AI_RND_SCHEDULER_PREFLIGHT_OK.', probe=True)
    passed = rc == 0 and completed and final.exists() and final.read_text(encoding='utf-8').strip() == 'AI_RND_SCHEDULER_PREFLIGHT_OK'
    report = {'time': now(), 'passed': passed, 'paths': checks, 'quota': q,
              'exit_code': rc, 'turn_completed': completed, 'actual_thread': thread}
    save(ROOT / 'preflight.json', report)
    if not passed:
        raise RuntimeError('Real Codex preflight failed; inspect preflight.stderr.log')
    state('scheduled_ready', preflight=report)


def delivery_complete():
    path=Path(CFG['workspace'])/'qa'/'v4_delivery_manifest.json'
    if not path.exists(): return False
    value=json.loads(path.read_text(encoding='utf-8'))
    if value.get('version')!='V4' or value.get('status')!='ready_for_user_review': return False
    if not all(value.get('checks',{}).get(k) is True for k in ['narrative','natural_speech','render_review','script_matches_slides','ten_minute_budget']): return False
    import hashlib
    for name,digest in value.get('sha256',{}).items():
        p=(Path(CFG['workspace'])/name).resolve()
        if not p.is_relative_to(Path(CFG['workspace']).resolve()) or not p.is_file(): return False
        if hashlib.sha256(p.read_bytes()).hexdigest()!=digest: return False
    return len(value.get('sha256',{}))>=4


def dispatch():
    if datetime.now(TARGET.tzinfo) < TARGET:
        preflight()
        return 0
    if STOP.exists():
        state('cancelled')
        return 0
    if delivery_complete():
        state('complete', reason='Existing verified delivery; duplicate launch skipped')
        return 0
    deadline = time.monotonic() + 1800
    while time.monotonic() < deadline:
        try:
            q = quota()
            reset = q.get('five_hour_reset')
            recovered = q['five_hour'] >= 50 or (isinstance(reset, (int, float)) and reset > TARGET.timestamp())
            if recovered and min(q['five_hour'], q['weekly']) > CFG['closeout_percent']:
                event('quota_gate_passed', **q)
                break
            state('waiting_for_quota', quota=q)
        except Exception as exc:
            state('waiting_for_quota', reason=str(exc))
        if STOP.exists():
            state('cancelled')
            return 0
        time.sleep(60)
    else:
        state('blocked', reason='Quota unavailable or not recovered for 30 minutes; assignment not started')
        return 2
    thread = None
    prompt = (ROOT / 'execution_prompt.md').read_text(encoding='utf-8')
    for attempt in range(1, 4):
        rc, completed, actual_thread, final = invoke('run_%03d' % attempt,
            prompt if attempt == 1 else prompt + '\nContinue from the checkpoint. Previous run returned without a verified complete delivery. Finish only outstanding work.',
            resume=thread)
        thread = actual_thread or thread
        if delivery_complete():
            state('complete', actual_thread=thread, final_message=str(final))
            return 0
        if CLOSEOUT.exists() or STOP.exists():
            state('incomplete', actual_thread=thread, final_message=str(final), reason='Closeout or stop requested')
            return 2
        q = quota()
        if min(q['five_hour'], q['weekly']) <= CFG['closeout_percent']:
            state('incomplete', actual_thread=thread, final_message=str(final), reason='Quota closeout')
            return 2
        event('bounded_retry', attempt=attempt, exit_code=rc, turn_completed=completed)
        if attempt < 3:
            time.sleep(30)
    state('incomplete', actual_thread=thread, reason='Three bounded attempts without verified delivery; inspect logs')
    return 2


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dispatch', action='store_true')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    if args.check_only:
        for key in ['codex', 'quota_checker', 'workspace']:
            assert Path(CFG[key]).exists(), key
        assert (ROOT / 'execution_prompt.md').read_text(encoding='utf-8').startswith('# 已批准')
        print(json.dumps({'passed': True, 'not_before': CFG['not_before'],
                          'model': CFG['model'], 'command': command(ROOT / 'run.last.md')}, ensure_ascii=False))
        return 0
    if not args.dispatch:
        parser.error('--dispatch or --check-only required')
    with (ROOT / 'run.lock').open('a+b') as lock:
        lock.seek(0)
        if lock.read(1) == b'':
            lock.write(b'0')
            lock.flush()
        lock.seek(0)
        try:
            msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return 0
        try:
            return dispatch()
        except Exception as exc:
            event('runner_error', reason=str(exc))
            state('error', reason=str(exc))
            return 1


if __name__ == '__main__':
    raise SystemExit(main())
