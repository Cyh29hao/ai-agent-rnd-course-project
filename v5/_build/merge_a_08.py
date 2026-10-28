"""Replace five A pages and two reference pages; preserve all other package parts."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy,json,hashlib,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
build=ROOT/'_build/a_refinement_08';qa=ROOT/'qa/a_refinement_08';qa.mkdir(exist_ok=True)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
mapping={2:1,3:2,4:3,5:4,6:5,25:6,26:7}
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def notes(content,text):
    root=E.fromstring(content)
    for shape in root.findall('.//p:sp',ns):
        ph=shape.find('p:nvSpPr/p:nvPr/p:ph',ns)
        if ph is not None and ph.get('type')=='body':
            body=shape.find('p:txBody',ns)
            for par in list(body.findall('a:p',ns)):body.remove(par)
            for line in text.splitlines():
                par=E.SubElement(body,'{'+ns['a']+'}p');run=E.SubElement(par,'{'+ns['a']+'}r');E.SubElement(run,'{'+ns['a']+'}t').text=line
            return E.tostring(root,encoding='utf-8',xml_declaration=True)
    raise RuntimeError('No notes body')
changed=[]
with ZipFile(ROOT/'outputs/智能体产业研发_V5_07.pptx') as src,ZipFile(build/'a_authored.pptx') as draft,ZipFile(build/'a_merged.pptx','w',ZIP_DEFLATED) as dst:
    for item in src.infolist():
        content=src.read(item.filename)
        for n,index in mapping.items():
            if item.filename==f'ppt/slides/slide{n}.xml':
                content=draft.read(f'ppt/slides/slide{index}.xml');assert b'r:embed=' not in content and b'r:link=' not in content;changed.append(item.filename)
        for n in range(1,8):
            if item.filename==f'ppt/notesSlides/notesSlide{n}.xml':
                s=data[n-1]
                content=notes(content,f"主讲第{n}页，设计预算{s['seconds']}秒，未真人计时。\n{s['script']}\n{s['note']}\n原文：[10] https://www.anthropic.com/institute/recursive-self-improvement；[12] https://github.com/karpathy/autoresearch；[13] https://arxiv.org/html/2609.26457v1；[14] https://arxiv.org/abs/2408.06292；[15] https://arxiv.org/abs/2609.15802\n机制解释和追问见18_A部分答辩备课.md。")
                changed.append(item.filename)
        if item.filename in ['ppt/notesSlides/notesSlide25.xml','ppt/notesSlides/notesSlide26.xml']:
            content=notes(content,'新增[12]Karpathy autoresearch，2026年3月；[13]Srikanth等AIDE²，2026-09-22；[14]Lu等The AI Scientist，2024-08-12；[15]Cunningham等The Economics of RSI，2026-09-14。原[1]—[11]保留。完整书目信息和链接见04_来源与答辩.md。');changed.append(item.filename)
        dst.writestr(copy.copy(item),content)
with ZipFile(ROOT/'outputs/智能体产业研发_V5_07.pptx') as a,ZipFile(build/'a_merged.pptx') as b:
    assert a.namelist()==b.namelist()
    assert all(a.read(p)==b.read(p) for p in a.namelist() if p not in changed)
receipt={'changedParts':changed,'allOtherPackagePartsByteIdentical':True,'BMediaChartWorkbookPreserved':True,'changedSlideNumbers':list(mapping),'ASeconds':205,'totalSlides':34}
(qa/'merge.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
