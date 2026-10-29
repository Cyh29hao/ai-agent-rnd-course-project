"""Check the two-input reading plan without third-party dependencies."""
from pathlib import Path
from urllib.parse import unquote,urlsplit
import hashlib,json,re,sys

ROOT=Path(__file__).resolve().parents[1]

def check():
    errors=[]
    manifest=json.loads((ROOT/'docs/当前版本.json').read_text(encoding='utf-8'))
    plan=manifest['readingPlan'];readme=(ROOT/'README.md').read_text(encoding='utf-8')
    kits=[]
    def path_for(name):
        path=(ROOT/name).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            errors.append(f'Missing or outside repository: {name}')
        return path
    def local_links(path,text,images=True):
        pattern=r'!?\[[^\]\n]*\]\(([^)\n]+)\)' if images else r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)'
        found=[]
        for raw in re.findall(pattern,text):
            target=urlsplit(raw.strip().strip('<>'))
            if target.scheme or not target.path:continue
            linked=(path.parent/unquote(target.path)).resolve()
            if not linked.is_relative_to(ROOT) or not linked.is_file():errors.append(f'Broken link in {path.name}: {raw}')
            found.append(linked)
        return set(found)
    if set(plan['reports'])!=set('ABCD'):errors.append('Report owners differ from A/B/C/D')
    for part,entry in plan['reports'].items():
        materials=entry['materials']
        if len(materials)!=2 or len({m['path'] for m in materials})!=2:
            errors.append(f'{part}: expected two distinct report inputs');continue
        paths=[path_for(m['path']) for m in materials]
        if paths[0].suffix!='.md' or paths[1].suffix!='.pdf':errors.append(f'{part}: expected self-contained Markdown and projection PDF')
        if not all(m['path'] in readme for m in materials):errors.append(f'{part}: README omits an input')
        text=paths[0].read_text(encoding='utf-8');kits.append(paths[0])
        for marker in [entry['owner'],'## 交给AI的参考提示词','## 本人最后确认','## 参考来源','```text']:
            if marker not in text:errors.append(f'{part}: missing {marker}')
        if text.count('```')!=2:errors.append(f'{part}: unbalanced prompt code block')
        if '\ufffd' in text:errors.append(f'{part}: replacement character')
        local_links(paths[0],text)
        if local_links(paths[0],text,False)!={paths[1]}:
            errors.append(f'{part}: needs another local document beyond its paired PDF')
        body,refs=text.split('## 参考来源',1)
        declared={int(n) for n in re.findall(r'^\*\*\[(\d+)\]',refs,re.M)}
        if not {int(n) for n in re.findall(r'\[(\d+)\]',body)}.issubset(declared):errors.append(f'{part}: reference missing')
    extra=plan['leaderDefense']['extraMaterials']
    if len(extra)!=2 or len({m['path'] for m in extra})!=2:errors.append('Leader: expected two distinct extra inputs')
    for item in extra:
        path_for(item['path'])
        if item['path'] not in readme:errors.append('Leader: README omits an input')
    handbook=path_for(extra[1]['path']);text=handbook.read_text(encoding='utf-8')
    local_links(handbook,text)
    slides=json.loads((ROOT/'v5/主讲内容.json').read_text(encoding='utf-8'))
    for slide in slides:
        if slide['script'] not in text:errors.append(f'Handbook: missing exact spoken script {slide["n"]}')
    if len(re.findall(r'^### \d+\. ',text,re.M))!=18:errors.append('Handbook: expected 18 question groups')
    for name in [ROOT/'README.md',ROOT/'docs/个人报告准备与提示词.md',ROOT/'docs/组长准备总览.md']:
        local_links(name,name.read_text(encoding='utf-8'))
    for artifact in manifest['artifacts'].values():
        path=path_for(artifact['path'])
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']:errors.append(f'Stale hash: {artifact["path"]}')
    return {'passed':not errors,'reportInputs':{part:len(p['materials']) for part,p in plan['reports'].items()},'extraDefenseInputs':len(extra),'spokenPages':len(slides),'questionGroups':18,'artifactsChecked':len(manifest['artifacts']),'errors':errors}

if __name__=='__main__':
    result=check();print(json.dumps(result,ensure_ascii=True,indent=2));sys.exit(0 if result['passed'] else 1)
