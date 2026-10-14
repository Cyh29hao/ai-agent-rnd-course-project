from pathlib import Path
from zipfile import ZipFile
import json,re,xml.etree.ElementTree as ET,os
import fitz
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'样页口播.json').read_text(encoding='utf-8'))
src=ROOT/'outputs/审批样页_05.pptx'
with ZipFile(src) as z:
    slide_parts=[n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)]
    assert len(slide_parts)==8
    ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
    for i,row in enumerate(records,1):
        notes=ET.fromstring(z.read(f'ppt/notesSlides/notesSlide{i}.xml'))
        text=''.join(t.text or '' for t in notes.findall('.//a:t',ns))
        assert row['script'] in text,f'Notes mismatch {i}'
assert len(fitz.open(ROOT/'outputs/审批样页_05.pdf'))==8
decodes={}
for stem,seconds in [('mechanism',18),('trace',12)]:
    d=json.loads((ROOT/f'qa/decoded_{stem}/decode.json').read_text(encoding='utf-8-sig'))
    assert d['decoded'] and abs(d['duration']-seconds)<.15
    decodes[stem]={'seconds':d['duration'],'width':d['width'],'height':d['height']}
count=0
for dirpath,dirs,files in os.walk(ROOT):
    dirs[:]=[d for d in dirs if d!='node_modules']
    for name in files:
        p=Path(dirpath)/name
        if p.suffix in ['.md','.json','.html','.py','.mjs']:
            t=p.read_text(encoding='utf-8-sig');assert '\ufffd' not in t,p;count+=1
interactive=json.loads((ROOT/'qa/interactive_test.json').read_text(encoding='utf-8'))
assert interactive['loss_monotonically_decreased'] and interactive['play_pass'] and interactive['reset_pass']
result={'status':'ready_for_user_review','slides':8,'notes_match':True,'native_powerpoint_all_8_pages_read':True,'decoded':decodes,'interactive_math_and_controls_checked':True,'utf8_text_files_checked':count,'full_goal_complete':False,'user_approval_received':False,'human_comprehension_tested':False,'full_talk_timing_tested':False,'boundaries':['Authoring Node process printed valid receipts but exited 1; native PowerPoint open/export verified separately.','Only samples, plan and teaching prototypes were made.','Single parameter demo is not LLM training or AAR reproduction.']}
(ROOT/'qa/review_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=True))
