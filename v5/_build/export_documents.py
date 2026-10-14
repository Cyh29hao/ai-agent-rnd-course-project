"""Native Word rendering fallback; packaged renderer needs absent LibreOffice."""
from pathlib import Path
import json,hashlib,sys
import pythoncom,win32com.client,fitz
ROOT=Path(__file__).resolve().parents[1]
pythoncom.CoInitialize();app=None;doc=None;receipts=[]
label=sys.argv[1] if len(sys.argv)>1 else ''
try:
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    for stem in ['课程报告_V5','四人口播_V5','来源与答辩_V5']:
        if label:stem+='_'+label
        src=ROOT/'outputs'/f'{stem}.docx';dst=src.with_suffix('.pdf')
        doc=app.Documents.Open(str(src),ReadOnly=True,AddToRecentFiles=False,Visible=False)
        doc.ExportAsFixedFormat(str(dst),17);doc.Close(0);doc=None
        pdf=fitz.open(dst);out=ROOT/'qa'/stem;out.mkdir(exist_ok=True)
        for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(out/f'{i+1:02}.png')
        for stale in out.glob('[0-9][0-9].png'):
            if int(stale.stem)>len(pdf):
                assert stale.resolve().parent==out.resolve()
                stale.unlink()
        receipts.append({'file':src.name,'pages':len(pdf),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'renderer':'Microsoft Word COM','pdf_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
    receipt='documents_export'+('_'+label if label else '')+'.json'
    (ROOT/'qa'/receipt).write_text(json.dumps(receipts,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(receipts,ensure_ascii=True))
finally:
    if doc:
        try:doc.Close(0)
        except Exception:pass
    if app:
        try:app.Quit(0)
        except Exception:pass
    pythoncom.CoUninitialize()
