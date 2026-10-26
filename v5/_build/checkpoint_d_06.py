"""Save this takeover's private checkpoint with the existing atomic helper."""
from pathlib import Path
import json
import subprocess
import os
import sys

ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'.git/d-takeover-20261026'
folder.mkdir(exist_ok=True)
complete='--complete' in sys.argv
note={
 'task_id':'course-d-takeover-01a17782-20261026',
 'workspace':str(ROOT),
 'objective':'完成D口播、PPT06、组长备课及同步资料，并实际渲染验收、交付可审阅候选；不自动合并、不虚构真人验收',
 'status':'complete' if complete else 'in_progress',
 'completed':[
   '恢复原线程最新授权；旧任务已Disabled，三次只读续接没有推进产品，本聊天接管制作',
   '14问一手核源、DGM实验分母与附加实验范围修正；四份全场配套文本同步',
   '34页PPT06结构/版面/字体/原生表图检查与Artifact Tool导入通过',
   'PowerPoint后台打开导出；D六页及33/34页实际目视，30页与05像素一致',
   '五份Word与PDF共32页已逐页看，短答粗体及结尾孤页修复完成；正在收尾入口与候选发布' if not complete else '五份Word/PDF共32页逐页检查完成；最终证据与候选发布记录见v5/qa/d_refinement_06'
 ],
 'changed_files':subprocess.check_output(['git','-c','core.quotepath=false','diff','--name-only'],cwd=ROOT,text=True,encoding='utf-8').splitlines(),
 'verification':[
   'v5/qa/d_refinement_06/validation.json记录PPT06结构版面与34页导入通过',
   'v5/qa/native_06.json记录原生PowerPoint导出；主讲24页，含答辩34页',
   'v5/qa/d_refinement_06/documents_export.json记录Word COM导出及源文档散列',
   '未运行实践；真人理解、计时及最终课程提交未验证'
 ],
 'remaining':[] if complete else [
   '完成最终入口检查与候选分支/PR发布，不合并'
 ],
 'blockers':[],
 'next_action':'本轮D材料制作已完成，阅读v5/13_D交付与验收.md后由成员理解练习、组长试讲与决定是否合并。' if complete else '在当前仓库运行python scripts/check_collaboration_docs.py和git diff --check，提交work/d-refinement-06并推送候选、建立PR，不合并；完成后保存complete检查点并交付报告。'
}
prepared=folder/'prepared.json'
prepared.write_text(json.dumps(note,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
codex=Path(os.environ.get('CODEX_HOME',str(Path.home()/'.codex')))
subprocess.run([sys.executable,str(codex/'scripts/codex_quota_workflow.py'),'save','--file',str(folder/'checkpoint.json'),'--input',str(prepared)],check=True)
