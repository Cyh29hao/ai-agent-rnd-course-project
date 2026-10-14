from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'_build/build_deck.mjs';text=p.read_text(encoding='utf-8')
old="categories:['公开数据 SFT','自由数据 SFT','不受限研究方法']"
new="categories:['原样公共数据 SFT','自由构造数据 SFT','不受限研究方法']"
assert old in text or new in text
p.write_text(text.replace(old,new),encoding='utf-8')
for name in ['05_课程报告.md','04_来源与答辩.md']:
    p=ROOT/name;text=p.read_text(encoding='utf-8')
    p.write_text(text.replace('禁止向研究Agent或更强模型蒸馏','禁止从研究Agent或更强模型蒸馏'),encoding='utf-8')
print('CANONICALIZED')
