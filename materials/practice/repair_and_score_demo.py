"""Preserve failed provenance, document repair, score unchanged outputs."""
from pathlib import Path
import json,hashlib,datetime,subprocess,sys
root=Path(__file__).resolve().parent
runs=root/'runs'/'demo'
failed=runs/'baseline'/'metadata.json'
archive=failed.with_name('metadata.failed-original.json')
if not archive.exists(): archive.write_bytes(failed.read_bytes())
actions=[json.loads(x) for x in (runs/'baseline'/'actions.jsonl').read_text(encoding='utf-8').splitlines() if x.strip()]
freeze=json.loads((runs/'freeze.json').read_text(encoding='utf-8'))
repair={'model_id':freeze['model_id'],'executor':'Codex native baseline production agent','source_review_started_at':None,'source_review_start_note':'No start timestamp instrumented; agent observed clock 2026-10-13 03:38:40 UTC during run. Do not infer full wall time.','output_generation_recorded_at':'2026-10-13T03:39:50.847851+00:00','last_recorded_action_at':actions[-1]['recorded_at'],'sampling':'not exposed','raw_action_entries':len(actions),'nested_tool_calls':None,'nested_tool_calls_note':'Agent declared 10 but action history has 11 entries. Without raw event reconciliation, cost comparison is unverified.','design':freeze['design'],'sha256':freeze['sha256'],'repair':{'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operator':'root production agent','reason':'Final PowerShell update replaced metadata with JSON null. Original preserved, model judgments unmodified.','original_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'scope':'Reconstructed only fields traceable to freeze, recorded actions and agent handoff. Missing fields retained null.'}}
failed.write_text(json.dumps(repair,ensure_ascii=False,indent=2),encoding='utf-8')
out=runs/'score.json'
cmd=[sys.executable,str(root/'score.py'),'--claims',str(root/'demo'/'claims.json'),'--gold',str(root/'demo'/'gold.json'),'--sources',str(root/'sources.json'),'--variant','baseline='+str(runs/'baseline'/'outputs'),'--variant','candidate='+str(runs/'candidate'/'outputs'),'--out',str(out)]
result=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8')
if result.returncode: raise SystemExit(result.stderr)
scores=json.loads(out.read_text(encoding='utf-8'))
print(json.dumps({name:{k:data[k] for k in ['total','valid_outputs','label_correct','false_release','risky_gold_total','location_correct']} for name,data in scores['variants'].items()}))
