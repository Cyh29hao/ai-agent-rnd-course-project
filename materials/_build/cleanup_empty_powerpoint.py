# -*- coding: utf-8 -*-
"""Fresh COM client: stop only a registered, identity-checked empty task instance."""
from pathlib import Path
import json,subprocess,datetime
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
registry=ROOT/'qa/office_instances.json'
flags=getattr(subprocess,'CREATE_NO_WINDOW',0)

def snapshot():
    cmd="Get-CimInstance Win32_Process -Filter \"Name='POWERPNT.EXE'\" | ForEach-Object { [pscustomobject]@{ pid=$_.ProcessId; created_utc=$_.CreationDate.ToUniversalTime().ToString('o'); automation=($_.CommandLine -match '/AUTOMATION') } } | ConvertTo-Json -Compress"
    r=subprocess.run(['powershell.exe','-NoProfile','-Command',cmd],capture_output=True,text=True,encoding='utf-8',creationflags=flags,timeout=15,check=True)
    rows=json.loads(r.stdout) if r.stdout.strip() else []
    return rows if isinstance(rows,list) else [rows]

rows=snapshot()
if len(rows)!=1 or not registry.exists():raise SystemExit(0)
row=rows[0]
known=json.loads(registry.read_text(encoding='utf-8'))
if not row['automation'] or not any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in known):raise SystemExit(0)
try:
    active=win32com.client.GetActiveObject('PowerPoint.Application')
    count=active.Presentations.Count
except Exception:
    print('No cleanup: document state unavailable')
    raise SystemExit(0)
if count!=0:
    print('No cleanup: documents open')
    raise SystemExit(0)
# Recheck process identity after reading the document count. No mixed shell path operations.
current=snapshot()
if current!=[row]:raise SystemExit(0)
try:active.Quit()
except Exception:pass
current=snapshot()
if any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in current):
    subprocess.run(['powershell.exe','-NoProfile','-Command',f"Stop-Process -Id {int(row['pid'])} -ErrorAction Stop"],capture_output=True,text=True,encoding='utf-8',creationflags=flags,timeout=10,check=True)
with (ROOT/'qa/export_events.jsonl').open('a',encoding='utf-8') as f:
    f.write(json.dumps({'at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':'fresh_client_cleaned_verified_empty_task_instance','pid':row['pid'],'created_utc':row['created_utc']})+'\n')
print('Verified empty registered task instance cleaned')
