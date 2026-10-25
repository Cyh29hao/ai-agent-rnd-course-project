// Reuse the approved V5 typography and editable scientific diagrams.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const OUT=path.join(ROOT,'_build/d_refinement_06');
const data=JSON.parse(await fs.readFile(path.join(ROOT,'主讲内容.json'),'utf8'));
const C={bg:'#FAF8F3',ink:'#1E3544',teal:'#167F78',rust:'#B65D3E',muted:'#667680',rule:'#D5D9D5',pale:'#E7EFEB'};
const p=Presentation.create({slideSize:{width:1280,height:720}});
function tx(s,t,x,y,w,h,size=30,color=C.ink,bold=false){const o=s.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:'Microsoft YaHei',fontSize:size,color,bold};o.text.insets=0;return o;}
function rule(s,y){s.shapes.add({geometry:'rect',position:{left:72,top:y,width:1136,height:2},fill:C.rule,line:{fill:'none',width:0}});}
function block(s,t,x,y,w,h){const o=s.shapes.add({geometry:'rect',position:{left:x,top:y,width:w,height:h},fill:C.pale,line:{fill:'none',width:0}});o.text=t;o.text.style={typeface:'Microsoft YaHei',fontSize:30,color:C.ink};o.text.insets=18;return o;}
function arrow(s,x,y,w,color=C.teal,dir='rightArrow'){s.shapes.add({geometry:dir,position:{left:x,top:y,width:w,height:24},fill:color,line:{fill:'none',width:0}});}
function base(n,footer){const d=data[n-1],s=p.slides.add();s.background.fill=C.bg;tx(s,d.section,72,30,1136,33,20,C.teal,true);tx(s,d.title,72,90,1136,98,46,C.ink,true);rule(s,190);tx(s,footer,72,676,1070,32,17,C.muted);tx(s,String(n),1166,676,44,32,18,C.muted);s.speakerNotes.text=d.script;return s;}
{
 const s=base(19,'[7] AgentEvolver v1, §3—5；[8] DGM, Introduction；[11] 代码库');
 tx(s,'通义 AgentEvolver',72,231,540,62,37,C.teal,true);
 tx(s,'任务生成 · 经验复用',72,326,540,54,31);
 tx(s,'奖励指导策略训练',72,405,540,60,35,C.teal,true);
 tx(s,'更新负责行动选择的模型参数',72,486,540,50,25,C.muted);
 tx(s,'Sakana DGM',696,231,512,62,37,C.rust,true);
 tx(s,'修改工具和流程代码',696,326,512,54,31);
 tx(s,'评测后从版本档案继续探索',696,405,512,94,31,C.rust,true);
 tx(s,'此实验固定底层模型',696,506,512,43,25,C.muted);
 rule(s,563);tx(s,'改策略与改代码，改进发生的位置不同',72,595,1136,58,33);
}
{
 const s=base(21,'[4] AAR；[5] Codex评测；[8] DGM；[10] RSI分析');
 block(s,'研究Agent\n提方法、跑实验',72,247,290,126);arrow(s,389,298,70);
 block(s,'这一轮的成果\n模型、算法或代码',487,247,300,126);arrow(s,815,298,70);block(s,'检查效果\n保存方法与结果',913,247,295,126);
 tx(s,'记录留下来，下一轮接着试',72,401,1136,49,32,C.teal,true);arrow(s,165,466,960,C.pale,'leftArrow');
 tx(s,'DGM：修改后的Agent继续探索',72,520,1136,53,32,C.rust,true);arrow(s,165,584,960,C.rust,'leftArrow');
 tx(s,'基础模型后继研发，需要继续跟踪多轮结果',72,625,1136,39,27,C.ink,true);
}
{
 const s=base(22,'比较思路为本报告分析，尚未执行实验；[8] DGM；[10] RSI分析');
 const titles=['换任务','同预算','连续多轮'];
 data[21].body.forEach((t,i)=>{tx(s,titles[i],72,240+i*119,170,77,35,C.rust,true);tx(s,t,288,247+i*119,920,85,35);});
 tx(s,'记录时间、计算成本和人工帮助，保留失败尝试',72,625,1136,42,25,C.muted);
}
{
 const s=base(23,'[4] AAR；[5] Codex评测；[6] AlphaEvolve；[7] AgentEvolver；[8] DGM；[10] RSI分析');
 tx(s,data[22].body[0],72,243,1136,85,46,C.teal,true);
 tx(s,data[22].body[1],72,350,1136,75,32);
 rule(s,463);tx(s,data[22].body[2],72,517,1136,122,39,C.rust,true);
}
await fs.mkdir(OUT,{recursive:true});
await (await PresentationFile.exportPptx(p)).save(path.join(OUT,'d_authored.pptx'));
console.log('D_AUTHORED_4_EDITABLE_SLIDES');
