from pathlib import Path
from zipfile import ZipFile
import re,json,hashlib,shutil,os
import xml.etree.ElementTree as E
import fitz
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'outputs';qa=ROOT/'qa';records=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
src=out/'智能体产业研发_V5_04.pptx';old=out/'智能体产业研发_V5_03.pptx'
if not old.exists():old=qa/'history/智能体产业研发_V5_03.pptx'
ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(src) as z,ZipFile(old) as before:
    names=z.namelist();assert len([n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)])==34
    changed=[n for n in before.namelist() if before.read(n)!=z.read(n)]
    assert changed==['ppt/slides/slide29.xml']
    for d in records:
        notes=''.join(E.fromstring(z.read(f'ppt/notesSlides/notesSlide{d["n"]}.xml')).itertext())
        assert d['script'] in notes,d['n']
    text29=''.join(E.fromstring(z.read('ppt/slides/slide29.xml')).itertext())
    assert '原样公共数据SFT与自由构造数据SFT' in text29
    media=[n for n in names if n.endswith('.mp4')];assert len(media)==1
    assert hashlib.sha256(z.read(media[0])).hexdigest()==hashlib.sha256((out/'蒸馏机制_18秒.mp4').read_bytes()).hexdigest()
    for name in names:
        if name.endswith('.xml'):
            assert '\ufffd' not in z.read(name).decode('utf-8-sig')
    assert b'0.233' in z.read('ppt/charts/chart1.xml')
pdf03=out/'智能体产业研发_V5_03_主讲.pdf'
if not pdf03.exists():pdf03=qa/'history/智能体产业研发_V5_03_主讲.pdf'
assert len(fitz.open(pdf03))==24
shutil.copy2(pdf03,out/'智能体产业研发_V5_04_主讲.pdf')
for stem,n in [('四人口播_V5',6),('课程报告_V5',7),('来源与答辩_V5',10)]:
    assert len(fitz.open(out/(stem+'.pdf')))==n
    with ZipFile(out/(stem+'.docx')) as z:
        assert '\ufffd' not in z.read('word/document.xml').decode('utf-8')
        E.fromstring(z.read('word/document.xml'))
play=json.loads((qa/'native_playback.json').read_text(encoding='utf-8'))
assert play['passed'] and len(play['samples'])==3
count=0
for base,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d!='node_modules']
    for name in files:
        p=Path(base)/name
        if p.suffix in ['.md','.mjs','.py','.json']:
            assert '\ufffd' not in p.read_text(encoding='utf-8-sig'),p;count+=1
result={'stage':'industry presentation saved; overall incomplete','latestPPTX':src.name,'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'slides':34,'mainSlides':24,'notesMatch':True,'changeFromNativeReviewed03':changed,'nativeReviewed03All34':True,'native04ReopenPassed':False,'embeddedVideoHashMatches':True,'actualPlaybackSamples03':play['samples'],'playbackProcessCleanupError':play.get('error'),'documentsPages':[6,7,10],'utf8FilesChecked':count,'practice':'deferred','humanTimingPassed':False,'humanComprehensionPassed':False,'sameChatSchedulingPassed':False}
(qa/'closeout_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
# Keep old exports in the private history folder rather than the user entry.
history=qa/'history';history.mkdir(exist_ok=True)
for p in list(out.glob('智能体产业研发_V5_0[1-3]*')):
    dst=history/p.name
    assert p.resolve().parent==out.resolve() and dst.resolve().parent==history.resolve()
    if not dst.exists():shutil.move(str(p),str(dst))
print(json.dumps(result,ensure_ascii=True))
