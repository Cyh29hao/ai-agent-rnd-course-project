import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
const deps='C:/Users/Cyh29hao/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const require=createRequire(pathToFileURL(path.join(deps,'task-anchor.cjs')));
const {Presentation,PresentationFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..'),OUT=path.join(ROOT,'_build/inspiration_10');
const data=JSON.parse(await fs.readFile(path.join(ROOT,'主讲内容.json'),'utf8'));
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',pale:'#E7EFEB',warm:'#F0E7DE',rule:'#D5D9D5',muted:'#667680',light:'#B7DAD3'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:'Microsoft YaHei',fontSize:size,color,bold};o.text.insets=0;return o;}
function rule(s,y){s.shapes.add({geometry:'rect',position:{left:72,top:y,width:1136,height:2},fill:C.rule,line:{fill:'none',width:0}});}
function arrow(s,x,y,w,dir='rightArrow'){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:24},fill:C.teal,line:{fill:'none',width:0}});}
function base(n,foot){const s=p.slides.add();s.background.fill=C.bg;tx(s,data[n-1].section,72,30,1136,33,20,C.teal,true);tx(s,data[n-1].title,72,90,1136,98,46,C.ink,true);rule(s,190);tx(s,foot,72,676,1070,32,17,C.muted);tx(s,String(n).padStart(2,'0'),1166,676,44,32,18,C.muted);s.speakerNotes.text=data[n-1].script;return s;}
{
 const s=p.slides.add();s.background.fill=C.ink;
 tx(s,'主题一 · 行业应用案例研究',72,55,1136,43,26,C.light);
 tx(s,data[0].title,72,161,1136,100,64,'#FAF8F3',true);
 tx(s,'让Agent参与改进模型与自身',72,315,1136,64,39,C.light,true);
 tx(s,'陈云海  张程翔  赵金城  曹天卓',72,610,1136,48,27,'#FAF8F3');
 s.speakerNotes.text=data[0].script;
}
{
 const s=base(2,'[10] Anthropic Institute；应用需求到研发参与为本报告的讲述思路');
 const heads=['应用更深入','研发需迭代','Agent参与研发'];
 const subs=['需要更可靠的Agent','模型 · 工具 · 行动流程','提出修改 · 运行验证'];
 heads.forEach((head,i)=>{const x=72+i*408;s.shapes.add({geometry:'rect',position:{left:x,top:302,width:320,height:150},fill:C.pale,line:{fill:'none',width:0}});tx(s,head,x+20,329,280,53,36,C.ink,true);tx(s,subs[i],x+20,397,280,39,24,C.muted);if(i<2)arrow(s,x+343,360,43);});
 tx(s,'人类设定目标与审核，Agent承担部分研发工作',72,548,1136,66,30,C.teal,true);
}
{
 const s=base(3,'主线：从已有系统出发，由Agent提出修改、运行验证，再判断保留什么');
 const subtitles=['为什么选这个行业，怎样理解RSI','Agent怎样提出并验证模型训练方法','工具怎样执行评测，程序怎样优化','Agent怎样改进自身，成果怎样进入下一轮'];
 data[2].body.forEach((t,i)=>{let y=223+i*105;tx(s,t,72,y,1136,49,31,C.teal,true);tx(s,subtitles[i],72,y+48,1136,39,25,C.ink);if(i<3)rule(s,y+93);});
}
{
 const s=base(4,'[1][10][12]；Karpathy，2026年3月；5分钟仅为训练预算，不含启动与编译');
 tx(s,'RSI · Recursive Self-Improvement · 递归自我改进',72,221,1136,48,31,C.teal,true);
 const titles=['改训练代码','训练5分钟','比较验证指标','保留或丢弃'];
 const subs=['提出一次修改','小模型实际训练','检查这次结果','决定下一次尝试'];
 titles.forEach((t,i)=>{const x=72+i*295;s.shapes.add({geometry:'rect',position:{left:x,top:309,width:251,height:144},fill:i===3?C.warm:C.pale,line:{fill:'none',width:0}});tx(s,t,x+17,335,220,46,31,C.ink,true);tx(s,subs[i],x+17,397,220,44,24,C.muted);if(i<3)arrow(s,x+260,365,28);});
 arrow(s,222,495,837,'leftArrow');tx(s,'autoresearch：实验自动继续',380,535,700,45,28,C.teal,true);
 rule(s,587);tx(s,'RSI进一步看：成果能否提高下一轮研发能力',72,615,1136,51,30,C.ink,true);
}
{
 const s=base(5,'问题贯穿后续案例；不把不同改进对象归成同一种训练');
 tx(s,'改了什么？',72,272,1136,65,44,C.teal,true);
 tx(s,'模型、研发程序，还是Agent自身',72,349,1136,50,31,C.ink);
 rule(s,433);
 tx(s,'怎么知道更好？',72,477,1136,65,44,C.teal,true);
 tx(s,'看实际任务、评测结果与代价',72,554,1136,50,31,C.ink);
}
await fs.mkdir(OUT,{recursive:true});await(await PresentationFile.exportPptx(p)).save(path.join(OUT,'opening_authored.pptx'));
console.log('OPENING09_AUTHORED');
