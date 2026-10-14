"""Recover native export after the windowless slide-show lifecycle ended."""
from pathlib import Path
import shutil,tempfile,json
import pythoncom,win32com.client
ROOT=Path(__file__).resolve().parents[1]
app=pres=None;pythoncom.CoInitialize()
try:
    app=win32com.client.DispatchEx('PowerPoint.Application')
    print('APP',app.Version,'presentations',app.Presentations.Count,'slideshows',app.SlideShowWindows.Count,flush=True)
    if app.Presentations.Count==0:
        app.Visible=-1;app.WindowState=2
    with tempfile.TemporaryDirectory(prefix='v5-export-') as temp:
        copy=Path(temp)/'deck.pptx';shutil.copy2(ROOT/'outputs/智能体产业研发_V5_04.pptx',copy)
        pres=app.Presentations.Open(str(copy),ReadOnly=-1,Untitled=0,WithWindow=-1)
        print('OPENED',pres.Slides.Count,flush=True)
        folder=ROOT/'qa/powerpoint_04';folder.mkdir(exist_ok=True)
        for i in range(1,pres.Slides.Count+1):pres.Slides(i).Export(str(folder/f'{i:02}.png'),'PNG',1280,720)
        # First open is read-only; create a new untitled copy for the static PDF.
        pres.Close();pres=None
        pres=app.Presentations.Open(str(copy),ReadOnly=0,Untitled=-1,WithWindow=-1)
        for i in range(pres.Slides(11).Shapes.Count,0,-1):
            if pres.Slides(11).Shapes(i).Name=='MechanismTeachingVideo':pres.Slides(11).Shapes(i).Delete()
        pres.SaveAs(str(ROOT/'outputs/智能体产业研发_V5_04_含答辩.pdf'),32)
        pres.Close();pres=None
    print('NATIVE_RECOVERED',flush=True)
finally:
    if pres:
        try:pres.Close()
        except Exception:pass
    if app:
        try:
            if app.Presentations.Count==0:app.Quit()
        except Exception:pass
    pythoncom.CoUninitialize()
