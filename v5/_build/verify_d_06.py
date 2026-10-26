"""Verify revision 06 files and the exact preservation boundary."""
from pathlib import Path
from zipfile import ZipFile
import hashlib
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import fitz
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
QA=ROOT/'qa/d_refinement_06'
OUT=ROOT/'outputs'
OLD=OUT/'智能体产业研发_V5_05.pptx'
NEW=OUT/'智能体产业研发_V5_06.pptx'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def norm(text):return re.sub(r'\W+','',text)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
baseline=json.loads(subprocess.check_output(['git','show','630480656df03f342e1d1dfe9bf12491bac322c3:v5/主讲内容.json'],cwd=REPO).decode('utf-8'))
assert baseline[:18]==data[:18],'ABC source changed'
assert len(data)==24 and sum(s['seconds'] for s in data)==850
assert sum(s['seconds'] for s in data[18:])==190
spoken=(ROOT/'01_自然口播稿.md').read_text(encoding='utf-8')
practice=(ROOT/'11_D部分口播与练习.md').read_text(encoding='utf-8')
permitted={f'ppt/slides/slide{n}.xml' for n in [19,21,22,23]}
permitted.update(f'ppt/notesSlides/notesSlide{n}.xml' for n in [19,20,21,22,23,24,33])
with ZipFile(OLD) as old,ZipFile(NEW) as new:
    assert old.namelist()==new.namelist()
    changed=[p for p in old.namelist() if old.read(p)!=new.read(p)]
    assert set(changed)<=permitted,changed
    assert all(f'ppt/slides/slide{n}.xml' in changed for n in [19,21,22,23])
    assert len([p for p in new.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',p)])==34
    for slide in data[18:]:
        note=ET.fromstring(new.read(f'ppt/notesSlides/notesSlide{slide["n"]}.xml'))
        text=''.join(note.itertext())
        assert slide['script'] in text,slide['n']
        assert slide['script'] in spoken and slide['script'] in practice,slide['n']
    media=[p for p in old.namelist() if p.startswith(('ppt/media/','ppt/charts/','ppt/embeddings/'))]
    assert media and all(old.read(p)==new.read(p) for p in media)

pixel_changed=[]
for n in range(1,35):
    a=Image.open(ROOT/f'qa/powerpoint_05/{n:02}.png').convert('RGB')
    b=Image.open(ROOT/f'qa/powerpoint_06/{n:02}.png').convert('RGB')
    if ImageChops.difference(a,b).getbbox():pixel_changed.append(n)
assert pixel_changed==[19,21,22,23],pixel_changed
validation=json.loads((QA/'validation.json').read_text(encoding='utf-8'))
assert validation['finalSha256']==sha(NEW)
assert validation['packageIntegrity']['exitCode']==0
assert validation['presentationLayout']['exitCode']==0
assert validation['firstPartyImport']['passed']
native=json.loads((ROOT/'qa/native_06.json').read_text(encoding='utf-8'))
assert native['nativeOpen'] and native['pptxSha256']==sha(NEW)
assert len(fitz.open(OUT/'智能体产业研发_V5_06_主讲.pdf'))==24
assert len(fitz.open(OUT/'智能体产业研发_V5_06_含答辩.pdf'))==34

records=json.loads((QA/'documents_export.json').read_text(encoding='utf-8'))
original_doc=REPO/'collaboration/proposals/D_曹天卓_20261025/D_19-24页_曹天卓_V5修订.docx'
assert sha(original_doc)=='a47a1d4099d8f7e2b48686854f7802e7e4bfc47b90f46673f63b960313b22bf6'
with fitz.open(OUT/'D部分投影_V5_06.pdf') as part,fitz.open(OUT/'智能体产业研发_V5_06_主讲.pdf') as full:
    assert len(part)==6
    assert all(part[i].get_text()==full[i+18].get_text() for i in range(6))
for record in records:
    assert sha(ROOT/record['source'])==record['sourceSha256'],record['source']
    docx=OUT/record['docx'];pdf=OUT/record['pdf']
    assert sha(docx)==record['docxSha256'] and sha(pdf)==record['pdfSha256']
    doc=fitz.open(pdf)
    assert len(doc)==record['pages']
    assert all(norm(page.get_text()) for page in doc),'Empty page'
    assert len(list((ROOT/record['pngDirectory']).glob('page-*.png')))==len(doc)
    with ZipFile(docx) as z:
        xml=z.read('word/document.xml').decode('utf-8')
        assert '\ufffd' not in xml
        document=ET.fromstring(xml)
        text=''.join(document.itertext())
        if record['source'] in ['11_D部分口播与练习.md','01_自然口播稿.md']:
            pdf_text=''.join(page.get_text() for page in doc)
            for slide in data[18:]:
                assert norm(slide['script']) in norm(text),(record['source'],slide['n'],'docx')
                assert norm(slide['script']) in norm(pdf_text),(record['source'],slide['n'],'pdf')
        if record['source']=='10_D部分答辩备课.md':
            assert len(re.findall(r'^### \d+\.',(ROOT/record['source']).read_text(encoding='utf-8'),re.M))==14
        # Strong first answers must survive the printable conversion.
        if record['source'] in ['10_D部分答辩备课.md','04_来源与答辩.md']:
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            starts=['短答：','约30秒回答：']
            checked=0
            for run in document.findall('.//w:r',ns):
                run_text=''.join(run.itertext())
                if any(run_text.startswith(s) for s in starts):
                    assert run.find('w:rPr/w:b',ns) is not None,run_text
                    checked+=1
            assert checked>=14,checked
    doc.close()

historical={}
for name in ['智能体产业研发_V5_05.pptx','智能体产业研发_V5_05_主讲.pdf','智能体产业研发_V5_05_含答辩.pdf']:
    original=subprocess.check_output(['git','show',f'HEAD:v5/outputs/{name}'],cwd=REPO)
    assert (OUT/name).read_bytes()==original,name
    historical[name]=sha(OUT/name)
receipt={
 'status':'pass','revision':'V5-06','mainSlides':24,'totalSlides':34,
 'changedPackageParts':changed,'changedProjectionPages':pixel_changed,
 'unchangedPageCount':30,'mediaChartsAndWorkbooksByteIdentical':True,
 'DNotesAndTwoScriptsMatch':True,'ABCSourceUnchanged':True,
 'DDesignSeconds':190,'humanTimingVerified':False,'practiceRun':False,
 'nativeOpenAndPDFExport':True,'native06PlaybackRetested':False,
 'playbackBoundary':'Media and slide11 are byte-identical to previously playback-tested05;06 opened and rendered natively without a foreground slideshow.',
 'printedDocumentPages':{r['docx']:r['pages'] for r in records},
 'historical05Preserved':historical,'DOriginalSha256':sha(original_doc),'DOnlyPDFMatches':True,'finalPptxSha256':sha(NEW),
 'visualReviewIsSeparate':'See visual_review.md; this script does not infer visual acceptance.',
}
(QA/'verification.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=True))
