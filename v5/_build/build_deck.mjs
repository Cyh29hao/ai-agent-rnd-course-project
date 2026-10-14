import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL='C:/Users/Cyh29hao/.codex/plugins/cache/openai-primary-runtime/presentations/26.1011.11113/skills/presentations';
const FONT='Microsoft YaHei';
const {applyPresentationChartFont}=await import(pathToFileURL(path.join(SKILL,'container_tools/artifact_tool_utils.mjs')).href);
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',rust:'#B65D3E',muted:'#667680',rule:'#D5D9D5',pale:'#E7EFEB',soft:'#EFE5DA'};
const source={
1:['Good, 1965','https://scienceplusplus.org/metascience/assets/Good1965.pdf'],
2:['Schmidhuber, Gödel Machines','https://people.idsia.ch/~juergen/gmweb4/gmweb4.html'],
3:['Zoph & Le, NAS, 2016','https://arxiv.org/abs/1611.01578'],
4:['Chen 等, Automated Researchers…, 2026','https://alignment.anthropic.com/2026/automated-alignment-researchers/'],
5:['Lewi, OpenAI评测工作流, 2026','https://developers.openai.com/blog/automating-repetitive-work-at-openai-with-codex'],
6:['Google DeepMind, AlphaEvolve, 2025','https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/'],
7:['AgentEvolver论文, 2025','https://arxiv.org/html/2511.10395v1'],
8:['Sakana AI, DGM, 2025','https://sakana.ai/dgm/'],
9:['OpenAI研究加速报告, 2026','https://openai.com/index/research-acceleration-view-inside-openai/'],
10:['Anthropic, Recursive Self-Improvement','https://www.anthropic.com/institute/recursive-self-improvement'],
11:['modelscope/AgentEvolver','https://github.com/modelscope/AgentEvolver']};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:FONT,fontSize:size,color,bold};o.text.insets=0;return o;}
function rule(s,x,y,w,color=C.rule){s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:2},fill:color,line:{fill:'none',width:0}});}
function box(s,t,x,y,w,h,color=C.pale,size=30){const o=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:color,line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:FONT,fontSize:size,color:C.ink};o.text.insets=18;return o;}
function ar(s,x,y,w=64,color=C.teal,dir='rightArrow'){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:24},fill:color,line:{fill:'none',width:0}});}
const short={1:'Good, 1965',2:'Gödel Machines',3:'NAS, 2016',4:'Chen等, AAR, 2026',5:'Lewi, Codex评测, 2026',6:'AlphaEvolve, 2025',7:'AgentEvolver, 2025',8:'DGM, 2025',9:'OpenAI研究加速, 2026',10:'Anthropic RSI分析',11:'AgentEvolver代码库'};
const tiny={4:'AAR',5:'Codex评测',6:'AlphaEvolve',7:'AgentEvolver',8:'DGM',10:'RSI分析'};
function footer(ids,extra=''){return ids.map(i=>`[${i}] ${ids.length>=5?(tiny[i]||short[i]):short[i]}`).join('；')+(extra?`；${extra}`:'');}
function base(pr,section,title,foot,num){const s=pr.slides.add();s.background.fill=C.bg;tx(s,section,72,30,1136,33,20,C.teal,true);tx(s,title,72,90,1136,98,46,C.ink,true);rule(s,72,190,1136);tx(s,foot,72,676,1075,32,17,C.muted);tx(s,String(num).padStart(2,'0'),1166,676,44,32,18,C.muted);return s;}
function row(s,a,b,y){tx(s,a,72,y,318,60,33,C.teal,true);tx(s,b,430,y,778,90,31);rule(s,72,y+95,1136);}
function step(s,idx,title,detail,x,y,w){tx(s,idx,x,y,w,57,40,C.rust,true);tx(s,title,x,y+70,w,80,33,C.ink,true);tx(s,detail,x,y+169,w,130,27,C.muted);}
const data=JSON.parse(await fs.readFile(path.join(ROOT,'主讲内容.json'),'utf8'));
function mechanism(pr,num,stage=-1){const s=base(pr,'二  模型改进  Anthropic','蒸馏训练把行为变化写进学生权重',footer([4],'App. D.4；机制教学示意'),num);
 box(s,'教师分布 pT\n目标模型的引导版本',72,253,340,105,stage===0?C.soft:C.pale,28);ar(s,440,305);
 box(s,'学生分布 pθ\n训练前的学生',72,431,340,105,C.pale,28);ar(s,440,481);
 box(s,'比较输出分布\nKL训练目标\n更新学生权重',533,266,305,270,stage===1?C.soft:C.pale,30);ar(s,866,389);
 box(s,'正常推理\n外部评测',967,332,241,140,stage===2?C.soft:C.pale,30);
 tx(s,stage<0?'分布差异成为训练信号，参数更新发生在学生模型':[
 '① 教师来自目标模型的引导版本','② 比较教师与学生分布，据此调整学生参数','③ 正常推理时检查行为改善与能力副作用'][stage],72,558,1136,60,32,C.teal,true);
 tx(s,'KL方向和完整配方由具体方法定义，此图不指定超参数',72,630,1136,38,23,C.muted);return s;}
