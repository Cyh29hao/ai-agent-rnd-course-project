"""Write a candidate manifest and D-only PDF from verified revision 06 files."""
from pathlib import Path
import hashlib
import json
import fitz
ROOT=Path(__file__).resolve().parents[2]
V5=ROOT/'v5'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

source=fitz.open(V5/'outputs/智能体产业研发_V5_06_主讲.pdf')
target=V5/'outputs/D部分投影_V5_06.pdf'
part=fitz.open();part.insert_pdf(source,from_page=18,to_page=23)
part.save(target);part.close();source.close()

p=ROOT/'docs/当前版本.json'
manifest=json.loads(p.read_text(encoding='utf-8'))
manifest.update(updated='2026-10-26',release='V5-06',releaseStatus='candidate_ready_for_review_and_practice',baseRelease='V5-05',mergedIntoMain=False)
manifest['defensePreparation']['nextAction']='D材料已成套并通过本机验收；成员理解练习、组长熟悉与试讲后反馈具体问题。其他部分按原分工继续。'
manifest['submissionProgress']['D'].update(status='AI精修、联改、核源及本机验收完成；06基本稿可供理解练习，候选待组长采用',aiRefinementComplete=True,readyForPractice=True,aiRefinementCompletedOn='2026-10-26',humanUnderstandingVerified=False,humanTimingVerified=False,merged=False,finalized=False,refinementBranch='work/d-refinement-06')
manifest['groupDraftMilestone']['status']='D已有成套06基本稿；成员本人理解、试讲与其他段落的准备情况未核认'
manifest['currentWorkFocus']['status']='D精修本轮完成；组长后续仍以A为主并审核衔接全场，未在本轮开展A重写'
artifacts={}
for key,name in [('deck','智能体产业研发_V5_06.pptx'),('mainPdf','智能体产业研发_V5_06_主讲.pdf'),('fullPdf','智能体产业研发_V5_06_含答辩.pdf'),('DSlidesPdf','D部分投影_V5_06.pdf')]:
    path=V5/'outputs'/name;artifacts[key]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
for key,stem in [('DSpoken','D部分口播与练习_V5_06'),('DDefense','组长D部分答辩备课_V5_06'),('fullSpoken','全场口播_V5_06'),('sourcesDefense','来源与答辩_V5_06'),('sharedReport','课程报告_V5_06')]:
    for ext in ['docx','pdf']:
        path=V5/'outputs'/f'{stem}.{ext}'
        artifacts[key+ext.upper()]={'path':path.relative_to(ROOT).as_posix(),'sha256':sha(path)}
manifest['artifacts']=artifacts
manifest['sources'].update(DSpoken='v5/11_D部分口播与练习.md',DDefense='v5/10_D部分答辩备课.md',DLayout='v5/_build/build_d_06.mjs')
p.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
receipt={'release':'V5-06','status':'candidate_not_merged','artifacts':artifacts,'DOriginal':{
 'path':'collaboration/proposals/D_曹天卓_20261025/D_19-24页_曹天卓_V5修订.docx',
 'sha256':sha(ROOT/'collaboration/proposals/D_曹天卓_20261025/D_19-24页_曹天卓_V5修订.docx')},
 'humanTimingVerified':False,'practiceRun':False,'fullCourseGoalComplete':False}
(V5/'qa/d_refinement_06/deliverable_manifest.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('CANDIDATE_V5_06_MANIFEST',len(artifacts))
