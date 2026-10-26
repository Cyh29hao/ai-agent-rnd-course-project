"""Render task documents through invisible Word; never close user documents."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import sys
import fitz
import pythoncom
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'qa/d_refinement_06/documents_build.json').read_text(encoding='utf-8'))
only=next((arg.split('=',1)[1].split(',') for arg in sys.argv if arg.startswith('--only=')),None)
previous={r['source']:r for r in json.loads((ROOT/'qa/d_refinement_06/documents_export.json').read_text(encoding='utf-8'))} if only else {}
pythoncom.CoInitialize()
app=doc=None
try:
    app=win32com.client.DispatchEx('Word.Application')
    app.Visible=False
    app.DisplayAlerts=0
    for record in records:
        if only and record['source'][:2] not in only:
            record.update(previous[record['source']])
            continue
        src=ROOT/'outputs'/record['docx']
        dst=src.with_suffix('.pdf')
        doc=app.Documents.Open(str(src),ReadOnly=True,AddToRecentFiles=False,Visible=False)
        doc.ExportAsFixedFormat(str(dst),17)
        doc.Close(0)
        doc=None
        pdf=fitz.open(dst)
        folder=ROOT/'qa/d_refinement_06/documents'/src.stem
        folder.mkdir(parents=True,exist_ok=True)
        for number,page in enumerate(pdf,1):
            page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(folder/f'page-{number}.png')
        for stale in folder.glob('page-*.png'):
            if int(stale.stem.split('-')[-1])>len(pdf):
                assert stale.resolve().parent==folder.resolve()
                stale.unlink()
        with ZipFile(src) as archive:
            xml=archive.read('word/document.xml').decode('utf-8')
            assert '\ufffd' not in xml
        record.update(pdf=dst.name,pages=len(pdf),renderer='Microsoft Word COM invisible',
                      pdfSha256=hashlib.sha256(dst.read_bytes()).hexdigest(),
                      pngDirectory=str(folder.relative_to(ROOT)))
        pdf.close()
    (ROOT/'qa/d_refinement_06/documents_export.json').write_text(
        json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps([{'file':r['docx'],'pages':r['pages']} for r in records],ensure_ascii=True))
finally:
    if doc is not None:
        try:doc.Close(0)
        except Exception:pass
    if app is not None:
        try:app.Quit(0)
        except Exception:pass
    pythoncom.CoUninitialize()
