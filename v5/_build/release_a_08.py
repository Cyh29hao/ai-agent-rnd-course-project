"""Promote only checked, native-rendered 08 artifacts and refresh the manifest."""
from pathlib import Path
import json,hashlib,shutil
import fitz
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parent;QA=ROOT/'qa/a_refinement_08';OUT=ROOT/'outputs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
native=json.loads((QA/'native_preview.json').read_text(encoding='utf-8'))
validation=json.loads((QA/'validation.json').read_text(encoding='utf-8'))
ppt=OUT/'智能体产业研发_V5_08.pptx'
assert sha(ppt)==native['candidateSha256']==validation['finalSha256']
assert validation['packageIntegrity']['status']=='pass' and validation['firstPartyImport']['passed']
full=OUT/'智能体产业研发_V5_08_含答辩.pdf'
if full.exists():raise FileExistsError(full)
shutil.copy2(ROOT/'_build/a_refinement_08/preview_含答辩.pdf',full)
with fitz.open(full) as source:
    assert len(source)==34
    for first,last,name in [(0,23,'智能体产业研发_V5_08_主讲.pdf'),(0,6,'A部分投影_V5_08.pdf')]:
        target=OUT/name
        if target.exists():raise FileExistsError(target)
        part=fitz.open();part.insert_pdf(source,from_page=first,to_page=last);part.save(target);part.close()
native.update(finalPptxSha256=sha(ppt),finalBytesIdenticalToNativePreview=True,mainPages=24,APages=7)
(QA/'native.json').write_text(json.dumps(native,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=REPO/'docs/当前版本.json';m=json.loads(p.read_text(encoding='utf-8'))
m.update(updated='2026-10-28',release='V5-08',baseRelease='V5-07',releaseStatus='prepared_pending_validation',mergedIntoMain=False)
for key in ['deck','mainPdf','fullPdf','fullSpokenDOCX','fullSpokenPDF','sourcesDefenseDOCX','sourcesDefensePDF','sharedReportDOCX','sharedReportPDF']:
    m['artifacts'][key]['path']=m['artifacts'][key]['path'].replace('_V5_07','_V5_08')
for key,name in {'ASlidesPdf':'A部分投影_V5_08.pdf','ASpokenDOCX':'A部分口播与练习_V5_08.docx','ASpokenPDF':'A部分口播与练习_V5_08.pdf',
                 'ADefenseDOCX':'组长A部分答辩备课_V5_08.docx','ADefensePDF':'组长A部分答辩备课_V5_08.pdf'}.items():m['artifacts'][key]={'path':'v5/outputs/'+name}
for a in m['artifacts'].values():a['sha256']=sha(REPO/a['path'])
m['sources'].update(ASpoken='v5/17_A部分口播与练习.md',ADefense='v5/18_A部分答辩备课.md',ALayout='v5/_build/build_a_08.mjs',integration='v5/19_08交付与验收.md')
m['collaboration']['leaderOverview']='docs/组长准备总览.md'
m['submissionProgress']['A']={'owner':'陈云海','scope':'01—07页、全场主线与相关材料联动',
    'basis':'组长提出内容、确认选项；AI核源、精修、制图并检查全场衔接','status':'08材料已生成，待本轮验收发布',
    'aiRefinementComplete':True,'readyForPractice':False,'humanUnderstandingVerified':False,'humanTimingVerified':False,
    'designSeconds':205,'refinementBranch':'work/a-refinement-08','finalized':False}
m['defensePreparation']['nextAction']='本轮完成A与全场资料联动；组长先通读主讲，再读A/B/D备课，练习全场及查源；成员按具体卡点反馈。'
m['currentWorkFocus']['status']='A完成08精修与全场联动，待验收发布；组长准备全场理解与试讲，C本轮未单独精修'
m['suggestedNextDirections']['A']='理解并练熟七页，掌握RSI/autoresearch、资源与条件增长；使用A/B/D备课衔接整场'
m['groupDraftMilestone']['status']='A08待验收，B07、D06材料已采用；成员真人理解、计时及C个人改稿情况未核认'
p.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'release':m['release'],'artifacts':len(m['artifacts']),'nativePptx':sha(ppt),'status':m['releaseStatus']}))
