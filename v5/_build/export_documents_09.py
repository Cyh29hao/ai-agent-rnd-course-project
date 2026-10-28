"""Export only task-owned 08 documents in invisible Microsoft Word."""
from pathlib import Path
from zipfile import ZipFile
import json
import hashlib
import argparse
import fitz
import pythoncom
import win32com.client
ROOT=Path(__file__).resolve().parents[1]
QA=ROOT/'qa/opening_09'
records=json.loads((QA/'documents_build.json').read_text(encoding='utf-8'))
parser=argparse.ArgumentParser();parser.add_argument('--a-only',action='store_true');parser.add_argument('--sources',nargs='+');args=parser.parse_args()
previous=json.loads((QA/'documents_export.json').read_text(encoding='utf-8')) if (args.a_only or args.sources) else []
pythoncom.CoInitialize();app=doc=None
try:
    app=win32com.client.DispatchEx('Word.Application');app.Visible=False;app.DisplayAlerts=0
    for record in records:
        if (args.a_only and not record['source'].startswith(('17_','18_'))) or (args.sources and not record['source'].startswith(tuple(args.sources))):
            record.update(next(r for r in previous if r['source']==record['source']));continue
        src=ROOT/'outputs'/record['docx'];pdf=src.with_suffix('.pdf')
        doc=app.Documents.Open(str(src),ReadOnly=True,AddToRecentFiles=False,Visible=False)
        doc.ExportAsFixedFormat(str(pdf),17);doc.Close(0);doc=None
        rendered=fitz.open(pdf);folder=QA/'documents'/src.stem;folder.mkdir(parents=True,exist_ok=True)
        for n,page in enumerate(rendered,1):page.get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(folder/f'page-{n}.png')
        for stale in folder.glob('page-*.png'):
            if int(stale.stem.split('-')[-1])>len(rendered):
                assert stale.resolve().parent==folder.resolve();stale.unlink()
        with ZipFile(src) as z:assert '\ufffd' not in z.read('word/document.xml').decode('utf-8')
        record.update(pdf=pdf.name,pages=len(rendered),pdfSha256=hashlib.sha256(pdf.read_bytes()).hexdigest(),
                      renderer='Microsoft Word COM invisible',pngDirectory=folder.relative_to(ROOT).as_posix())
        rendered.close()
    (QA/'documents_export.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps([{'file':r['docx'],'pages':r['pages']} for r in records],ensure_ascii=True))
finally:
    if doc is not None:
        try:doc.Close(0)
        except Exception:pass
    if app is not None:
        try:app.Quit(0)
        except Exception:pass
    pythoncom.CoUninitialize()
