"""Verify the edited A set, preserved B-D, and synchronized deliverables."""
from pathlib import Path
from zipfile import ZipFile
import json,re,hashlib,subprocess
import xml.etree.ElementTree as E
import fitz
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent;OUT=ROOT/'outputs';QA=ROOT/'qa/a_refinement_08'
BASE='531fd170cffc1bf4a3bb3801c8423573a91d3425'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\W+','',s)
def old(p):return subprocess.check_output(['git','show',f'{BASE}:{p}'],cwd=REPO)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'));baseline=json.loads(old('v5/主讲内容.json').decode('utf-8'))
assert len(data)==24 and data[7:]==baseline[7:]
assert sum(s['seconds'] for s in data[:7])==205 and sum(s['seconds'] for s in data)==850
spoken=(ROOT/'01_自然口播稿.md').read_text(encoding='utf-8');practice=(ROOT/'17_A部分口播与练习.md').read_text(encoding='utf-8')
ppt=OUT/'智能体产业研发_V5_08.pptx'
permitted={f'ppt/slides/slide{n}.xml' for n in [2,3,4,5,6,25,26]}|{f'ppt/notesSlides/notesSlide{n}.xml' for n in [1,2,3,4,5,6,7,25,26]}
with ZipFile(OUT/'智能体产业研发_V5_07.pptx') as a,ZipFile(ppt) as b:
    assert a.namelist()==b.namelist()
    changed=[p for p in a.namelist() if a.read(p)!=b.read(p)]
    assert set(changed)==permitted,changed
    for s in data:
        text=''.join(E.fromstring(b.read(f'ppt/notesSlides/notesSlide{s["n"]}.xml')).itertext())
        assert norm(s['script']) in norm(text) and s['script'] in spoken,s['n']
        if s['n']<=7:assert s['script'] in practice,s['n']
    media=[p for p in b.namelist() if p.startswith(('ppt/media/','ppt/charts/','ppt/embeddings/'))]
    assert media and all(a.read(p)==b.read(p) for p in media)
changed_pixels=[]
for n in range(1,35):
    a=Image.open(ROOT/f'qa/b_integration_07/slides/{n:02}.png').convert('RGB')
    b=Image.open(QA/f'slides/{n:02}.png').convert('RGB')
    if ImageChops.difference(a,b).getbbox():changed_pixels.append(n)
assert changed_pixels==[2,3,4,5,6,25,26],changed_pixels
v=json.loads((QA/'validation.json').read_text(encoding='utf-8'));n=json.loads((QA/'native.json').read_text(encoding='utf-8'))
assert v['finalSha256']==n['finalPptxSha256']==n['candidateSha256']==sha(ppt)
assert v['packageIntegrity']['status']=='pass' and v['firstPartyImport']['passed'] and v['nativeQuantitativeCharts']['exitCode']==0
assert n['nativeOpen'] and n['slides']==34 and n['mediaMilliseconds']==[18000]
with fitz.open(OUT/'智能体产业研发_V5_08_含答辩.pdf') as full,fitz.open(OUT/'智能体产业研发_V5_08_主讲.pdf') as main,fitz.open(OUT/'A部分投影_V5_08.pdf') as part,fitz.open(OUT/'B部分投影_V5_07.pdf') as b,fitz.open(OUT/'D部分投影_V5_06.pdf') as d:
    assert [len(full),len(main),len(part)]==[34,24,7]
    assert all(full[i].get_text()==main[i].get_text() for i in range(24))
    assert all(full[i].get_text()==part[i].get_text() for i in range(7))
    assert all(full[i+7].get_text()==b[i].get_text() for i in range(6))
    assert all(full[i+18].get_text()==d[i].get_text() for i in range(6))
records=json.loads((QA/'documents_export.json').read_text(encoding='utf-8'))
for r in records:
    assert sha(ROOT/r['source'])==r['sourceSha256'],r['source']
    assert sha(OUT/r['docx'])==r['docxSha256'] and sha(OUT/r['pdf'])==r['pdfSha256']
    with fitz.open(OUT/r['pdf']) as pdf:
        assert len(pdf)==r['pages'] and all(norm(p.get_text()) for p in pdf)
        assert len(list((ROOT/r['pngDirectory']).glob('page-*.png')))==len(pdf)
        text=''.join(p.get_text() for p in pdf)
        if r['source'].startswith(('01_','17_')):
            for s in (data if r['source'].startswith('01_') else data[:7]):assert norm(s['script']) in norm(text),(r['source'],s['n'])
    with ZipFile(OUT/r['docx']) as z:
        text=z.read('word/document.xml').decode('utf-8');assert '\ufffd' not in text
        if r['source'].startswith('18_'):
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            answers=[r for r in E.fromstring(text).findall('.//w:r',ns) if ''.join(r.itertext()).startswith('短答：')]
            assert len(answers)==12 and all(r.find('w:rPr/w:b',ns) is not None for r in answers)
preserved=[]
raw=subprocess.check_output(['git','ls-tree','-rz',BASE,'v5/outputs'],cwd=REPO)
for item in raw.split(b'\0'):
    if not item:continue
    meta,name=item.split(b'\t',1);relative=name.decode('utf-8')
    if not any(label in relative for label in ['V5_06','V5_07','B07_18']):continue
    digest=meta.decode().split()[2]
    actual=subprocess.check_output(['git','hash-object',relative],cwd=REPO).decode().strip()
    assert actual==digest,relative
    preserved.append(relative)
original=REPO/'collaboration/proposals/D_曹天卓_20261025/D_19-24页_曹天卓_V5修订.docx'
assert sha(original)=='a47a1d4099d8f7e2b48686854f7802e7e4bfc47b90f46673f63b960313b22bf6'
result={'status':'pass','revision':'V5-08','changedSlideNumbers':changed_pixels,'other27PagesPixelIdenticalTo07':True,
        'BCDSourceUnchanged':True,'all24NotesAndScriptsMatch':True,'ASevenScriptsMatchPrint':True,
        'ASeconds':205,'totalContentSeconds':850,'humanTimingVerified':False,'nativeOpenAndPDFExport':True,
        'embeddedMediaSeconds':18,'foregroundPlaybackTested':False,'mediaChartWorkbookByteIdentical':True,
        'printedPages':{r['docx']:r['pages'] for r in records},'historicalArtifactsPreserved':len(preserved),
        'DOriginalPreserved':True,'finalPptxSha256':sha(ppt),'visualReview':'Separate visual_review.md; assertions do not infer appearance.'}
(QA/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=True))
