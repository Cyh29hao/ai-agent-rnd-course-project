# -*- coding: utf-8 -*-
from pathlib import Path
import json,hashlib,datetime
import fitz
from PIL import Image, ImageOps, ImageDraw

root=Path(__file__).resolve().parents[1]
pdf=root/'03_完整备份版.pdf'
out=root/'qa'/'slides'
out.mkdir(parents=True,exist_ok=True)
doc=fitz.open(pdf)
thumbs=[]
for i,page in enumerate(doc):
    pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
    im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    im.save(out/f'{i+1:02d}.png')
    tile=im.copy();tile.thumbnail((640,360))
    canvas=Image.new('RGB',(650,390),'#e6e8e6');canvas.paste(tile,((650-tile.width)//2,6))
    ImageDraw.Draw(canvas).text((12,366),f'{i+1:02d}',fill='#26323a')
    thumbs.append(canvas)
for name,subset in [('main',thumbs[:14]),('backup',thumbs[14:])]:
    cols=3;rows=(len(subset)+cols-1)//cols
    sheet=Image.new('RGB',(cols*650,rows*390),'#d9dddd')
    for j,tile in enumerate(subset):sheet.paste(tile,((j%cols)*650,(j//cols)*390))
    sheet.save(root/'qa'/f'contact_{name}.png')
main=root/'02_主讲版.pdf'
short=fitz.open(pdf)
short.select(list(range(14)))
short.save(main)
manifest={'rendered_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'source_pdf_sha256':hashlib.sha256(pdf.read_bytes()).hexdigest(),
          'main_pdf_sha256':hashlib.sha256(main.read_bytes()).hexdigest(),
          'rendered_pages':len(thumbs),
          'png_sha256':{f'{i+1:02d}.png':hashlib.sha256((out/f'{i+1:02d}.png').read_bytes()).hexdigest() for i in range(len(thumbs))}}
(root/'qa'/'render_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'pages={len(doc)} rendered={len(thumbs)} main_pdf={main}')
