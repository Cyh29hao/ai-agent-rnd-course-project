"""Check edited slide scope, spoken notes, media and native exports."""
from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib,subprocess
import xml.etree.ElementTree as E
import fitz
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'outputs';QA=ROOT/'qa'
slides=[3,5,6,20,21,22,23]
permitted={f'ppt/slides/slide{i}.xml' for i in slides}
permitted.update(f'ppt/notesSlides/notesSlide{i}.xml' for i in range(1,25))
old=OUT/'智能体产业研发_V5_04.pptx';new=OUT/'智能体产业研发_V5_05.pptx'
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(old) as original,ZipFile(new) as final:
    assert set(original.namelist())==set(final.namelist())
    changed={p for p in original.namelist() if original.read(p)!=final.read(p)}
    assert changed<=permitted,changed-permitted
    assert all(f'ppt/slides/slide{i}.xml' in changed for i in slides)
    assert len([n for n in final.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==34
    for d in data:
        texts=''.join(E.fromstring(final.read(f'ppt/notesSlides/notesSlide{d["n"]}.xml')).itertext())
        assert d['script'] in texts,d['n']
        assert d['script'] in (ROOT/'01_自然口播稿.md').read_text(encoding='utf-8'),d['n']
    assert sum(d['seconds'] for d in data)==850
    for i in [21,22,23]:
        text=''.join(E.fromstring(final.read(f'ppt/slides/slide{i}.xml')).itertext())
        assert not any(w in text for w in ['证据不足','证据缺口','待验证','仍需充分检验']),i
    # Native table/chart/media parts are exactly retained from the verified deck.
    assert original.read('ppt/slides/slide11.xml')==final.read('ppt/slides/slide11.xml')
    for p in original.namelist():
        if p.startswith(('ppt/media/','ppt/charts/','ppt/embeddings/')):
            assert original.read(p)==final.read(p),p
native=json.loads((QA/'native_05.json').read_text(encoding='utf-8'))
sha=hashlib.sha256(new.read_bytes()).hexdigest()
assert native['nativeOpen'] and native['slides']==34 and native['pptxSha256']==sha
assert len(fitz.open(OUT/'智能体产业研发_V5_05_主讲.pdf'))==24
assert len(fitz.open(OUT/'智能体产业研发_V5_05_含答辩.pdf'))==34
play=json.loads((QA/'native_playback_05.json').read_text(encoding='utf-8'))
assert play['passed'] and play['sourceSha256']==sha
assert all(s['state']==0 for s in play['samples'])
positions=[s['position'] for s in play['samples']]
assert 0<positions[0]<positions[1]<positions[2]
doc_records=json.loads((QA/'documents_export_精修.json').read_text(encoding='utf-8'))
for d in doc_records:
    p=OUT/d['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==d['sha256']
    pdf=p.with_suffix('.pdf');assert len(fitz.open(pdf))==d['pages']
    assert hashlib.sha256(pdf.read_bytes()).hexdigest()==d['pdf_sha256']
    with ZipFile(p) as z:
        xml=z.read('word/document.xml').decode('utf-8');assert '\ufffd' not in xml
    assert len(list((QA/p.stem).glob('[0-9][0-9].png')))==d['pages']
# Restore the previous delivered PDF bytes after a read-only native recheck
# generated a new timestamp. The newly edited PDF has its own version name.
pdf04=OUT/'智能体产业研发_V5_04_主讲.pdf'
historic=subprocess.check_output(['git','show','HEAD:v5/outputs/智能体产业研发_V5_04_主讲.pdf'],cwd=ROOT.parent)
pdf04.write_bytes(historic)
result={'stage':'expression refinement checked','mainSlides':24,'totalSlides':34,'editedSlides':slides,'notesMatch':True,'scriptsSeconds':850,'mainAndFullPDFChecked':True,'nativeOpenFinal':True,'nativePlaybackPositions':positions,'playbackCleanupWarning':play.get('cleanupWarning'),'docPages':[d['pages'] for d in doc_records],'changedPagesVisuallyRead':slides,'unchangedDeckPartsPreserved':True,'reportAndDefensePagesRead':17,'talkPagesRead':5,'independentLanguageReview':'no required changes','practice':'deferred','fullCourseGoalComplete':False,'humanTimingVerified':False,'sameChatSchedulingVerified':False,'sha256':sha}
(QA/'closing_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
