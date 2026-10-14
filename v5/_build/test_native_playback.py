"""Play the embedded media in a task-owned off-screen PowerPoint slideshow.

Only a copy of the PPTX is placed in a fresh directory, with no adjacent video.
See https://learn.microsoft.com/en-us/office/vba/api/powerpoint.slideshowview.player
and PowerPoint.Player.State / CurrentPosition / Play.
"""
from pathlib import Path
import tempfile,shutil,time,json,hashlib,sys
import pythoncom,win32com.client,win32gui,win32con
ROOT=Path(__file__).resolve().parents[1]
revision=sys.argv[1] if len(sys.argv)>1 else '03'
src=ROOT/f'outputs/智能体产业研发_V5_{revision}.pptx'
app=pres=window=None;record={'passed':False,'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'isolatedPPTX':True,'samples':[]}
pythoncom.CoInitialize()
try:
    with tempfile.TemporaryDirectory(prefix='v5-native-media-') as temp:
        target=Path(temp)/'presentation.pptx';shutil.copy2(src,target)
        app=win32com.client.DispatchEx('PowerPoint.Application')
        pres=app.Presentations.Open(str(target),ReadOnly=-1,Untitled=0,WithWindow=0)
        media=next(pres.Slides(11).Shapes(i) for i in range(1,pres.Slides(11).Shapes.Count+1) if pres.Slides(11).Shapes(i).Name=='MechanismTeachingVideo')
        ss=pres.SlideShowSettings;ss.ShowType=2;ss.RangeType=2;ss.StartingSlide=11;ss.EndingSlide=11
        ss.ShowWithAnimation=True
        window=ss.Run()
        window.Left=-18000;window.Top=-18000
        raw_id=media.Id
        player=window.View.Player(raw_id() if callable(raw_id) else raw_id);player.Play()
        for wait in [2,5,7]:
            end=time.monotonic()+wait
            while time.monotonic()<end:pythoncom.PumpWaitingMessages();time.sleep(.1)
            record['samples'].append({'state':int(player.State),'position':int(player.CurrentPosition)})
        positions=[x['position'] for x in record['samples']]
        assert positions[0]>0 and positions[0]<positions[1]<positions[2],positions
        assert all(x['state']==0 for x in record['samples']),record
        record['passed']=True
        window.View.Exit();window=None
        # A presentation opened without an editing window may close itself
        # when its only slideshow exits. Do not close that nonexistent object.
        try:pres.Close()
        except Exception as exc:
            if 'Object does not exist' not in str(exc):raise
            record['cleanup']='PowerPoint closed the windowless copy on slideshow exit'
        pres=None
        if app.Presentations.Count==0:app.Quit()
        app=None
except Exception as exc:
    record['error']=str(exc);raise
finally:
    (ROOT/'qa/native_playback.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
    if window:
        try:window.View.Exit()
        except Exception:pass
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
print(json.dumps(record))
