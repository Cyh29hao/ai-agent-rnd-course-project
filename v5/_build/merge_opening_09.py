from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'_build/opening_09';QA=ROOT/'qa/opening_09'
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
def header(root):
    candidates=[]
    for sp in root.findall('.//p:sp',ns):
        off=sp.find('p:spPr/a:xfrm/a:off',ns);body=sp.find('p:txBody',ns)
        if off is not None and body is not None and int(off.get('y'))<650000 and int(off.get('x'))<1200000:
            if ''.join(body.itertext()).strip():candidates.append(sp)
    assert len(candidates)==1,len(candidates)
    return candidates[0]
def note(content,text):
    root=E.fromstring(content)
    for sp in root.findall('.//p:sp',ns):
        ph=sp.find('p:nvSpPr/p:nvPr/p:ph',ns)
        if ph is not None and ph.get('type')=='body':
            body=sp.find('p:txBody',ns)
            for par in list(body.findall('a:p',ns)):body.remove(par)
            for line in text.splitlines():
                par=E.SubElement(body,'{'+ns['a']+'}p');run=E.SubElement(par,'{'+ns['a']+'}r');E.SubElement(run,'{'+ns['a']+'}t').text=line
            return E.tostring(root,encoding='utf-8',xml_declaration=True)
    raise RuntimeError('No note body')
with ZipFile(ROOT/'outputs/智能体产业研发_V5_08.pptx') as src,ZipFile(BUILD/'opening_authored.pptx') as authored,ZipFile(BUILD/'merged.pptx','w',ZIP_DEFLATED) as dst:
    for item in src.infolist():
        content=src.read(item.filename)
        for n in range(1,25):
            if item.filename==f'ppt/slides/slide{n}.xml':
                if n<=3:content=authored.read(f'ppt/slides/slide{n}.xml')
                if n>=2:
                    root=E.fromstring(content);texts=header(root).findall('.//a:t',ns)
                    texts[0].text=data[n-1]['section']
                    for t in texts[1:]:t.text=''
                    content=E.tostring(root,encoding='utf-8',xml_declaration=True)
            if n<=7 and item.filename==f'ppt/notesSlides/notesSlide{n}.xml':
                s=data[n-1];content=note(content,f"主讲第{n}页，预算{s['seconds']}秒，未真人计时。\n{s['script']}\n{s.get('note','')}\n来源[4][10][12]—[15]，具体链接见04_来源与答辩.md；深入解释见18_A部分答辩备课.md。")
        dst.writestr(copy.copy(item),content)
print('MERGED09_OPENING_AND_23_NAVIGATION_HEADERS')
