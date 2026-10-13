"""Verify archived bytes in the working tree and committed Git objects, not report quality."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
MATERIALS = (ROOT / 'materials').resolve()
index = json.loads((ROOT / 'docs/材料存档清单.json').read_text(encoding='utf-8'))
process = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                           stdin=subprocess.PIPE, stdout=subprocess.PIPE)
failures = []
try:
    for name, expected in index['files'].items():
        path = (MATERIALS / name).resolve()
        if not path.is_relative_to(MATERIALS) or '\n' in name or '\r' in name:
            raise ValueError('Inventory path outside materials')
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            failures.append({'file': name, 'scope': 'working_tree'})
        process.stdin.write(('HEAD:materials/' + name + '\n').encode('utf-8'))
        process.stdin.flush()
        fields = process.stdout.readline().strip().split()
        if len(fields) != 3 or fields[1] != b'blob':
            raise ValueError('Committed material missing: ' + name)
        payload = process.stdout.read(int(fields[2]))
        if process.stdout.read(1) != b'\n':
            raise ValueError('Unexpected Git batch framing')
        if hashlib.sha256(payload).hexdigest() != expected:
            failures.append({'file': name, 'scope': 'committed_blob'})
finally:
    process.stdin.close()
    process.stdout.close()
    process.wait(timeout=10)
print(json.dumps({'files': len(index['files']), 'byte_integrity_pass': not failures,
                  'failures': failures, 'boundary': 'Does not establish factual accuracy, presentation usability or rehearsal.'},
                 ensure_ascii=True))
raise SystemExit(1 if failures else 0)
