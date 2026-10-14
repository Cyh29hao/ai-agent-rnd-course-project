import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const REPO=path.resolve(ROOT,'..');
const SKILL='C:/Users/Cyh29hao/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const PY='C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const {finalizePresentation,applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const FONT='Microsoft YaHei';
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',rust:'#B65D3E',muted:'#667680',rule:'#D5D9D5',pale:'#E7EFEB',soft:'#EFE5DA',white:'#FFFFFF'};
const P=()=>Presentation.create({slideSize:{width:1280,height:720}});
const p=P();
const records=[];
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:FONT,fontSize:size,color,bold};o.text.insets=0;return o;}
function line(s,x,y,w,color=C.rule){s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:2},fill:color,line:{fill:'none',width:0}});}
function node(s,t,x,y,w,h,color=C.pale){const o=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:color,width:0}});o.text=t;o.text.style={typeface:FONT,fontSize:31,color:C.ink};o.text.insets=20;return o;}
function ar(s,x,y,w=70,color=C.teal,dir='rightArrow'){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:25},fill:color,line:{fill:'none',width:0}});}
function base(pr,section,title,source,label){const s=pr.slides.add();s.background.fill=C.bg;tx(s,section,72,30,1100,32,20,C.teal,true);tx(s,title,72,92,1136,95,48,C.ink,true);line(s,72,187,1136);tx(s,source,72,675,1090,32,17,C.muted);tx(s,label,1156,675,72,32,18,C.muted);return s;}
function add(n,intended,title,section,source,script){const s=base(p,section,title,source,`${n}/8`);s.speakerNotes.text=`审批样页，拟用于主讲第${intended}页。\n${script}\n来源与边界见本页脚和审批方案。\n原文：https://alignment.anthropic.com/2026/automated-alignment-researchers/\nOpenAI原文：https://developers.openai.com/blog/automating-repetitive-work-at-openai-with-codex`;records.push({sample:n,intended_page:intended,title,script});return s;}
let s=add(1,9,'激活引导改变教师的回答倾向','模型改进   Anthropic','[4] Chen 等, Automated Researchers…, 2026, App. D.4；此图为机制示意','研究Agent提出的一条路线，是先让教师更少迎合。图中改变的是模型推理时的内部表示。这会影响教师给出的回答分布。学生还没有接受训练，所以这一步本身还没有把新行为写进学生权重。下一页再看它怎样保留下来。');
tx(s,'目标：更少迎合用户的错误观点',72,220,1120,60,35,C.teal,true);
node(s,'同一模型\n原来的内部表示 h',72,329,330,137);
ar(s,430,387);
node(s,'激活引导\n加入方向性干预',518,329,300,137,C.soft);
ar(s,847,387);
node(s,'引导后的教师\n输出倾向改变',933,329,275,137);
tx(s,'激活引导改变教师的输出分布',72,537,1120,65,36);
tx(s,'学生权重尚未在这一步更新',72,604,1100,45,27,C.muted);
s=add(2,10,'蒸馏训练更新学生模型的权重','模型改进   Anthropic','[4] 同上, App. D.4；KL方向与配方系数未由此图指定','第二步才发生训练。引导后的教师给出输出概率分布，学生也给出自己的分布。KL散度用来衡量两者的差异，训练据此调整学生参数。这样，学生在正常推理时也能保留部分行为变化，随后交给外部评测。教师来自目标模型的引导版本，不需要假设更强的外部教师。');
node(s,'教师分布 pT',72,251,385,90);
node(s,'学生分布 pθ',72,430,385,90);
ar(s,484,289,66);ar(s,484,467,66);
node(s,'比较输出分布\nKL训练目标',584,310,283,164,C.soft);
ar(s,895,379,63);
node(s,'更新权重 θ\n正常推理',985,310,223,164);
tx(s,'推理时的临时干预，通过训练形成可保留的行为变化',72,561,1120,70,33,C.teal,true);
s=add(3,11,'改善了多少，要看原来还有多少空间','结果解释   一个教学例子','[4] 指标定义见 §2.2；50、70、100仅为教学数值','先用一个数值例子理解论文的指标。原来50分，训练后70分，满分100分。实际增加了20分，而原来距离满分还有50分，因此关闭了40%的改善空间。这样，下面的论文百分数才有明确的分母。多基准汇总还有几何均值，详细式子留在备份。');
tx(s,'基线',72,234,340,42,27,C.muted);tx(s,'50',72,287,340,92,78,C.ink,true);
tx(s,'训练后',478,234,340,42,27,C.muted);tx(s,'70',478,287,340,92,78,C.teal,true);
tx(s,'该指标最优',898,234,310,42,27,C.muted);tx(s,'100',898,287,310,92,78,C.ink,true);
line(s,72,422,1136);
tx(s,'关闭的改善空间',72,469,450,55,34);
tx(s,'(70 − 50) / (100 − 50) = 40%',523,466,685,88,41,C.teal,true);
tx(s,'接下来才看真实实验。这个40%不是论文结果',72,588,1130,47,27,C.muted);
s=add(4,12,'方法空间不同，探索到的结果也不同','结果解释   相同方法数量下的比较','[4] App. D.4, Fig.20；Qwen3.5-2B／谄媚／前150个已评分方法','现在看论文的真实比较。横轴是前一页解释的改善空间比例。这里比较允许不同训练办法的搜索条件，方法数量都截到150个，并非刚才一个蒸馏配方的单独效果。不受限方法在这一运行中得到更大的改善。不过，每个条件只有一次运行；这些数字属于谄媚任务的爬坡评测，不代表所有任务，也不等于各条件的全部时间和成本相同。');
tx(s,'谄媚任务的改善空间关闭比例',72,218,1120,42,27,C.muted);
const ch=s.charts.add('bar',{position:{left:72,top:282,width:730,height:326},categories:['公开数据 SFT','自由数据 SFT','不受限研究方法'],series:[{name:'改善空间',values:[.06,.029,.233],fill:C.teal}],hasLegend:false,barOptions:{direction:'bar',grouping:'clustered',gapWidth:115},xAxis:{textStyle:{fontSize:24,fill:C.ink}},yAxis:{min:0,max:.30,majorUnit:.05,numberFormatCode:'0%',textStyle:{fontSize:22,fill:C.muted},majorGridlines:{style:'solid',fill:C.rule,width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:26,bold:true,fill:C.ink}},chartFill:C.bg,plotAreaFill:C.bg});
applyPresentationChartFont(ch,{fontFamily:FONT,availableFonts:[FONT]});
tx(s,'比较的是\n可探索的训练办法',850,294,358,118,33,C.teal,true);
tx(s,'每条件一次\n爬坡评测套件\n任务与模型有限定',850,478,355,138,27,C.muted);
tx(s,'SFT指监督微调。各条件允许的训练办法不同',72,625,1136,35,22,C.muted);
s=add(5,14,'执行之前，先让人看见计划','研发现场   OpenAI','[5] Lewi, Automating repetitive work at OpenAI with Codex, 2026, Running evaluations','OpenAI工程师Jeremy Lewi公开了他运行发布前评测的流程。研究员把目标写进Runme，Codex参考旧记录拟定计划。作者写了一句很关键的要求：先等他审阅批准，再开始执行。后面再看执行过程怎样留下命令和结果，让下一次任务可以复用。');
tx(s,'原文的任务要求',72,232,1100,46,28,C.muted);
tx(s,'“Wait for me to review and approve\nthe plan before beginning.”',72,299,1136,142,43,C.ink,true);
line(s,72,474,1136);
tx(s,'目标与旧记录',72,528,338,60,34,C.teal,true);
ar(s,399,544,64);tx(s,'Codex拟计划',487,528,330,60,34,C.teal,true);
ar(s,808,544,64);tx(s,'人审阅后执行',895,528,310,60,34,C.teal,true);
const card=JSON.parse(await fs.readFile(path.join(REPO,'materials/practice/runs/smoke/output.json'),'utf8'));
if(card.claim_id!=='smoke-01'||card.fragment_id!=='T1-run-evals-plan')throw new Error('Unexpected stored evidence card');
s=add(6,21,'一条来源主张怎样变成证据卡','本组实践   一条真实核查任务','原文依据[5]；中文摘自本项目smoke-01原始产物，工具执行由Codex完成','准备报告时，我们要知道一个结论来自谁，能够推广到哪里。于是Codex核对了刚才那条人审要求，打开公开文章并保存证据卡。左边是原文短句，右边是实际保存的中文改写。它还保留了一项限定：这是这位作者介绍的流程。这样我们能回到具体句子检查，哪些结论可以采用，哪些仍需要人工核实。一张卡也不能证明整份报告已经核查完。');
tx(s,'原文的关键要求',72,241,485,45,28,C.muted);
tx(s,'“Wait for me to review\nand approve the plan\nbefore beginning.”',72,306,485,173,33,C.ink,true);
tx(s,'证据卡中的对应改写',650,241,558,45,28,C.muted);
tx(s,'先在笔记本写计划，\n待作者审阅批准后，\n再开始执行。',650,306,558,173,34,C.teal,true);
line(s,72,526,1136);
tx(s,'适用范围：这位作者的工作流，不能外推到全部发布评测',72,558,1136,90,29,C.muted);
s.speakerNotes.text+=`\n真实输出：materials/practice/runs/smoke/output.json\n原始限定：${card.limitation}\n动作记录：materials/practice/runs/smoke/actions.jsonl；部分早期动作事后补记，不能当精确耗时。\n不是本组复现公司训练，也不是四人逐一执行。`;
s=add(7,19,'结果反馈，还要走到研发能力的持续改进','回到题目   两种回流各需要什么证据','本报告分析；所选案例依据见[4][5]及完整方案','刚才的研究系统已经会把评测结果和记录带回下一次尝试，这是一种真实的反馈循环。还要问另一件事：研发产物的改进，是否提高了系统继续研究的能力，并能持续产生更强的后继系统？局部代码或策略改进可以存在，但完整后继研发仍需要更充分的证据。人工审批属于治理安排，不能单凭它是否存在来判定技术能力。');
node(s,'研究系统\n提出与执行方法',72,261,290,132);
ar(s,389,313,70);node(s,'研发产物\n权重、算法或流程',487,261,300,132);
ar(s,815,313,70);node(s,'评测与保留\n检验局部收益',913,261,295,132);
tx(s,'已有：评测结果与记录，反馈给下一次尝试',72,412,1136,47,27,C.teal,true);
ar(s,165,474,960,C.pale,'leftArrow');
tx(s,'待验证：改进是否持续提高下一轮研发能力',72,526,1115,52,30,C.rust,true);
ar(s,165,580,960,C.rule,'leftArrow');
tx(s,'并持续产生更强的后继系统',72,615,1136,48,27,C.rust,true);
s=add(8,'引用页','样页引用的原始资料','来源   编号在PPT、稿件与报告中保持一致','本页只列审批样页使用的来源；整套文献在批准后统一编号','课堂中第一次介绍来源时说作者与研究对象，页脚给短引用与节图，完整链接放备注与文献页。');
tx(s,'[4] Chen Y.-H., Wen J., Kirchner J. H.',72,232,1136,43,28,C.teal,true);
tx(s,'Automated Researchers Can Mitigate Well-Characterized\nAlignment Failures [EB/OL]. Alignment Science Blog, 2026.',72,290,1136,90,25);
tx(s,'https://alignment.anthropic.com/2026/automated-alignment-researchers/',72,390,1136,42,18,C.muted);
tx(s,'[5] Lewi J. Automating repetitive work at OpenAI with Codex',72,471,1136,43,28,C.teal,true);
tx(s,'[EB/OL]. OpenAI Developers, 2026. 引用节：Running evaluations with Codex.',72,526,1136,54,23);
tx(s,'完整URL见备注。核查日期：2026-10-14',72,606,1136,40,22,C.muted);
// Three progressive mechanism frames; no fabricated model execution or measurements.
const mech=P();
for(let k=0;k<3;k++){
 const labels=['引导教师，得到不同的输出倾向','比较教师与学生分布，训练学生权重','学生正常推理，再由外部评测检查'];
 const f=base(mech,'机制教学示意',labels[k],'依据[4] App. D.4重绘；不是运行录屏，也不是实验测量数据',`${k+1}/3`);
 node(f,'引导后的教师\n给出输出分布',72,295,316,150,k===0?C.soft:C.pale);
 ar(f,415,356,64);
 node(f,'KL训练目标\n调整学生权重',507,295,314,150,k===1?C.soft:C.pale);
 ar(f,849,356,64);
 node(f,'正常推理\n外部评测',940,295,268,150,k===2?C.soft:C.pale);
 tx(f,['先生成一种更少迎合的教师输出','分布差异成为训练信号，更新发生在学生参数','正常推理时检查行为改善与能力副作用'][k],72,536,1136,93,34,C.teal,true);
 f.speakerNotes.text='本帧为论文机制的教学重绘。教师为目标模型的引导版本，不编造完整配方或超参数。';
}
const trace=P();
const stages=[['1  输入主张','Codex执行前会写计划，\n并等待作者审阅批准。'],['2  实际来源定位','OpenAI公开文章\nRunning evaluations with Codex'],['3  实际保存的限定','一位作者的工作流自述，\n不能推成所有Codex评测都如此。']];
for(let k=0;k<3;k++){
 const f=base(trace,'本项目实际工件的重排',stages[k][0],'来源：已保存的smoke-01输入、工具动作与output.json；不是UI录屏',`${k+1}/3`);
 tx(f,stages[k][1],72,280,1136,200,47,k===2?C.rust:C.ink,true);
 tx(f,'Codex读取来源并保存证据卡，人的判断仍要对应原文',72,544,1136,93,29,C.teal);
 f.speakerNotes.text='重排显示顺序不代表实际执行速度；早期动作部分为事后补记。未声称四人分别操作。';
}
await fs.mkdir(path.join(ROOT,'qa/slides'),{recursive:true});
await fs.writeFile(path.join(ROOT,'样页口播.json'),JSON.stringify(records,null,2),'utf8');
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'_build/samples_draft.pptx'));
await (await PresentationFile.exportPptx(mech)).save(path.join(ROOT,'_build/mechanism_frames.pptx'));
await (await PresentationFile.exportPptx(trace)).save(path.join(ROOT,'_build/trace_frames.pptx'));
for(let i=0;i<p.slides.items.length;i++){
 const b=await p.export({slide:p.slides.items[i],format:'png',scale:1});
 await fs.writeFile(path.join(ROOT,'qa/slides',`${String(i+1).padStart(2,'0')}.png`),new Uint8Array(await b.arrayBuffer()));
}
const v=process.env.SAMPLE_REVISION||'01';
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:path.join(ROOT,'_build/samples_draft.pptx'),finalPath:path.join(ROOT,'outputs',`审批样页_${v}.pptx`),explicitTotalSlideCount:8,pythonExecutable:PY,integrityValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_package_integrity.py'),layoutValidatorPath:path.join(SKILL,'container_tools/inspect_presentation_layout_geometry.py'),layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],fontPolicy:{basis:'design',families:[FONT]},verifyArtifactToolImport:true,requiredNativeChartOwnerSlides:[4],materializeLiteralChartWorkbooks:true,receiptPath:path.join(ROOT,'qa',`validation_${v}.json`)});
console.log(JSON.stringify({file:result.finalPath,sha256:result.finalSha256}));
