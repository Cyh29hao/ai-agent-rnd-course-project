"""Read-only checks for collaboration entry points; standard-library Python 3."""
from pathlib import Path
import hashlib
import json
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs' / '\u5f53\u524d\u7248\u672c.json'

def check(root=ROOT):
    errors = []
    manifest = json.loads((root / MANIFEST.relative_to(ROOT)).read_text(encoding='utf-8'))
    def path_at(name):
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()):
            errors.append(f'Outside repository: {name}')
            return None
        if not path.is_file():
            errors.append(f'Missing file: {name}')
            return None
        return path
    path_at(manifest['entry'])
    for artifact in manifest['artifacts'].values():
        path = path_at(artifact['path'])
        if path and artifact.get('sha256'):
            if hashlib.sha256(path.read_bytes()).hexdigest() != artifact['sha256']:
                errors.append(f'Artifact hash differs: {artifact["path"]}')
    for group in ['sources', 'collaboration']:
        for name in manifest[group].values():
            path_at(name)
    docs = [root / 'README.md', root / 'AGENTS.md', root / 'collaboration/README.md']
    docs += [root / name for name in manifest['collaboration'].values()]
    docs += [root / 'docs' / '\u9879\u76ee\u72b6\u6001.md', root / manifest['entry']]
    docs += list((root / 'collaboration/proposals').rglob('*.md'))
    for path in docs:
        try:
            text = path.read_text(encoding='utf-8')
        except (UnicodeError, OSError) as exc:
            errors.append(f'Cannot read UTF-8 file {path.name}: {exc}')
            continue
        if '\ufffd' in text:
            errors.append(f'Replacement character: {path.name}')
        # Fenced examples and code spans are not navigation links.
        body = re.sub(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1[^\n]*$', '', text, flags=re.M | re.S)
        body = re.sub(r'`[^`\n]+`', '', body)
        for target in re.findall(r'!?\[[^\]\n]*\]\(([^)\n]+)\)', body):
            target = target.strip().strip('<>')
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith(('#', '//')):
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if not destination.is_relative_to(root.resolve()) or not destination.exists():
                errors.append(f'Broken local link in {path.relative_to(root)}: {target}')
    slides = json.loads((root / manifest['sources']['slideContent']).read_text(encoding='utf-8'))
    if len(slides) != manifest['mainSlides']:
        errors.append('Main slide count differs from source')
    if sum(slide['seconds'] for slide in slides) > manifest['designSeconds']:
        errors.append('Source budget exceeds total design budget')
    return {'scope': 'Local links, UTF-8, release paths/hash, source count/budget only; not academic or human validation',
            'release': manifest['release'], 'documents': len(docs), 'passed': not errors, 'errors': errors}

if __name__ == '__main__':
    result = check()
    print(json.dumps(result, ensure_ascii=True, indent=2))
    sys.exit(0 if result['passed'] else 1)