for(const d of data){
 let s=d.layout==='cover'?p.slides.add():d.layout==='distill'?mechanism(p,d.n):base(p,d.section,d.title,footer(d.sources),d.n);
 const refs=d.sources.map(i=>`[${i}] ${source[i][0]}\n${source[i][1]}`).join('\n');
 s.speakerNotes.text=`主讲第${d.n}页，设计预算${d.seconds}秒（未真人计时）。\n${d.script}\n\n来源：\n${refs}`;
 switch(d.layout){
 case 'cover':
  s.background.fill=C.ink;
  // Cover is a flat typography composition, all text remains editable.
  tx(s,'大模型与智能体工程实践',72,54,1136,45,24,'#CDDCD7');
  tx(s,'智能体在大模型产业\n研发中的应用',72,153,1136,195,64,C.bg,true);
  tx(s,d.body[0],72,378,1136,76,41,'#B4DAD2',true);
  tx(s,d.body[1],72,473,1136,64,29,C.bg);
  tx(s,'陈云海   张程翔   赵金城   曹天卓',72,592,1136,44,28,C.bg);
  break;
 case 'history':
  tx(s,'1965',72,228,418,150,108,C.teal,true);
  tx(s,'I. J. Good',72,407,410,65,36,C.muted);
  tx(s,'如果机器能参与设计\n更好的机器，\n改进会不会继续？',550,251,658,237,48,C.ink,true);
  rule(s,72,547,1136);tx(s,'今天可以追问：它接手了哪项任务，交付了什么结果',72,583,1136,67,30,C.teal);break;
 case 'tasks':
  ['方法','实现','评测','下一轮'].forEach((t,i)=>{tx(s,t,72+i*292,260,259,58,38,C.teal,true);tx(s,d.body[i],72+i*292,348,253,158,29);if(i<3)ar(s,321+i*292,278,33);});
  tx(s,'一次行为改善，可能伴随其他能力下降',72,564,1136,80,37,C.rust,true);break;
 case 'routes':
  tx(s,'证明后修改',72,231,510,64,38,C.teal,true);tx(s,'Gödel Machine\n先证明修改有益',72,330,510,128,33);
  tx(s,'评测后保留',690,231,518,64,38,C.rust,true);tx(s,'NAS与DGM\n搜索候选，再检验结果',690,330,518,128,33);
  rule(s,72,512,1136);tx(s,'真实研发怎样验证“更好”，贯穿今天的案例',72,554,1136,95,34);break;
 case 'agenda':
  d.body.forEach((t,i)=>{tx(s,`0${i+1}`,72,231+i*101,110,64,42,C.teal,true);tx(s,t,237,235+i*101,970,70,37);});break;
 case 'selection':
  row(s,'Anthropic','方法、目标模型权重与实验评测',237);
  row(s,'OpenAI','研发任务、工具使用与决策记录',365);
  tx(s,'Google与开放研究补充算法、策略和代码的改动',72,532,1136,81,32,C.muted);
  tx(s,'按可检查的公开证据选案例',72,614,1136,42,27,C.teal,true);break;
 case 'roles':
  box(s,'研究Agent\nClaude Opus 4.8\n提出并实施方法',72,279,320,153,C.pale,27);ar(s,420,343);
  box(s,'Qwen3.5-2B\n接受后训练',518,279,310,153,C.soft);ar(s,856,343);
  box(s,'评测器\n行为与能力',954,279,254,153);
  tx(s,'任务：减少顺着用户错误观点说的行为',72,222,1136,48,32,C.teal,true);
  tx(s,'研究者、被训练模型、评测器承担不同角色',72,525,1136,94,36);break;
 case 'experiment':
  step(s,'01','提出假设','资料与研究方法',72,226,241);
  step(s,'02','冻结小论文','本轮结果尚未公布',366,226,241);
  step(s,'03','提交实现','代码监控后训练',660,226,241);
  step(s,'04','外部评测','反馈结果与副作用',954,226,254);
  tx(s,'典型方法预算：约1张H200，约30分钟',72,553,1136,53,32,C.teal,true);
  tx(s,'基本规则：禁用评测数据，禁止从研究Agent或更强模型蒸馏',72,623,1136,43,24,C.muted);break;
 case 'memory':
  box(s,'多个研究Agent\n并行探索候选',72,274,328,161);
  ar(s,427,341);box(s,'共享记录\n方法、评分与失败',521,274,317,161,C.soft);
  ar(s,865,341);box(s,'新会话\n读取后继续尝试',956,274,252,161);
  ar(s,235,480,810,C.pale,'leftArrow');
  tx(s,'研究能接续：记忆保存在外部记录中',72,550,1136,72,36,C.teal,true);break;
 case 'steering':
  tx(s,'目标：更少迎合错误观点',72,220,1136,52,34,C.teal,true);
  box(s,'原内部表示 h',72,329,330,126);ar(s,430,380);
  box(s,'方向性干预\nh′ = h + αv',518,329,300,126,C.soft);ar(s,847,380);
  box(s,'引导后的教师\n输出倾向改变',933,329,275,126);
  tx(s,'推理时的临时改变，怎样保留下来？',72,530,1136,77,37);
  tx(s,'h′公式为一般教学示意，方向与强度取决于具体方法',72,617,1136,41,24,C.muted);break;
 case 'distill':break;
 case 'headroom':
  [['基线','50'],['训练后','70'],['该指标最优','100']].forEach((v,i)=>{tx(s,v[0],72+i*407,235,321,50,29,C.muted);tx(s,v[1],72+i*407,294,321,115,82,i===1?C.teal:C.ink,true);});
  rule(s,72,431,1136);tx(s,'关闭的改善空间',72,474,450,59,34);
  tx(s,'(70 − 50) / (100 − 50) = 40%',523,473,685,87,41,C.teal,true);
  tx(s,'50、70、100是教学数值，40%不是论文结果',72,602,1136,48,25,C.muted);break;
 case 'results':{
  tx(s,'Qwen3.5-2B谄媚任务：前150个已评分方法',72,220,1136,45,28,C.muted);
  const ch=s.charts.add('bar',{position:{left:72,top:280,width:737,height:324},categories:['原样公共数据 SFT','自由构造数据 SFT','不受限研究方法'],series:[{name:'改善空间',values:[.06,.029,.233],fill:C.teal}],hasLegend:false,barOptions:{direction:'bar',grouping:'clustered',gapWidth:115},xAxis:{textStyle:{fontSize:24,fill:C.ink}},yAxis:{min:0,max:.30,majorUnit:.05,numberFormatCode:'0%',textStyle:{fontSize:22,fill:C.muted},majorGridlines:{style:'solid',fill:C.rule,width:1}},dataLabels:{showValue:true,position:'outEnd',numberFormatCode:'0.0%',textStyle:{fontSize:26,bold:true,fill:C.ink}},chartFill:C.bg,plotAreaFill:C.bg});
  applyPresentationChartFont(ch,{fontFamily:FONT,availableFonts:[FONT]});
  tx(s,'比较搜索条件\n允许的方法不同',858,306,350,115,32,C.teal,true);
  tx(s,'每条件一次运行\n爬坡评测套件',858,478,350,108,27,C.muted);
  tx(s,'横轴：改善空间关闭比例；选取[4] Fig.20中的三项比较',72,623,1136,41,23,C.muted);break;}
 case 'evaltask':
  tx(s,'发布前，怎样检查模型是否达到要求？',72,228,1136,87,40,C.teal,true);
  row(s,'研究员','确定本次评测目标',350);row(s,'Codex','找工具、写命令、检查结果',476);break;
 case 'approval':
  tx(s,'作者给Codex的要求',72,229,1136,48,28,C.muted);
  tx(s,'“Wait for me to review and approve\nthe plan before beginning.”',72,303,1136,153,43,C.ink,true);
  rule(s,72,484,1136);tx(s,'目标与旧记录',72,539,340,62,34,C.teal,true);ar(s,411,551,55);
  tx(s,'Codex拟计划',492,539,326,62,34,C.teal,true);ar(s,825,551,55);tx(s,'人审阅后执行',910,539,298,62,34,C.teal,true);break;
 case 'record':
  tx(s,'Runme笔记',72,229,450,65,41,C.teal,true);
  row(s,'目标与计划','为什么做，准备怎样做',323);
  row(s,'命令与输出','实际做了什么，发生了什么',439);
  tx(s,'解释与取舍',72,560,318,62,33,C.teal,true);tx(s,'下一次任务可以读取判断依据',430,560,778,78,31);break;
 case 'evolution':
  box(s,'Gemini\n提出程序候选',72,282,320,149);ar(s,420,343);
  box(s,'执行与评测\n正确性、性能',518,282,310,149,C.soft);ar(s,856,343);
  box(s,'保留较好程序\n继续产生候选',954,282,254,149);
  ar(s,226,476,820,C.pale,'leftArrow');tx(s,'改进对象：能运行和检查的算法程序',72,554,1136,78,36,C.teal,true);break;
 case 'localglobal':
  tx(s,'23%',72,231,520,167,113,C.teal,true);tx(s,'所举矩阵乘法kernel的加速',72,434,520,105,32);
  tx(s,'1%',738,231,470,167,113,C.rust,true);tx(s,'Gemini总训练时间减少',738,434,470,105,32);
  rule(s,72,562,1136);tx(s,'局部与整体的分母不同',72,599,1136,52,33,C.muted);break;
 case 'open':
  tx(s,'通义 AgentEvolver',72,233,537,63,37,C.teal,true);tx(s,'生成任务\n复用经验\n贡献归因支持策略训练',72,328,527,178,32);
  tx(s,'Sakana DGM',696,233,512,63,37,C.rust,true);tx(s,'修改Agent自身代码\n运行基准检查\n保留候选谱系继续探索',696,328,512,178,32);
  rule(s,72,551,1136);tx(s,'策略训练与代码自改，需要分别追踪',72,587,1136,63,34);break;
 case 'comparison':
  {const vals=[['案例','改动对象','检验依据'],['Anthropic','目标模型权重','训练后的行为与能力'],['OpenAI','流程与记录','命令结果、研究员判断'],['Google','算法程序','正确性与性能'],['开放研究','策略或代码','任务评测、版本表现']];
  const tb=s.tables.add({rows:5,columns:3,left:72,top:230,width:1136,height:405,columnWidths:[270,365,501],values:vals});
  tb.borders.assign({fill:C.rule,width:1,style:'solid'});
  for(let r=0;r<5;r++)for(let c=0;c<3;c++){const cell=tb.getCell(r,c);cell.fill=r===0?C.pale:C.bg;cell.text.style={typeface:FONT,fontSize:r===0?27:c===2?27:31,color:c===0?C.teal:C.ink,bold:r===0||c===0};cell.text.insets=12;}
  break;}
 case 'rsi':
  box(s,'研究系统\n提出与执行方法',72,256,290,132);ar(s,389,309,70);
  box(s,'研发产物\n权重、算法或流程',487,256,300,132);ar(s,815,309,70);box(s,'评测与保留\n检验局部收益',913,256,295,132);
  tx(s,'已有：结果与记录反馈到下一次尝试',72,411,1136,47,27,C.teal,true);ar(s,165,475,960,C.pale,'leftArrow');
  tx(s,'待验证：基础模型后继研发能力持续提高',72,525,1136,54,30,C.rust,true);ar(s,165,588,960,C.rule,'leftArrow');
  tx(s,'并持续产生更强的后继模型',72,623,1136,38,25,C.rust,true);break;
 case 'evidence':
  d.body.forEach((t,i)=>{tx(s,`${i+1}`,72,242+i*125,103,77,49,C.rust,true);tx(s,t,238,251+i*125,970,85,35);});break;
 case 'conclusion':
  tx(s,'能交付局部改进',72,244,1136,82,49,C.teal,true);
  tx(s,'权重、算法、策略、代码和研发流程',72,346,1136,77,32);
  rule(s,72,464,1136);tx(s,'基础模型后继研发的持续循环，仍需充分检验',72,518,1136,110,40,C.rust,true);break;
 case 'thanks':
  d.body.forEach((t,i)=>tx(s,t,72,253+i*115,1136,77,40,i===2?C.rust:C.teal,true));break;
 default:throw new Error(`No layout ${d.layout}`);
 }
}
const backups=[
 {title:'参考文献  历史与模型研发',ids:[1,2,3,4,5],items:[
 '[1] Good I. J. Speculations Concerning the First Ultraintelligent Machine. Advances in Computers, 1965, 6:31–88.',
 '[2] Schmidhuber J. Gödel Machines: Self-Referential Universal Problem Solvers Making Provably Optimal Self-Improvements. 2003/2004技术报告.',
 '[3] Zoph B, Le Q V. Neural Architecture Search with Reinforcement Learning. arXiv:1611.01578, 2016.',
 '[4] Chen Y.-H., Wen J., Kirchner J. H. Automated Researchers Can Mitigate Well-Characterized Alignment Failures. 2026.',
 '[5] Lewi J. Automating repetitive work at OpenAI with Codex. OpenAI Developers, 2026-08-25.']},
 {title:'参考文献  算法、开放研究与RSI',ids:[6,7,8,9,10,11],items:[
 '[6] Google DeepMind. AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms. 2025.',
 '[7] AgentEvolver: Towards Efficient Self-Evolving Agent System. arXiv:2511.10395, 2025.',
 '[8] Zhang等. Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents. 2025；同团队官方说明.',
 '[9] OpenAI. Research acceleration: The view inside OpenAI. 2026.',
 '[10] Anthropic Institute. When AI builds itself. 2026.',
 '[11] ModelScope. AgentEvolver官方代码仓库. Apache-2.0.']},
 {title:'训练结果怎样避免只在排行榜上好看',ids:[4],items:[
 '研究Agent能看到爬坡评分，隐藏评测由独立评测器执行',
 '能力门槛：MMLU、GSM8K、IFEval的95%置信区间检查',
 'held-out参与选择Petri方法时承担验证集作用',
 '外部评测与代码监控降低风险，仍需检查取巧和泛化'],notes:'AAR §2.3、§3.2、§5.1。能力门槛是95%置信区间不完全低于基线，不能改写成每项都无下降。held-out在选择Petri方法时是validation，不能将所有阶段称为完全独立终测。'},
 {title:'KL与改善空间的数学解释',ids:[4],items:[
 '教学选定的KL(pT∥pθ) = Σ pT(y) log[pT(y)/pθ(y)]',
 '优化学生参数，使学生输出分布接近教师',
 '单基准改善比例 = (得分 − 基线) / (最优 − 基线)',
 '多基准汇总使用几何均值，负向指标需按原文转换'],notes:'KL方向仅为教学选定，不宣称获胜配方的全部方向、系数或实现。互动HTML的二类单参数原型是教学演示，不是AAR训练复现。'},
 {title:'前150个方法比较的适用范围',ids:[4],items:[
 '不受限研究允许探索不同训练配方',
 '原样公共数据SFT与自由构造数据SFT限制训练方式',
 '23.3%、6.0%、2.9%对应Fig.20前150个已评分方法',
 '每条件一次，仅爬坡评测；不推断单一方法因果贡献'],notes:'AAR App. D.4。全程峰值26.4/18.7/6.0/4.5与固定方法数不同。相同方法数不等于同全部时间、成本。该比较未重跑held-out/Petri。'},
 {title:'另一个实验：研究Agent只生成训练数据',ids:[4],items:[
 '研究Agent：Sonnet 5；只能构造训练数据',
 '目标：Opus 4.8早期检查点，已有对齐SFT',
 '产生数据后训练目标模型，再做Petri评测',
 '这个设置与Qwen激活引导实验分开'],notes:'AAR §6，Fig.9。研究Agent的ECI156与目标ECI158是所报代理指标，不能推断全能力排序。'},
 {title:'65%与72%究竟衡量什么',ids:[4],items:[
 '所设十维Petri审计：覆盖加权的改善空间',
 '公式：改善维度比例 × 改善比例的几何均值',
 '研究胜出检查点65%，发布版对照72%',
 '它衡量设定维度的改善，不能读成总体安全通过率'],notes:'AAR §6 Fig.9、App. E.1。与开放权重蒸馏不同实验。没有因此证明更弱研究Agent在全部能力上超越目标。'},
 {title:'3.1个Agent工作日怎样理解',ids:[9],items:[
 'Agent运行工作日 / 人类工作日 = 3.1',
 '按8小时折算运行时长，截至2026年8月中',
 '可以说明组织采用规模，不能直接换算产出效率',
 '净提效还需质量、人工成本与失败任务等对照'],notes:'OpenAI研究加速报告§1与方法。3.1不是生产率倍数。运行时间不会自动转化为有效研究贡献。'},
 {title:'代码开放与模型训练开放的区别',ids:[7,8,11],items:[
 'AgentEvolver支持任务生成、经验复用和策略训练',
 'DGM探索修改Agent工具与代码，底层权重需另查',
 '框架代码可以开放，训练权重和数据可能另有条件',
 '复现应逐项确认模型、数据、环境和计算预算'],notes:'不要把框架Apache-2.0外推为所有模型、训练数据或基础设施开放。SWE与Polyglot结果是各自基准，不能与Qwen谄媚分数直接排名。'},
 {title:'为什么人审不能单独判定RSI',ids:[4,5,8,10],items:[
 '人工审批说明谁控制目标、执行或发布',
 '技术判断要追踪修改对象与能力反馈',
 '有审批的系统仍可能存在局部递归能力改进',
 '没有审批也不保证持续后继研发或可靠结果'],notes:'这是本报告对技术能力与治理安排的区分。RSI并无本报告通用评分标准；对所选公开证据做限定性判断。'}
];
for(const [k,b] of backups.entries()){
 const n=25+k;const s=base(p,k<2?'参考文献':'答辩备份',b.title,k<2?'完整链接与来源定位见备注及来源手册':footer(b.ids),n);
 b.items.forEach((t,i)=>tx(s,t,72,232+i*(b.items.length>5?65:91),1136,b.items.length>5?64:85,k<2?25:30,i===0&&k>=2?C.teal:C.ink,i===0&&k>=2));
 s.speakerNotes.text=(b.notes||'文献编号与主讲保持一致；完整来源定位见来源与答辩手册。')+'\n'+b.ids.map(i=>`[${i}] ${source[i][0]}\n${source[i][1]}`).join('\n');
}
const frames=Presentation.create({slideSize:{width:1280,height:720}});for(let k=0;k<3;k++){const s=mechanism(frames,11,k);s.speakerNotes.text='机制教学示意，不是模型运行录屏；三段各6秒。';}
await fs.mkdir(path.join(ROOT,'_build'),{recursive:true});await fs.mkdir(path.join(ROOT,'outputs'),{recursive:true});await fs.mkdir(path.join(ROOT,'qa'),{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(ROOT,'_build/deck_draft.pptx'));
await (await PresentationFile.exportPptx(frames)).save(path.join(ROOT,'_build/mechanism_frames.pptx'));
await fs.writeFile(path.join(ROOT,'qa/deck_manifest.json'),JSON.stringify({mainSlides:24,totalSlides:p.slides.items.length,sources:source,seconds:data.reduce((a,d)=>a+d.seconds,0),practice:'deferred; excluded'},null,2),'utf8');
console.log('DRAFT_EXPORTED',p.slides.items.length);
