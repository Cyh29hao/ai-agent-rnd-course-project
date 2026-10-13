"""Freeze the paired production demonstration before execution."""
from pathlib import Path
import hashlib,json,datetime
root=Path(__file__).resolve().parent
files=['protocol_baseline.md','protocol_candidate.md','sources.json','schema.json','demo/claims.json']
record={'frozen_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_id':'gpt-6-sol','executor':'Codex native production agents','design':'two independent fresh variant contexts, 16 claims processed as one batch per variant','max_tool_calls_per_batch':10,'sampling':'not exposed by native subagent interface','is_sealed_holdout':False,'limitation':'Shared workspace permits access. Gold is excluded from prompts and agents are instructed not to read it. No OS isolation; source-author summaries and demo authorship preclude independent validation. Batch design is a demonstration deviation from proposed student per-claim protocol. No development-based optimization claim.','sha256':{f:hashlib.sha256((root/f).read_bytes()).hexdigest() for f in files}}
out=root/'runs'/'demo'/'freeze.json'
out.parent.mkdir(parents=True,exist_ok=True)
if out.exists(): raise SystemExit('Existing freeze retained; start another named run instead of overwriting.')
out.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(record))
