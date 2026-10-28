"""Render the task-owned candidate invisibly before finalization."""
from pathlib import Path
import json,hashlib
import pythoncom
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
BUILD=ROOT/'_build/a_refinement_08'
QA=ROOT/'qa/a_refinement_08';PNG=QA/'slides';PNG.mkdir(exist_ok=True)
src=BUILD/'a_merged.pptx';pres=app=None
pythoncom.CoInitialize()
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    pres=app.Presentations.Open(str(src),ReadOnly=1,Untitled=0,WithWindow=0)
    assert pres.Slides.Count==34
    for n in range(1,35):pres.Slides(n).Export(str(PNG/f'{n:02}.png'),'PNG',1280,720)
    media=[pres.Slides(11).Shapes(i) for i in range(1,pres.Slides(11).Shapes.Count+1) if pres.Slides(11).Shapes(i).Type==16]
    duration=[int(s.MediaFormat.Length) for s in media]
    pres.Close();pres=None
    pres=app.Presentations.Open(str(src),ReadOnly=0,Untitled=-1,WithWindow=0)
    removed=[]
    for i in range(pres.Slides(11).Shapes.Count,0,-1):
        shape=pres.Slides(11).Shapes(i)
        if shape.Name=='MechanismTeachingVideo_B07':removed.append(shape.Name);shape.Delete()
    assert removed==['MechanismTeachingVideo_B07']
    pres.SaveAs(str(BUILD/'preview_含答辩.pdf'),32);pres.Close();pres=None
    receipt={'nativeOpen':True,'source':'_build/a_refinement_08/a_merged.pptx','candidateSha256':hashlib.sha256(src.read_bytes()).hexdigest(),
             'slides':34,'mediaMilliseconds':duration,'renderer':'Microsoft PowerPoint invisible','foregroundPlaybackTested':False,
             'PDF':'Static native diagram on page11; teaching video removed from unsaved copy only.'}
    (QA/'native_preview.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(receipt))
finally:
    if pres is not None:
        try:pres.Close()
        except Exception:pass
    if app is not None:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
