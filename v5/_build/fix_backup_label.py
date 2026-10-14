"""Sync one already-verified backup label; preserve every other PPTX part."""
from pathlib import Path
import zipfile,json
ROOT=Path(__file__).resolve().parents[1]
old='公开数据SFT与自由数据SFT限制训练方式'
new='原样公共数据SFT与自由构造数据SFT限制训练方式'
p=ROOT/'_build/build_deck.mjs';t=p.read_text(encoding='utf-8')
assert old in t;t=t.replace(old,new);p.write_text(t,encoding='utf-8')
src=ROOT/'outputs/智能体产业研发_V5_03.pptx';dst=ROOT/'_build/deck_backupfix.pptx';changed=[]
with zipfile.ZipFile(src) as zin,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if item.filename=='ppt/slides/slide29.xml':
            assert data.count(old.encode('utf-8'))==1
            data=data.replace(old.encode('utf-8'),new.encode('utf-8'));changed.append(item.filename)
        zout.writestr(item,data)
assert changed==['ppt/slides/slide29.xml']
(ROOT/'qa/backup_label_fix.json').write_text(json.dumps({'changedParts':changed,'otherPartBytesPreserved':True},indent=2),encoding='utf-8')
print('BACKUP_LABEL_SYNCED')
