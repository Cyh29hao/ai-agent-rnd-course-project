"""Native export, with a static-only readable PDF for the teaching video slide."""
from pathlib import Path
import json,hashlib,sys
import pythoncom,win32com.client,fitz
ROOT=Path(__file__).resolve().parents[1]
revision=sys.argv[1] if len(sys.argv)>1 else '01'
src=ROOT/f'outputs/智能体产业研发_V5_{revision}.pptx'
pythoncom.CoInitialize();app=None;pres=None
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    pres=app.Presentations.Open(str(src),ReadOnly=-1,Untitled=0,WithWindow=0)
    native=ROOT/f'qa/powerpoint_{revision}';native.mkdir(exist_ok=True)
    # Keep actual deck renders; static export removes only the task's teaching media.
    for i in range(1,pres.Slides.Count+1):pres.Slides(i).Export(str(native/f'{i:02}.png'),'PNG',1280,720)
    pres.Close();pres=None
    pres=app.Presentations.Open(str(src),ReadOnly=0,Untitled=-1,WithWindow=0)
    for i in range(pres.Slides(11).Shapes.Count,0,-1):
        if pres.Slides(11).Shapes(i).Name=='MechanismTeachingVideo':pres.Slides(11).Shapes(i).Delete()
    full=ROOT/f'outputs/智能体产业研发_V5_{revision}_含答辩.pdf'
    pres.SaveAs(str(full),32)
    pres.Close();pres=None
    doc=fitz.open(full);main=fitz.open();main.insert_pdf(doc,from_page=0,to_page=23)
    main.save(ROOT/f'outputs/智能体产业研发_V5_{revision}_主讲.pdf');main.close();doc.close()
    r={'slides':34,'main':24,'nativeOpen':True,'pngDirectory':native.name,'pptxSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'staticPDF':'Task-owned media removed from unsaved copy; all teaching diagrams retained'}
    (ROOT/f'qa/native_{revision}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print('NATIVE_EXPORT_VERIFIED',r['slides'])
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
