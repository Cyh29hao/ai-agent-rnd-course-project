# -*- coding: utf-8 -*-
"""Export with source hashes; clean only verified task-created empty instances."""
from pathlib import Path
import hashlib,json,os,subprocess,datetime,tempfile,uuid,shutil,time,sys
import pythoncom
import win32com.client

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'01_正式汇报.pptx'
DST=ROOT/'03_完整备份版.pdf'
TMP=Path(tempfile.gettempdir())/f'ai_rnd_v3_{uuid.uuid4().hex}.pdf'
REGISTRY=ROOT/'qa'/'office_instances.json'
LOG=ROOT/'qa'/'export_events.jsonl'
FLAGS=getattr(subprocess,'CREATE_NO_WINDOW',0)

def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def emit(event,**fields):
    with LOG.open('a',encoding='utf-8') as stream:
        stream.write(json.dumps({'at':now(),'event':event,**fields},ensure_ascii=False)+'\n')

def snapshot():
    command="Get-CimInstance Win32_Process -Filter \"Name='POWERPNT.EXE'\" | ForEach-Object { [pscustomobject]@{ pid=$_.ProcessId; created_utc=$_.CreationDate.ToUniversalTime().ToString('o'); automation=($_.CommandLine -match '/AUTOMATION') } } | ConvertTo-Json -Compress"
    result=subprocess.run(['powershell.exe','-NoProfile','-Command',command],capture_output=True,text=True,encoding='utf-8',creationflags=FLAGS,timeout=20,check=True)
    data=json.loads(result.stdout) if result.stdout.strip() else []
    return data if isinstance(data,list) else [data]

def register(rows):
    known=json.loads(REGISTRY.read_text(encoding='utf-8')) if REGISTRY.exists() else []
    for row in rows:
        if row['automation'] and not any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in known):
            known.append({**row,'registered_at':now(),'created_by':'this export; process absent before DispatchEx'})
    REGISTRY.write_text(json.dumps(known,ensure_ascii=False,indent=2),encoding='utf-8')

def cleanup_empty_registered():
    rows=snapshot()
    if len(rows)!=1 or not REGISTRY.exists(): return
    row=rows[0]
    known=json.loads(REGISTRY.read_text(encoding='utf-8'))
    if not row['automation'] or not any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in known): return
    try:
        last_error=None
        for attempt in range(3):
            try:
                active=win32com.client.GetActiveObject('PowerPoint.Application')
                count=active.Presentations.Count
                break
            except Exception as exc:
                last_error=exc
                if attempt==2: raise
                time.sleep(.5)
        if count!=0:
            emit('cleanup_skipped_open_documents',pid=row['pid'],open_count=count);return
        active.Quit()
    except Exception as exc:
        emit('cleanup_skipped_unverified_document_state',pid=row['pid'],reason=str(exc));return
    remaining=snapshot()
    if not any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in remaining): return
    try:
        active=win32com.client.GetActiveObject('PowerPoint.Application')
        if active.Presentations.Count!=0: return
    except Exception:
        pass  # The registered task application accepted Quit with no open documents.
    subprocess.run(['powershell.exe','-NoProfile','-Command',f"Stop-Process -Id {int(row['pid'])} -ErrorAction Stop"],capture_output=True,text=True,encoding='utf-8',creationflags=FLAGS,timeout=10,check=True)
    emit('stopped_registered_empty_automation',pid=row['pid'],created_utc=row['created_utc'])

subprocess.run([sys.executable,str(ROOT/'_build/cleanup_empty_powerpoint.py')],capture_output=True,text=True,encoding='utf-8',creationflags=FLAGS,timeout=45,check=True)
pythoncom.CoInitialize()
app=None;pres=None
try:
    cleanup_empty_registered()
    before=snapshot()
    digest=hashlib.sha256(SRC.read_bytes()).hexdigest()
    app=win32com.client.DispatchEx('PowerPoint.Application')
    try:app.Visible=-1;app.WindowState=2
    except Exception:pass
    after=snapshot()
    register([row for row in after if not any(x['pid']==row['pid'] and x['created_utc']==row['created_utc'] for x in before)])
    emit('opening_source',source=str(SRC),sha256=digest)
    pres=app.Presentations.Open(str(SRC),ReadOnly=-1,Untitled=0,WithWindow=0)
    slide_count=pres.Slides.Count
    pres.SaveAs(str(TMP),32)
    pres.Close();pres=None
    local_tmp=DST.with_suffix('.exporting.pdf')
    shutil.copyfile(TMP,local_tmp)
    os.replace(local_tmp,DST)
    TMP.unlink()
    manifest={'exported_at':now(),'source_file':SRC.name,'source_sha256':digest,'pdf_file':DST.name,'pdf_sha256':hashlib.sha256(DST.read_bytes()).hexdigest(),'slide_count':slide_count,'renderer':'Microsoft PowerPoint COM'}
    (ROOT/'qa'/'export_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    emit('export_success',**manifest)
    print(json.dumps(manifest,ensure_ascii=True))
except Exception as exc:
    emit('export_failed',reason=str(exc),source=str(SRC))
    raise
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    try:cleanup_empty_registered()
    except Exception as exc:emit('cleanup_warning',reason=str(exc))
    pythoncom.CoUninitialize()
