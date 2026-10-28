// Editable scientific diagrams, matching the retained V5 template.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const deps='C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const require=createRequire(pathToFileURL(path.join(deps,'task-anchor.cjs')));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const OUT=path.join(ROOT,'_build/a_refinement_08');
const data=JSON.parse(await fs.readFile(path.join(ROOT,'主讲内容.json'),'utf8'));
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',rust:'#B65D3E',muted:'#667680',rule:'#D5D9D5',pale:'#E7EFEB',warm:'#F0E7DE'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:'Microsoft YaHei',fontSize:size,color,bold};o.text.insets=0;return o;}
function rule(s,y){s.shapes.add({geometry:'rect',position:{left:72,top:y,width:1136,height:2},fill:C.rule,line:{fill:'none',width:0}});}
function block(s,x,y,w,h,fill=C.pale){return s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}});}
function arrow(s,x,y,w,dir='rightArrow',color=C.teal){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:24},fill:color,line:{fill:'none',width:0}});}
function base(n,footer,title){const s=p.slides.add();s.background.fill=C.bg;tx(s,n<8?'一  问题与动机':'参考文献',72,30,1136,33,20,C.teal,true);tx(s,title??data[n-1].title,72,90,1136,98,46,C.ink,true);rule(s,190);tx(s,footer,72,676,1070,32,17,C.muted);tx(s,String(n).padStart(2,'0'),1166,676,44,32,18,C.muted);s.speakerNotes.text=n<8?data[n-1].script:'详细链接与文献见04_来源与答辩.md。';return s;}
{
 const s=base(2,'[1] Good，1965；[10] Anthropic Institute，When AI builds itself');
 tx(s,'RSI',72,232,224,110,88,C.teal,true);
 tx(s,'Recursive Self-Improvement',330,244,878,70,48,C.ink,true);
 tx(s,'递归自我改进',333,321,875,58,36,C.teal);
 for(const [x,t] of [[72,'研究系统'],[495,'改进后的系统'],[918,'继续改进']]){block(s,x,431,290,103);tx(s,t,x+18,461,254,55,32,C.ink,true);}
 arrow(s,390,470,80);arrow(s,813,470,80);
 tx(s,'关键：改进能力能否进入下一轮',72,568,1136,59,34,C.ink,true);
 tx(s,'1965 · Good：机器能否参与设计更好的机器？',72,632,1136,34,22,C.muted);
}
{
 const s=base(3,'[12] Karpathy，autoresearch，README；5分钟仅指训练，不含启动与编译');
 tx(s,'Karpathy · 2026年3月 · 原版单GPU',72,219,1136,47,29,C.teal,true);
 const titles=['改训练代码','训练5分钟','比较验证指标','保留或丢弃'];
 const subs=['提出一次修改','小模型实际训练','检查这次结果','决定下一次尝试'];
 titles.forEach((t,i)=>{let x=72+i*295;block(s,x,309,251,144,i===3?C.warm:C.pale);tx(s,t,x+17,335,220,46,31,C.ink,true);tx(s,subs[i],x+17,397,220,44,24,C.muted);if(i<3)arrow(s,x+260,365,28);});
 arrow(s,222,495,837,'leftArrow');
 tx(s,'实验自动继续',504,535,360,45,28,C.teal,true);
 rule(s,587);tx(s,'autoresearch自动做研究；RSI追问研究者能否更会研究',72,615,1136,51,29,C.ink,true);
}
{
 const s=base(4,'[10] Anthropic Institute；[15] Economics of RSI；正反馈为机制示意，非实测增长曲线');
 const titles=['更强的AI','更有效的研发','更强的系统'];
 const subs=['提出与执行研究','探索方法、训练与评测','改善模型、程序或Agent'];
 titles.forEach((t,i)=>{let x=72+i*408;block(s,x,274,320,137,i===1?C.warm:C.pale);tx(s,t,x+20,298,281,48,37,C.ink,true);tx(s,subs[i],x+20,365,281,37,23,C.muted);if(i<2)arrow(s,x+342,330,44);});
 arrow(s,220,462,838,'leftArrow');
 tx(s,'研究成果重新提高研发能力',72,512,1136,55,34,C.teal,true);
 tx(s,'可能产生复利式、甚至指数式加速',72,588,1136,49,34,C.rust,true);
 tx(s,'条件：增益能迁移，计算资源与可靠评测跟得上',72,639,1136,30,22,C.muted);
}
{
 const s=base(5,'[10] Anthropic Institute；[12] autoresearch；跨规模验证为本报告的检查建议');
 const rows=[['会研究','模型能力、工具与研究判断'],['跑得起','推理调用成本、训练算力与实验周期'],['能成立','同预算、新任务，并检查跨规模迁移']];
 rows.forEach(([a,b],i)=>{let y=237+i*119;tx(s,a,72,y,237,60,37,i===1?C.rust:C.teal,true);tx(s,b,341,y+6,867,83,31);if(i<2)rule(s,y+91);});
 tx(s,'算法看真实增益，算力看能验证到多大',72,611,1136,55,33,C.ink,true);
}
{
 const s=base(6,'[4]—[8] 现有案例；[13] AIDE²，2026-09预印本；其结果为作者报告');
 const rows=[['Anthropic','训练方法怎样进入目标模型'],['OpenAI · Google','评测流程与训练程序怎样改进'],['开放研究','Agent怎样改变自身，再继续研究']];
 rows.forEach(([a,b],i)=>{let y=230+i*113;tx(s,a,72,y,384,67,34,C.teal,true);tx(s,b,490,y+5,718,65,30);if(i<2)rule(s,y+87);});
 tx(s,'AIDE²：研究Agent代码层的连续改进',72,577,1136,46,28,C.rust,true);
 tx(s,'沿研发链条看：改了什么，怎样验证，怎样进入下一轮？',72,630,1136,39,27,C.ink,true);
}
const refs=[
 '[1] Good · Speculations Concerning the First Ultraintelligent Machine · 1965',
 '[2] Schmidhuber · Gödel Machines · 2003—2004',
 '[3] Zoph & Le · Neural Architecture Search with Reinforcement Learning · 2016',
 '[4] Chen et al. · Automated Researchers Can Mitigate Well-Characterized Alignment Failures · 2026',
 '[5] Lewi · Automating repetitive work at OpenAI with Codex · 2026',
 '[6] Google DeepMind · AlphaEvolve · 2025',
 '[7] AgentEvolver · Efficient Self-Evolving Agent System · 2025',
 '[8] Sakana AI · Darwin Gödel Machine · 2025',
 '[9] OpenAI · How OpenAI uses Codex · 2026',
 '[10] Anthropic Institute · When AI builds itself · 2026',
 '[11] AgentEvolver contributors · Official repository / Apache-2.0 License',
 '[12] Karpathy · autoresearch · March 2026',
 '[13] Srikanth et al. · Recursive self-improvement of AI research agents · 2026',
 '[14] Lu et al. · The AI Scientist · 2024',
 '[15] Cunningham et al. · The Economics of Recursive Self-Improvement · 2026'
];
for(const [n,start,end] of [[25,0,8],[26,8,15]]){
 const s=base(n,'详细作者、链接与适用范围见来源与答辩；新增[12]—[15]，原[1]—[11]不重排',`参考文献 ${n===25?'1—8':'9—15'}`);
 refs.slice(start,end).forEach((t,i)=>tx(s,t,72,222+i*54,1136,49,20,C.ink));
}
await fs.mkdir(OUT,{recursive:true});
await(await PresentationFile.exportPptx(p)).save(path.join(OUT,'a_authored.pptx'));
console.log('A08_AUTHORED_NATIVE_DIAGRAMS_AND_REFERENCES');
