"""Check the official B integration against the preserved 06 and submitted 07."""
from pathlib import Path
from zipfile import ZipFile
from io import BytesIO
import hashlib,json,re,subprocess
import xml.etree.ElementTree as E
import fitz
from PIL import Image,ImageChops
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parent
OUT=ROOT/'outputs'
QA=ROOT/'qa/b_integration_07'
BASE='fe0a327d71fb71e7adb4d41d08b766e9455bbe56'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return re.sub(r'\W+','',s)
def old(path):return subprocess.check_output(['git','show',f'{BASE}:{path}'],cwd=REPO)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
baseline=json.loads(old('v5/主讲内容.json').decode('utf-8'))
assert data[:7]==baseline[:7] and data[13:]==baseline[13:]
assert len(data)==24 and sum(x['seconds'] for x in data)==850
assert sum(x['seconds'] for x in data[7:13])==260
spoken=(ROOT/'01_自然口播稿.md').read_text(encoding='utf-8')
practice=(ROOT/'14_B部分口播与练习.md').read_text(encoding='utf-8')
ppt=OUT/'智能体产业研发_V5_07.pptx'
with ZipFile(OUT/'智能体产业研发_V5_07_候选.pptx') as candidate,ZipFile(ppt) as z:
    assert z.namelist()==candidate.namelist()
    changed=[p for p in z.namelist() if z.read(p)!=candidate.read(p)]
    assert set(changed)=={'ppt/slides/slide11.xml','ppt/notesSlides/notesSlide12.xml'},changed
    assert len([p for p in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',p)])==34
    for slide in data:
        text=''.join(E.fromstring(z.read(f'ppt/notesSlides/notesSlide{slide["n"]}.xml')).itertext())
        assert norm(slide['script']) in norm(text),slide['n']
        assert slide['script'] in spoken
        if 8<=slide['n']<=13:assert slide['script'] in practice
    chart=''.join(E.fromstring(z.read('ppt/charts/chart1.xml')).itertext())
    workbook=[p for p in z.namelist() if p.startswith('ppt/embeddings/') and p.endswith('.xlsx')]
    assert len(workbook)==1
    with ZipFile(BytesIO(z.read(workbook[0]))) as wb:
        cells=''.join(''.join(E.fromstring(wb.read(p)).itertext()) for p in wb.namelist() if p.startswith('xl/worksheets/') and p.endswith('.xml'))
    for value in ['0.06','0.029','0.165','0.233']:assert value in chart and value in cells
    media=[p for p in z.namelist() if p.startswith('ppt/media/') and p.endswith('.mp4')]
    assert len(media)==1 and z.read(media[0])==(OUT/'蒸馏机制_B07_18秒.mp4').read_bytes()
    for n in range(1,35):
        for node in E.fromstring(z.read(f'ppt/slides/slide{n}.xml')).iter():
            assert not any(k.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}') and v=='' for k,v in node.attrib.items())
changed_pixels=[]
for n in range(1,35):
    a=Image.open(ROOT/f'qa/powerpoint_06/{n:02}.png').convert('RGB')
    b=Image.open(QA/f'slides/{n:02}.png').convert('RGB')
    if ImageChops.difference(a,b).getbbox():changed_pixels.append(n)
assert changed_pixels==[8,9,10,11,12,13,29],changed_pixels
for n in range(8,14):
    a=Image.open(ROOT/f'qa/b_refinement_07/slides/{n:02}.png').convert('RGB')
    b=Image.open(QA/f'slides/{n:02}.png').convert('RGB')
    assert not ImageChops.difference(a,b).getbbox(),n
validation=json.loads((QA/'validation.json').read_text(encoding='utf-8'))
assert validation['finalSha256']==sha(ppt)
assert validation['packageIntegrity']['status']=='pass' and validation['firstPartyImport']['passed']
assert validation['nativeQuantitativeCharts']['exitCode']==0
native=json.loads((QA/'native.json').read_text(encoding='utf-8'))
assert native['nativeOpen'] and native['slides']==34 and native['mediaMilliseconds']==[18000]
assert native['pptxSha256']==sha(ppt)
with fitz.open(OUT/'智能体产业研发_V5_07_主讲.pdf') as main,fitz.open(OUT/'智能体产业研发_V5_07_含答辩.pdf') as full,fitz.open(OUT/'B部分投影_V5_07.pdf') as part:
    assert [len(main),len(full),len(part)]==[24,34,6]
    assert all(main[i].get_text()==full[i].get_text() for i in range(24))
    assert all(part[i].get_text()==full[i+7].get_text() for i in range(6))
records=json.loads((QA/'documents_export.json').read_text(encoding='utf-8'))
for r in records:
    assert sha(ROOT/r['source'])==r['sourceSha256'],r['source']
    assert sha(OUT/r['docx'])==r['docxSha256'] and sha(OUT/r['pdf'])==r['pdfSha256']
    with fitz.open(OUT/r['pdf']) as pdf:
        assert len(pdf)==r['pages'] and all(norm(p.get_text()) for p in pdf)
        assert len(list((ROOT/r['pngDirectory']).glob('page-*.png')))==len(pdf)
        text=''.join(p.get_text() for p in pdf)
        if r['source'] in ['01_自然口播稿.md','14_B部分口播与练习.md']:
            for slide in (data if r['source'].startswith('01_') else data[7:13]):assert norm(slide['script']) in norm(text),(r['source'],slide['n'])
    with ZipFile(OUT/r['docx']) as z:
        xml=z.read('word/document.xml').decode('utf-8');assert '\ufffd' not in xml
        if r['source'].startswith('15_'):
            ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
            answers=[run for run in E.fromstring(xml).findall('.//w:r',ns) if ''.join(run.itertext()).startswith('短答：')]
            assert len(answers)==10 and all(run.find('w:rPr/w:b',ns) is not None for run in answers)
preserved=[]
for p in OUT.glob('*_V5_06*'):
    relative=p.relative_to(REPO).as_posix()
    assert p.read_bytes()==old(relative),relative
    preserved.append(relative)
assert preserved
original=REPO/'collaboration/proposals/D_曹天卓_20261025/D_19-24页_曹天卓_V5修订.docx'
assert sha(original)=='a47a1d4099d8f7e2b48686854f7802e7e4bfc47b90f46673f63b960313b22bf6'
result={'status':'pass','revision':'V5-07','changedPackagePartsFromCandidate':changed,
        'changedProjectionPagesFrom06':changed_pixels,'other27PagesPixelIdenticalTo06':True,
        'BProjectionPixelIdenticalToCandidate':True,'all24NotesAndSpokenScriptsMatch':True,
        'ACDSourceUnchanged':True,'BDesignSeconds':260,'humanTimingVerified':False,
        'nativeOpenAndPDFExport':True,'embeddedMediaSeconds':18,'foregroundPlaybackTested':False,
        'printedPages':{r['docx']:r['pages'] for r in records},'preserved06Artifacts':preserved,
        'originalDWordPreserved':True,'finalPptxSha256':sha(ppt),
        'visualReview':'Separate human-readable visual_review.md; assertions do not infer visual quality.'}
(QA/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(result,ensure_ascii=True))
