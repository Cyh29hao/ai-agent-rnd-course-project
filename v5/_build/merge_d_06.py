"""Preserve the released package; replace four slide XMLs and D-only notes."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy,json,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'outputs/智能体产业研发_V5_05.pptx'
authored=ROOT/'_build/d_refinement_06/d_authored.pptx'
destination=ROOT/'_build/d_refinement_06/d_merged.pptx'
mapping={19:1,21:2,22:3,23:4}
slides=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def update_note(data,text):
    root=ET.fromstring(data)
    for shape in root.findall('.//p:sp',ns):
        marker=shape.find('p:nvSpPr/p:nvPr/p:ph',ns)
        if marker is not None and marker.get('type')=='body':
            body=shape.find('p:txBody',ns)
            for paragraph in list(body.findall('a:p',ns)):body.remove(paragraph)
            for line in text.split('\n'):
                paragraph=ET.SubElement(body,'{'+ns['a']+'}p');run=ET.SubElement(paragraph,'{'+ns['a']+'}r');ET.SubElement(run,'{'+ns['a']+'}t').text=line
            return ET.tostring(root,encoding='utf-8',xml_declaration=True)
    raise RuntimeError('No note body')
changed=[]
with ZipFile(source) as original,ZipFile(authored) as draft,ZipFile(destination,'w',ZIP_DEFLATED) as output:
    for item in original.infolist():
        content=original.read(item.filename)
        for target,index in mapping.items():
            if item.filename==f'ppt/slides/slide{target}.xml':
                content=draft.read(f'ppt/slides/slide{index}.xml')
                assert b'r:embed=' not in content and b'r:link=' not in content
                changed.append(item.filename)
        for number in range(19,25):
            if item.filename==f'ppt/notesSlides/notesSlide{number}.xml':
                slide=slides[number-1]
                text=f"主讲第{number}页，设计预算{slide['seconds']}秒，未真人计时。\n{slide['script']}\n{slide.get('note','')}\n来源：[7] https://arxiv.org/html/2511.10395v1；[8] https://sakana.ai/dgm/；[10] https://www.anthropic.com/institute/recursive-self-improvement\n深入问答与具体分母见10_D部分答辩备课.md。"
                content=update_note(content,text);changed.append(item.filename)
        if item.filename=='ppt/notesSlides/notesSlide33.xml':
            content=update_note(content,'开放框架、策略训练与代码自改要分别追踪。AgentEvolver训练更新策略参数；DGM此实验固定底层模型，修改代码和工具。DGM官方20%→50%对应论文SWE-bench 200题子集；Polyglot 14.2%→30.7%为完整复评，勿混50题搜索子集或pass@2榜单。见DGM v1 §4.2与组长D答辩备课。\nhttps://arxiv.org/html/2505.22954v1\nhttps://arxiv.org/html/2511.10395v1\nhttps://sakana.ai/dgm/')
            changed.append(item.filename)
        output.writestr(copy.copy(item),content)
with ZipFile(source) as original,ZipFile(destination) as result:
    assert original.namelist()==result.namelist()
    assert all(original.read(name)==result.read(name) for name in original.namelist() if name not in changed)
qa=ROOT/'qa/d_refinement_06';qa.mkdir(exist_ok=True)
receipt={'sourceSHA256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidateSHA256':hashlib.sha256(destination.read_bytes()).hexdigest(),'changedParts':changed,'unchangedPartsByteIdentical':True,'mediaAndWorkbooksPreserved':True,'mainSlides':24,'totalSlides':34}
(qa/'merge.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=True))
