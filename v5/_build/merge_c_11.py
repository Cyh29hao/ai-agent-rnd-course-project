"""Merge editable C pages while preserving every unrelated slide and media byte."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy,json,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'_build/final_11'
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
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
urls={5:'https://developers.openai.com/blog/automating-repetitive-work-at-openai-with-codex',6:'https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/',7:'https://arxiv.org/html/2511.10395v1',8:'https://arxiv.org/html/2505.22954v1',11:'https://github.com/modelscope/AgentEvolver'}
with ZipFile(ROOT/'outputs/智能体产业研发_V5_10.pptx') as src,ZipFile(BUILD/'c_authored.pptx') as authored,ZipFile(BUILD/'merged.pptx','w',ZIP_DEFLATED) as dst:
 for item in src.infolist():
  content=src.read(item.filename)
  for n in range(14,20):
   if n<19 and item.filename==f'ppt/slides/slide{n}.xml':content=authored.read(f'ppt/slides/slide{n-13}.xml')
   if item.filename==f'ppt/notesSlides/notesSlide{n}.xml':
    s=data[n-1];links='\n'.join(f'[{k}] {urls[k]}' for k in s['sources'])
    content=note(content,f"主讲第{n}页，预算{s['seconds']}秒，未真人计时。\n{s['script']}\n{s.get('note','')}\n{links}")
  dst.writestr(copy.copy(item),content)
print('MERGED_C11_AND_SIX_NOTES')
