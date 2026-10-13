"""Prepare a student's empty evidence record. Does not run an agent or create answers."""
from pathlib import Path
import argparse,hashlib,json,re,datetime
p=argparse.ArgumentParser()
p.add_argument('--id',required=True)
a=p.parse_args()
if not re.fullmatch(r'[A-Za-z0-9_\-]{1,48}',a.id):
 p.error('Use 1-48 letters, numbers, underscores or hyphens for the record ID.')
root=Path(__file__).resolve().parent
out=root/'runs'/'students'/a.id
(out/'outputs').mkdir(parents=True,exist_ok=True)
inputs=['protocol_baseline.md','schema.json','smoke/claims.json','smoke/sources.json']
manifest={'record_id':a.id,'prepared_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'prepared_only_not_executed','executor_name':None,'model_id':None,'platform':None,'started_at':None,'ended_at':None,'tools_available':None,'sampling':'unknown','cost':'unknown','input_sha256':{n:hashlib.sha256((root/n).read_bytes()).hexdigest() for n in inputs},'agent_output':None,'validator_result':None,'human_source_review':None,'actual_contribution':None}
dest=out/'run_manifest.json'
if dest.exists():
 raise SystemExit('Existing record retained. Choose a new ID for a new run; no evidence was overwritten.')
dest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(out/'本人记录.md').write_text((root/'成员实际记录模板.md').read_text(encoding='utf-8'),encoding='utf-8')
print(json.dumps({'record_directory':str(out),'status':'prepared only; no agent was run'},ensure_ascii=True))
