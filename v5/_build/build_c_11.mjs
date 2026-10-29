import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const deps='C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const require=createRequire(pathToFileURL(path.join(deps,'task-anchor.cjs')));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),OUT=path.join(ROOT,'_build/final_11');
const data=JSON.parse(await fs.readFile(path.join(ROOT,'主讲内容.json'),'utf8'));
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',pale:'#E7EFEB',warm:'#F0E7DE',rule:'#D5D9D5',muted:'#667680'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:'Microsoft YaHei',fontSize:size,color,bold};o.text.insets=0;return o;}
function box(s,x,y,w,h,fill=C.pale){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function arrow(s,x,y,w,dir='rightArrow'){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:24},fill:C.teal,line:{fill:'none',width:0}});}
function base(n,foot){const s=p.slides.add();s.background.fill=C.bg;tx(s,data[n-1].section,72,30,1136,33,20,C.teal,true);tx(s,data[n-1].title,72,90,1136,98,46,C.ink,true);box(s,72,190,1136,2,C.rule);tx(s,foot,72,676,1070,32,17,C.muted);tx(s,String(n),1166,676,44,32,18,C.muted);s.speakerNotes.text=data[n-1].script;return s;}
{
 const s=base(14,'[5] Lewi，Codex评测工作流，2026');
 box(s,72,219,1136,66);tx(s,'发布前评测：模型或功能上线前，检查是否符合预期',110,236,1080,48,28);
 box(s,72,312,240,82,C.teal);tx(s,'研究员',100,337,200,50,32,'#FFFFFF',true);box(s,331,312,877,82);tx(s,'确定本次评测目标',370,337,800,50,30);
 box(s,72,414,1136,2,C.rule);box(s,72,434,240,82,C.teal);tx(s,'Codex',100,459,200,50,32,'#FFFFFF',true);
 ['找工具','准备命令','处理执行问题','解释结果'].forEach((t,i)=>{const x=331+i*224;box(s,x,434,205,82);tx(s,t,x+18,460,180,48,26);});
 tx(s,'Agent参与评测流程：人设定目标，Codex执行获批步骤',72,563,1136,72,29,C.muted);
}
{
 const s=base(15,'[5] Lewi，Running evaluations with Codex');
 tx(s,'作者给Codex的要求',72,218,1136,42,28,C.muted);box(s,72,267,1136,155);
 tx(s,'“Wait for me to review and approve\nthe plan before beginning.”',145,284,1050,104,42,C.ink,true);
 tx(s,'开始之前，等我审阅并批准计划',145,382,1050,40,27,C.muted);
 const labels=['目标与旧记录','Codex拟计划','人批准后由Codex执行'];
 labels.forEach((t,i)=>{let x=[72,461,845][i],w=[322,312,363][i];box(s,x,456,w,78,i===2?C.teal:C.pale);tx(s,t,x+20,479,w-30,50,i===2?28:31,i===2?'#FFFFFF':C.teal,true);if(i<2)arrow(s,x+w+7,482,50);});
 tx(s,'研究员检查评测选择、关键条件与资源取舍',72,583,1136,54,28,C.muted);
}
{
 const s=base(16,'[5] Lewi，Runme笔记与可复用上下文');
 tx(s,'Runme笔记',72,222,350,52,39,C.teal,true);tx(s,'执行命令，并保存输出、解释和决定',410,237,798,45,28,C.muted);
 const a=['目标与计划','命令与输出','解释与取舍'],b=['为什么做，准备怎样做','实际做了什么，发生了什么','后续会话可以读取判断依据'];
 a.forEach((t,i)=>{const y=307+i*87;box(s,72,y,288,75,C.teal);box(s,372,y,836,75);tx(s,t,98,y+24,250,49,31,'#FFFFFF',true);tx(s,b[i],403,y+24,775,49,29);});
 box(s,72,585,1136,67,C.warm);tx(s,'外部记录提供上下文，不是Codex权重更新的证据',98,604,1080,49,29,C.ink,true);
}
{
 const s=base(17,'[6] Google DeepMind，AlphaEvolve，2025');
 const heads=['Gemini','自动评测器','程序数据库'],subs=['提出程序候选','验证、运行和打分','进化算法选择父代'];
 heads.forEach((t,i)=>{const x=[72,461,845][i],w=[317,312,363][i];box(s,x,259,w,150);tx(s,t,x+24,303,w-38,48,31,C.ink,true);tx(s,subs[i],x+24,350,w-38,46,26);if(i<2)arrow(s,x+w+8,320,53);});
 arrow(s,227,438,680,'leftArrow');tx(s,'数据库保存候选，选择父代后继续生成',240,479,860,46,28,C.muted);
 box(s,72,548,1136,84);tx(s,'改进对象：算法程序',98,561,1080,45,31,C.teal,true);tx(s,'用正确性与运行性能检验修改',98,604,1080,42,26);
}
{
 const s=base(18,'[6] Google DeepMind，Enhancing AI training and inference；官方案例，非本组复现');
 [[72,'23%','所举矩阵乘法kernel的加速','局部算子'],[656,'1%','Gemini总训练时间减少','整段训练']].forEach(([x,num,label,scope],i)=>{box(s,x,219,552,221);tx(s,num,x+25,244,500,101,88,i? '#B95B38':C.teal,true);tx(s,label,x+25,359,500,47,29);tx(s,scope,x+25,400,500,39,24,C.muted);});
 box(s,72,459,1136,83);tx(s,'同类kernel优化的工程时间（官方报告）',98,471,1080,43,28,C.teal,true);tx(s,'专家数周工作，转为数天自动实验',98,509,1080,39,27);
 tx(s,'局部加速不等于整体加速：先看对象与分母',72,577,1136,62,32,C.teal,true);
}
await fs.mkdir(OUT,{recursive:true});await(await PresentationFile.exportPptx(p)).save(path.join(OUT,'c_authored.pptx'));
console.log('C11_NATIVE_EDITABLE_SLIDES_AUTHORED');
