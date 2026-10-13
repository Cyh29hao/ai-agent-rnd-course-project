"""Native Word fallback when bundled LibreOffice is unavailable on Windows."""
from pathlib import Path
import json,hashlib
import pythoncom,win32com.client,fitz
ROOT=Path(__file__).resolve().parents[1]
pythoncom.CoInitialize();app=None;doc=None;receipts=[]
try:
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    for stem in ['课程报告_V4','四人口播_V4']:
        src=ROOT/'outputs'/f'{stem}.docx';dst=src.with_suffix('.pdf')
        doc=app.Documents.Open(str(src),ReadOnly=True,AddToRecentFiles=False,Visible=False)
        doc.ExportAsFixedFormat(str(dst),17);doc.Close(0);doc=None
        pdf=fitz.open(dst);out=ROOT/'qa'/stem;out.mkdir(exist_ok=True)
        for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(out/f'{i+1:02}.png')
        receipts.append({'file':src.name,'pages':len(pdf),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'renderer':'Microsoft Word COM','pdf_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
    (ROOT/'qa/documents_export.json').write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipts,ensure_ascii=True))
finally:
    if doc:
        try:doc.Close(0)
        except Exception:pass
    if app:
        try:app.Quit(0)
        except Exception:pass
    pythoncom.CoUninitialize()
