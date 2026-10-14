"""Remove PowerPoint's empty relationship attribute on its intrinsic media action.

The ppaction://media hyperlink is an intrinsic action. It has no relationship
target. Actual video/image relationships remain byte-for-byte unchanged.
"""
from pathlib import Path
import zipfile,re,json
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
src=ROOT/'_build/deck_with_media.pptx';dst=ROOT/'_build/deck_normalized.pptx'
changed=[]
with zipfile.ZipFile(src) as zin,zipfile.ZipFile(dst,'w',zipfile.ZIP_DEFLATED) as zout:
    for item in zin.infolist():
        data=zin.read(item.filename)
        if item.filename=='ppt/slides/slide11.xml':
            old=data
            data=re.sub(rb'(<a:hlinkClick\b[^>]*?) r:id=""(?=[^>]*action="ppaction://media")',rb'\1',data)
            if data!=old:changed.append(item.filename)
        if item.filename=='ppt/charts/chart1.xml':
            # Native PowerPoint serializes binary floats with 17-digit noise.
            # The authoritative literal source remains .06, .029, .233.
            for native,original in [('2.9000000000000001E-2','0.029'),('0.23300000000000001','0.233')]:
                assert abs(Decimal(native)-Decimal(original))<Decimal('1e-15')
                assert data.count(native.encode())==1
                data=data.replace(native.encode(),original.encode())
            changed.append(item.filename)
        zout.writestr(item,data)
assert set(changed)=={'ppt/slides/slide11.xml','ppt/charts/chart1.xml'},changed
(ROOT/'qa/media_normalization.json').write_text(json.dumps({'changed':changed,'removed':'empty r:id on ppaction://media','chart':'Restore authoritative decimal literals from source .06/.029/.233 after native roundtrip noise','preserved':'video links, poster link, intrinsic action, all other parts'},indent=2),encoding='utf-8')
print('MEDIA_ACTION_NORMALIZED',changed)
