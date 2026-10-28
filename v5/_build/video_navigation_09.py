"""Reuse B's native teaching frames; refresh only their baked-in part heading."""
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import copy,time,json,posixpath,hashlib
import xml.etree.ElementTree as E
import pythoncom,win32com.client
import build_b_07 as mature
ROOT=Path(__file__).resolve().parents[1];BUILD=ROOT/'_build/opening_09';QA=ROOT/'qa/opening_09'
video=ROOT/'outputs/蒸馏机制_B09_18秒.mp4'
assert not video.exists(),'Preserve already-created draft'
old_textbox=mature.textbox
def textbox(slide,text,*args,**kwargs):
    if text=='二  模型改进  Anthropic':text='二  Anthropic：模型训练'
    return old_textbox(slide,text,*args,**kwargs)
mature.textbox=textbox
src=BUILD/'merged.pptx'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
with ZipFile(src) as z:
    slide=E.fromstring(z.read('ppt/slides/slide11.xml'))
    pic=next(p for p in slide.findall('.//p:pic',ns) if p.find('p:nvPicPr/p:cNvPr',ns).get('name')=='MechanismTeachingVideo_B07')
    rid=pic.find('p:blipFill/a:blip',ns).get('{'+ns['r']+'}embed')
    rels=E.fromstring(z.read('ppt/slides/_rels/slide11.xml.rels'))
    target=next(r.get('Target') for r in rels if r.get('Id')==rid)
    poster_part=posixpath.normpath(posixpath.join('ppt/slides',target))
    media=[p for p in z.namelist() if p.startswith('ppt/media/') and p.endswith('.mp4')]
    assert len(media)==1
poster=BUILD/('video_poster'+Path(poster_part).suffix)
pythoncom.CoInitialize();app=pres=None
try:
    app=win32com.client.DispatchEx('PowerPoint.Application');pres=app.Presentations.Add(WithWindow=0)
    pres.PageSetup.SlideWidth=mature.SLIDE_W;pres.PageSetup.SlideHeight=mature.SLIDE_H
    for stage in range(3):mature.draw_11(pres.Slides.Add(stage+1,12),stage=stage,frame=True)
    pres.Slides(1).Export(str(poster),'PNG' if poster.suffix.lower()=='.png' else 'JPG',1280,720)
    pres.SaveAs(str(BUILD/'video_frames_09.pptx'),24)
    pres.CreateVideo(str(video),False,6,720,25,85)
    started=time.monotonic()
    while time.monotonic()-started<300:
        status=pres.CreateVideoStatus
        if status==3 and video.exists() and video.stat().st_size>10000:break
        if status==4:raise RuntimeError('Native video encoding failed')
        time.sleep(1)
    else:raise TimeoutError('Native video encoding timeout')
    pres.Close();pres=None
finally:
    if pres is not None:pres.Close()
    if app is not None and app.Presentations.Count==0:app.Quit()
    pythoncom.CoUninitialize()
tmp=BUILD/'with_video_navigation.pptx'
with ZipFile(src) as source,ZipFile(tmp,'w',ZIP_DEFLATED) as dest:
    for item in source.infolist():
        content=video.read_bytes() if item.filename==media[0] else poster.read_bytes() if item.filename==poster_part else source.read(item.filename)
        dest.writestr(copy.copy(item),content)
tmp.replace(src)
final=ROOT/'outputs/智能体产业研发_V5_09.pptx'
if final.exists():final.replace(BUILD/'unpublished_before_video_navigation.pptx')
(QA/'video_navigation.json').write_text(json.dumps({'changedPackageParts':[media[0],poster_part],'change':'Only the part heading in the three existing native teaching frames; sequence, six seconds per stage and mechanisms retained','video':video.name,'videoSha256':hashlib.sha256(video.read_bytes()).hexdigest(),'designSeconds':18},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('NATIVE_VIDEO_AND_POSTER_NAVIGATION_UPDATED')
