"""Export the approval samples and silent media from task-owned PowerPoint instances."""
from pathlib import Path
import json,time,hashlib,sys
import pythoncom,win32com.client,fitz
ROOT=Path(__file__).resolve().parents[1]
pythoncom.CoInitialize();app=None;pres=None;receipts=[]
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    src=ROOT/'outputs/审批样页_05.pptx'
    pres=app.Presentations.Open(str(src),ReadOnly=-1,Untitled=0,WithWindow=0)
    dst=src.with_suffix('.pdf');pres.SaveAs(str(dst),32)
    native=ROOT/'qa/powerpoint';native.mkdir(exist_ok=True)
    for i in range(1,pres.Slides.Count+1):pres.Slides(i).Export(str(native/f'{i:02}.png'),'PNG',1280,720)
    receipts.append({'file':src.name,'slides':pres.Slides.Count,'renderer':'PowerPoint','sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
    pres.Close();pres=None
    video_jobs=[] if '--skip-video' in sys.argv else [('mechanism','机制教学示意_18秒',6),('trace','本项目工件重排_12秒',4)]
    if not video_jobs:
        for record in json.loads((ROOT/'qa/native_export.json').read_text(encoding='utf-8')):
            if record['file'].endswith('.mp4'):
                assert hashlib.sha256((ROOT/'outputs'/record['file']).read_bytes()).hexdigest()==record['sha256']
                receipts.append(record)
    for stem,name,seconds in video_jobs:
        frames=ROOT/'_build'/f'{stem}_frames.pptx'
        pres=app.Presentations.Open(str(frames),ReadOnly=-1,Untitled=0,WithWindow=0)
        frame_dir=ROOT/'qa'/stem;frame_dir.mkdir(exist_ok=True)
        for i in range(1,pres.Slides.Count+1):pres.Slides(i).Export(str(frame_dir/f'{i:02}.png'),'PNG',1280,720)
        target=ROOT/'outputs'/f'{name}.mp4'
        pres.CreateVideo(str(target),False,seconds,720,25,85)
        started=time.monotonic()
        while time.monotonic()-started<240:
            state=pres.CreateVideoStatus
            if state==3 and target.exists() and target.stat().st_size>10000:break
            if state==4:raise RuntimeError(f'Video failed {stem}')
            time.sleep(1)
        else:raise TimeoutError(f'Video timed out {stem}')
        receipts.append({'file':target.name,'seconds_design':seconds*pres.Slides.Count,'renderer':'PowerPoint CreateVideo','sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'disclosure':'Method illustration' if stem=='mechanism' else 'Existing artifacts rearranged; not UI recording'})
        print(f'VIDEO_EXPORTED {stem}',flush=True)
        pres.Close();pres=None
    (ROOT/'qa/native_export.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipts,ensure_ascii=True))
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
