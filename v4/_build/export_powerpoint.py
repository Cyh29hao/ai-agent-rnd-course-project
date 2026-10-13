"""Export only this deck using a task-owned automation instance."""
from pathlib import Path
import json,hashlib
import pythoncom
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'outputs/智能体产业研发_V4_试讲版_02.pptx'
dst=ROOT/'outputs/智能体产业研发_V4_完整.pdf'
pythoncom.CoInitialize()
app=None;pres=None
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    pres=app.Presentations.Open(str(src),ReadOnly=-1,Untitled=0,WithWindow=0)
    count=pres.Slides.Count
    pres.SaveAs(str(dst),32)
    pres.Close();pres=None
    import fitz
    doc=fitz.open(dst)
    main=fitz.open();main.insert_pdf(doc,from_page=0,to_page=17)
    main.save(ROOT/'outputs/智能体产业研发_V4_主讲.pdf')
    render=ROOT/'qa/powerpoint';render.mkdir(exist_ok=True)
    for i,page in enumerate(doc):
        page.get_pixmap(matrix=fitz.Matrix(1,1)).save(render/f'{i+1:02}.png')
    receipt={'renderer':'Microsoft PowerPoint COM','slide_count':count,'pdf_pages':len(doc),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'pdf_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'boundary':'Native file export and rendered pages; no human rehearsal or playback test.'}
    (ROOT/'qa/powerpoint_export.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipt,ensure_ascii=True))
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
