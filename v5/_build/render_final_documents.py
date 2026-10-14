from pathlib import Path
import json,hashlib
import fitz
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'qa/documents_03';out.mkdir(exist_ok=True)
records=[]
for stem in ['课程报告_V5','四人口播_V5','来源与答辩_V5']:
    pdf=fitz.open(ROOT/'outputs'/f'{stem}.pdf');folder=out/stem;folder.mkdir(exist_ok=True)
    for i,page in enumerate(pdf):page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(folder/f'{i+1:02}.png')
    records.append({'file':stem,'pages':len(pdf),'sha256':hashlib.sha256((ROOT/'outputs'/f'{stem}.pdf').read_bytes()).hexdigest()})
(out/'manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(records))
