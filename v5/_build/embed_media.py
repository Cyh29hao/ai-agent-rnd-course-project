"""Create a teaching video and embed it in the task-owned PowerPoint draft."""
from pathlib import Path
import time,json,hashlib
import pythoncom,win32com.client
ROOT=Path(__file__).resolve().parents[1]
pythoncom.CoInitialize();app=None;pres=None
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    video=ROOT/'outputs/蒸馏机制_18秒.mp4'
    pres=app.Presentations.Open(str(ROOT/'_build/mechanism_frames.pptx'),ReadOnly=-1,Untitled=0,WithWindow=0)
    pres.CreateVideo(str(video),False,6,720,25,85)
    start=time.monotonic()
    while time.monotonic()-start<240:
        state=pres.CreateVideoStatus
        if state==3 and video.exists() and video.stat().st_size>10000:break
        if state==4:raise RuntimeError('Video creation failed')
        time.sleep(1)
    else:raise TimeoutError('Video creation timeout')
    pres.Close();pres=None
    pres=app.Presentations.Open(str(ROOT/'_build/deck_draft.pptx'),ReadOnly=0,Untitled=0,WithWindow=0)
    slide=pres.Slides(11)
    # 16:9 full-canvas video uses the same title/diagram as its static fallback.
    media=slide.Shapes.AddMediaObject2(str(video),False,True,0,0,960,540)
    media.Name='MechanismTeachingVideo'
    media.AnimationSettings.PlaySettings.PlayOnEntry=True
    media.AnimationSettings.PlaySettings.HideWhileNotPlaying=False
    pres.SaveAs(str(ROOT/'_build/deck_with_media.pptx'),24)
    pres.Close();pres=None
    r={'embeddedSlide':11,'lengthDesignSeconds':18,'video':video.name,'sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'teachingOnly':True,'nativeEncoding':'PowerPoint CreateVideo'}
    (ROOT/'qa/media_embedding.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
    print('NATIVE_MEDIA_EMBEDDED')
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
