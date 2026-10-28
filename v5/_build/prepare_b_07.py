"""Promote the reviewed deck without redrawing or overwriting the candidate."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy
import json
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
build=ROOT/'_build/b_integration_07';build.mkdir(exist_ok=True)
(ROOT/'qa/b_integration_07').mkdir(exist_ok=True)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
candidate=ROOT/'outputs/智能体产业研发_V5_07_候选.pptx'
with ZipFile(candidate) as source,ZipFile(build/'ready.pptx','w',ZIP_DEFLATED) as target:
    for item in source.infolist():
        content=source.read(item.filename)
        if item.filename=='ppt/slides/slide11.xml':
            # PowerPoint's media action has an empty relationship id. Omit the
            # empty optional id; keep the media action and actual video links.
            root=E.fromstring(content)
            for node in root.iter():
                for key,value in list(node.attrib.items()):
                    if key.startswith('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}') and value=='':
                        del node.attrib[key]
            content=E.tostring(root,encoding='utf-8',xml_declaration=True)
        if item.filename=='ppt/notesSlides/notesSlide12.xml':
            root=E.fromstring(content)
            found=False
            for shape in root.findall('.//p:sp',ns):
                ph=shape.find('p:nvSpPr/p:nvPr/p:ph',ns)
                if ph is not None and ph.get('type')=='body':
                    body=shape.find('p:txBody',ns)
                    for paragraph in list(body.findall('a:p',ns)):body.remove(paragraph)
                    text=f"主讲第12页，设计预算40秒，未真人计时。\n{data[11]['script']}\n{data[11]['note']}\n来源：[4] https://alignment.anthropic.com/2026/automated-alignment-researchers/"
                    for line in text.splitlines():
                        paragraph=E.SubElement(body,'{'+ns['a']+'}p')
                        run=E.SubElement(paragraph,'{'+ns['a']+'}r')
                        E.SubElement(run,'{'+ns['a']+'}t').text=line
                    found=True
            assert found
            content=E.tostring(root,encoding='utf-8',xml_declaration=True)
        target.writestr(copy.copy(item),content)
print('READY_07_NOTES_12_ONLY')
