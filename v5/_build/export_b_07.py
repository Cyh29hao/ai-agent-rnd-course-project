"""Export official 07 in windowless PowerPoint; preserve the editable deck."""
from pathlib import Path
import json
import hashlib
import fitz
import pythoncom
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
qa=ROOT/'qa/b_integration_07'
png=qa/'slides';png.mkdir(exist_ok=True)
src=ROOT/'outputs/智能体产业研发_V5_07.pptx'
app=pres=None
pythoncom.CoInitialize()
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    pres=app.Presentations.Open(str(src),ReadOnly=1,Untitled=0,WithWindow=0)
    for n in range(1,pres.Slides.Count+1):pres.Slides(n).Export(str(png/f'{n:02}.png'),'PNG',1280,720)
    media=[pres.Slides(11).Shapes(i) for i in range(1,pres.Slides(11).Shapes.Count+1) if pres.Slides(11).Shapes(i).Type==16]
    durations=[int(shape.MediaFormat.Length) for shape in media]
    pres.Close();pres=None
    # An unsaved copy removes only this teaching video, exposing the editable
    # diagram underneath for a crisp, complete static PDF.
    pres=app.Presentations.Open(str(src),ReadOnly=0,Untitled=-1,WithWindow=0)
    removed=[]
    for i in range(pres.Slides(11).Shapes.Count,0,-1):
        shape=pres.Slides(11).Shapes(i)
        if shape.Name=='MechanismTeachingVideo_B07':removed.append(shape.Name);shape.Delete()
    assert removed==['MechanismTeachingVideo_B07']
    full=ROOT/'outputs/智能体产业研发_V5_07_含答辩.pdf'
    pres.SaveAs(str(full),32);pres.Close();pres=None
    doc=fitz.open(full)
    for start,end,name in [(0,23,'智能体产业研发_V5_07_主讲.pdf'),(7,12,'B部分投影_V5_07.pdf')]:
        part=fitz.open();part.insert_pdf(doc,from_page=start,to_page=end);part.save(ROOT/'outputs'/name);part.close()
    doc.close()
    receipt={'nativeOpen':True,'slides':34,'mainPages':24,'BPages':6,'mediaMilliseconds':durations,
             'pptxSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'staticPDF':'Removed B07 teaching video from an unsaved copy; native diagrams retained','foregroundPlaybackTested':False}
    (qa/'native.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
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
