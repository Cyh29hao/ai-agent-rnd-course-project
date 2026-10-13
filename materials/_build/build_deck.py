# -*- coding: utf-8 -*-
"""Build V3.1 classroom deck. All diagrams are native PowerPoint shapes."""
from __future__ import annotations

import json
import re
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt
from pptx.oxml.xmlchemy import OxmlElement

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "_build" / "assets"
DATA = json.loads((ROOT / "_build" / "slide_content.json").read_text(encoding="utf-8"))
GROUP = json.loads((ROOT / "_build" / "group_config.json").read_text(encoding="utf-8"))
OUT = ROOT / "01_正式汇报.pptx"
P = Presentation()
P.slide_width, P.slide_height = Inches(13.333), Inches(7.5)
FONT = "Microsoft YaHei"
PAPER = (249, 248, 244); INK = (30, 42, 51); MUTED = (90, 103, 111)
LINE = (209, 214, 211); WHITE = (255, 255, 255); NAVY = (26, 43, 55)
ANT = (176, 77, 55); OAI = (39, 104, 91); GOOGLE = (48, 101, 154)
TONGYI = (112, 83, 154); DGM = (170, 126, 52); SOFT = (236, 238, 233)
URL = {
 "H1":"https://scienceplusplus.org/metascience/assets/Good1965.pdf",
 "H2":"https://people.idsia.ch/~juergen/gmweb4/gmweb4.html",
 "H3":"https://arxiv.org/abs/1611.01578",
 "H4":"https://sakana.ai/dgm/",
 "L1":"https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
 "L2":"https://arxiv.org/pdf/2511.10395",
 "S1":"https://www.anthropic.com/institute/recursive-self-improvement",
 "S2":"https://alignment.anthropic.com/2026/automated-alignment-researchers/",
 "S3":"https://developers.openai.com/blog/automating-repetitive-work-at-openai-with-codex",
 "S4":"https://openai.com/index/research-acceleration-view-inside-openai/",
 "S5":"https://alignment.anthropic.com/2026/automated-w2s-researcher/",
}

def col(rgb): return RGBColor(*rgb)
def slide(dark=False):
    s=P.slides.add_slide(P.slide_layouts[6]); s.background.fill.solid()
    s.background.fill.fore_color.rgb=col(NAVY if dark else PAPER)
    return s
def rect(s,x,y,w,h,fill=None,stroke=None,sw=1):
    q=s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill: q.fill.solid(); q.fill.fore_color.rgb=col(fill)
    else: q.fill.background()
    if stroke: q.line.color.rgb=col(stroke); q.line.width=Pt(sw)
    else: q.line.fill.background()
    return q
def circle(s,x,y,d,fill):
    q=s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x), Inches(y), Inches(d), Inches(d))
    q.fill.solid();q.fill.fore_color.rgb=col(fill);q.line.fill.background();return q
def text(s,value,x,y,w,h,size=20,bold=False,color=INK,align="left",valign=MSO_ANCHOR.MIDDLE):
    q=s.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    f=q.text_frame;f.clear();f.word_wrap=True;f.margin_left=f.margin_right=Inches(.015)
    f.margin_top=f.margin_bottom=0;f.vertical_anchor=valign
    for i,line in enumerate(str(value).split("\n")):
        p=f.paragraphs[0] if i==0 else f.add_paragraph();p.text=line;p.alignment={"left":PP_ALIGN.LEFT,"center":PP_ALIGN.CENTER,"right":PP_ALIGN.RIGHT}[align]
        p.font.name=FONT;p.font.size=Pt(size);p.font.bold=bold;p.font.color.rgb=col(color)
        p.space_before=p.space_after=Pt(0)
    return q
def rule(s,x,y,w,color=LINE,th=.018): rect(s,x,y,w,th,color)
def connector(s,x1,y1,x2,y2,color=INK,width=1.5):
    q=s.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,Inches(x1),Inches(y1),Inches(x2),Inches(y2))
    q.line.color.rgb=col(color);q.line.width=Pt(width)
    end=OxmlElement('a:tailEnd');end.set('type','triangle');end.set('w','sm');end.set('len','sm')
    q._element.spPr.find('{http://schemas.openxmlformats.org/drawingml/2006/main}ln').append(end)
    return q
def label(s,v,x,y,w,color=INK,size=17): text(s,v,x,y,w,.34,size,True,color)
def head(s,d,n,dark=False):
    fg=WHITE if dark else INK; mt=(181,195,199) if dark else MUTED
    text(s,f"{n:02d}  /  {('备份' if n>14 else ['问题','历史','路径','行业','尺度','Anthropic','Anthropic','Anthropic','OpenAI','OpenAI','判断','实践','实践','结论'][n-1])}",.56,.29,8,.3,12,True,mt)
    text(s,d["title"],.56,.76,12.2,.95,29 if len(d["title"])<40 else 26,True,fg)
    if d.get("subtitle"): text(s,d["subtitle"],.58,1.76,11.9,.38,16,False,mt)
    rule(s,.56,2.24,12.2,(87,105,112) if dark else LINE)
def foot(s,n,src="",dark=False):
    mt=(175,193,198) if dark else MUTED
    concise={1:'[S1] RSI概念；[S4] 研发组织',2:'[H1] §2；[H2–H4] 原始论文／发布记录',
      4:'[L1] AlphaEvolve；[H4] DGM；[L2] AgentEvolver；[S2–S4]',
      5:'本组分析框架；非官方等级。[S1–S4]',6:'[S2] §2–3、附录B；按公开方法重绘',
      7:'[S2] 附录D.4；机制示意，未披露实现不补写',
      8:'[S2] Fig.3／Fig.9；不同实验，原图见B16／B19',
      9:'[S3] Running evaluations with Codex；官方产物裁切',
      10:'[S4] §1–4；用量非效率倍数',
      11:'[L1][L2][S1–S4] 指定案例证据覆盖，不能排名',
      12:'本组实践协议；成员真实操作由本人记录',
      13:'实测记录：practice/runs/demo/score.json；原金标待人工裁定',
      14:'[S1–S4]；本组制作代理演示，成员实操待完成'}
    src=concise.get(n,src)
    rule(s,.56,7.03,12.2,(87,105,112) if dark else LINE)
    text(s,src,.57,7.09,10.98,.29,12,False,mt)
    text(s,f"{n:02d}",11.84,7.09,.78,.29,12,False,mt,"right")
def notes(s,d):
    local={"PRACTICE_PROTOCOL":"practice/protocol_baseline.md；practice/protocol_candidate.md", "PRACTICE_DEMO_SCORE":"practice/runs/demo/score.json；practice/runs/demo/public_trace_manifest.json", "PRACTICE_SMOKE_LOG":"practice/runs/smoke/；media/smoke_log_replay.mp4（日志重排）"}
    refs={**URL,**local}
    ids=[i for i in d.get("source_ids",[]) if i in refs]
    body=d.get("script","")+"\n\n完整来源：\n"+"\n".join(f"[{i}] {refs[i]}" for i in ids)
    if d.get("seconds"):body+=f"\n\n讲述预算：{d['seconds']} 秒；发言人：{d['speaker']}。"
    s.notes_slide.notes_text_frame.text=body
def source_ids_from_label(v):
    ids=set(re.findall(r"[HLS]\d",v))
    for family,a,b in re.findall(r"([HLS])(\d)[–-](?:[HLS])?(\d)",v):
        ids.update(f"{family}{i}" for i in range(int(a),int(b)+1))
    return [i for i in URL if i in ids]
def base(d,n,dark=False,src=""):
    s=slide(dark);head(s,d,n,dark);foot(s,n,src,dark);notes(s,d);return s
def image_contain(s,path,x,y,w,h):
    if not Path(path).exists():return False
    from PIL import Image
    iw,ih=Image.open(path).size; scale=min(w/iw,h/ih); nw,nh=iw*scale,ih*scale
    s.shapes.add_picture(str(path),Inches(x+(w-nw)/2),Inches(y+(h-nh)/2),Inches(nw),Inches(nh));return True
def image_crop(s,path,x,y,w,h,region):
    """Crop an unchanged source image inside an editable PowerPoint picture frame."""
    if not Path(path).exists():return False
    from PIL import Image
    iw,ih=Image.open(path).size;x0,y0,x1,y1=region
    factor=min(w/(x1-x0),h/(y1-y0))
    nw,nh=(x1-x0)*factor,(y1-y0)*factor
    q=s.shapes.add_picture(str(path),Inches(x+(w-nw)/2),Inches(y+(h-nh)/2),Inches(nw),Inches(nh))
    q.crop_left=x0/iw;q.crop_right=(iw-x1)/iw
    q.crop_top=y0/ih;q.crop_bottom=(ih-y1)/ih
    return True
def panel_line(s,x,y,w,h,color=LINE):
    rule(s,x,y,w,color);rule(s,x,y+h,w,color);rect(s,x,y,.02,h,color);rect(s,x+w-.02,y,.02,h,color)
def step(s,num,name,desc,x,y,w=2.15,color=INK):
    text(s,num,x,y,.5,.38,15,True,color);rule(s,x,y+.48,w,color,.035)
    text(s,name,x,y+.65,w,.42,21,True,color);text(s,desc,x,y+1.17,w,.8,16,False,MUTED)

# Main pages, each with its own evidence-bearing composition.
for n,d in enumerate(DATA,1):
    if n==1:
        s=slide(True);notes(s,d);rect(s,0,0,.12,7.5,ANT)
        text(s,"大模型与智能体工程实践  ·  主题一",.66,.53,9,.36,16,True,(187,207,208))
        text(s,"AI 研发 AI，\n已经做到哪一步？",.66,1.31,8.8,1.62,35,True,WHITE)
        cover_title=d["title"].replace("应用：AI", "应用：\nAI").replace("？——以", "？\n——以")
        text(s,cover_title,.69,3.13,11.22,1.90,21,True,(234,237,232))
        for i,member in enumerate(GROUP['members']):
            text(s,member['name']+'  '+member['major'],.69+(i%2)*4.35,5.45+(i//2)*.52,4.20,.42,16,False,(188,205,207))
        text(s,"讲述角色待四人确认",.69,6.65,7.5,.29,13,False,(188,205,207))
        # Explicitly bounded loop: human-set brief on the left, returned evidence on the right.
        circle(s,10.42,5.10,.56,ANT);text(s,"人定目标",9.68,5.76,2.1,.38,17,True,WHITE,"center")
        circle(s,11.66,5.10,.56,OAI);text(s,"Agent实验",10.94,5.76,2.1,.38,17,True,WHITE,"center")
        connector(s,11.01,5.38,11.62,5.38,(191,209,211),2)
        text(s,"示意：结果回到人类判断",9.51,6.46,3.5,.28,13,False,(187,207,208))
        foot(s,n,"[S1] RSI概念；[S4] 研发组织实践",True)
    elif n==2:
        s=base({**d,"title":"从机器设计机器，到可验证的研究循环"},n,src="[H1] §2  [H2] Gödel Machines  [H3] NAS  [H4] DGM；年份为原始发表／公布时间")
        years=[("1965","Good","机器设计更好的机器",ANT),("2003","Gödel Machine","修改前求形式证明",DGM),("2016","NAS","在给定指标中搜索",GOOGLE),("2025","DGM","改Agent代码并测试",OAI)]
        rule(s,.86,4.04,11.55,LINE,.04)
        for i,(yr,name,desc,c) in enumerate(years):
            x=.84+i*3.07;circle(s,x,3.86,.38,c)
            text(s,yr,x-.02,2.74,2.45,.52,28,True,c);text(s,name,x-.02,3.27,2.55,.42,19,True)
            text(s,desc,x-.02,4.35,2.66,1.03,18)
        text(s,"思想构想",.84,5.94,2.3,.36,16,True,ANT)
        text(s,"理论与受限搜索",4.0,5.94,4.1,.36,16,True,DGM)
        text(s,"经验验证的系统改动",9.98,5.94,2.5,.42,16,True,OAI)
        text(s,"选题动机：研发试错耗资源，自动改进需要可信反馈",.84,6.53,11.5,.36,18,True,INK)
    elif n==3:
        s=base(d,n)
        phases=[("01","行业里改什么","问题与范围"),("02","两家公司如何做","机制与产物"),("03","证据走到哪","共同尺度"),("04","我们如何试","真实记录")]
        for i,(a,b,c) in enumerate(phases):step(s,a,b,c,.78+i*3.13,2.88,2.7,[ANT,GOOGLE,OAI,TONGYI][i])
        text(s,"做了什么？       如何证明？       边界在哪？",1.32,5.85,10.7,.62,25,True,INK,"center")
    elif n==4:
        s=base(d,n,src="[L1] AlphaEvolve  [H4] DGM  [L2] AgentEvolver  [S2] AAR  [S3–S4] Codex与研发组织")
        groups=[("算法／训练效率","Google AlphaEvolve","Gemini提程序 → 评测筛选",GOOGLE),
                ("Agent系统","Sakana／UBC DGM","自改代码与工作流 → 任务评测",DGM),
                ("Agent训练框架","通义 AgentEvolver","任务生成、经验复用、反馈归因",TONGYI),
                ("模型后训练","Anthropic","研究提案 → 训练权重",ANT),
                ("研发工作流","OpenAI","Runme评测产物与人审",OAI)]
        for i,(k,name,desc,c) in enumerate(groups):
            y=2.55+i*.77;rect(s,.75,y,.09,.55,c);text(s,k,1.02,y,2.3,.55,18,True,c)
            text(s,name,3.34,y,3.28,.55,19,True);text(s,desc,6.60,y,6.1,.55,17)
            if i<4:rule(s,.75,y+.68,11.85)
        text(s,"选例：模型实验可追踪 × 研发现场可复查；开放性分看权重与框架代码",.78,6.62,11.8,.38,16,True,MUTED)
    elif n==5:
        s=base(d,n,src="本组分析框架，非官方等级；案例定位据[S1–S4]")
        names=["选题／假设","数据","训练／设施","评测分析","发布"]
        for i,v in enumerate(names):
            x=.7+i*2.53;text(s,f"0{i+1}",x,2.68,.55,.37,14,True,ANT)
            text(s,v,x,3.14,2.4,.46,20,True);rule(s,x,3.72,2.15,ANT,.05)
            if i<4:connector(s,x+2.2,3.73,x+2.47,3.73,ANT,2)
        text(s,"证据位置",.72,4.35,2.2,.36,16,True,MUTED)
        levels=["辅助执行","闭环实验","局部模型改进","持续后继研发"]
        for i,v in enumerate(levels):
            x=.72+i*3.12;rect(s,x,4.94,2.9,.08,[GOOGLE,OAI,ANT,INK][i]);text(s,v,x,5.19,2.92,.62,19,True)
        text(s,"改动对象：工作流／训练数据与方法／模型参数",.72,6.15,8.4,.42,17)
        text(s,"人类批准权另记",10.06,6.15,2.5,.42,17,True,ANT)
    elif n==6:
        s=base({**d,"subtitle":"主实验：Opus 4.8研究Agent → 开放小模型目标"},n,src="依据[S2] §2–3、附录B重绘；官方原图见备份，流程形状可编辑")
        chain=[("研究Agent","mini-paper\n训练代码",ANT),("代码监控","规则检查\n接受／拒绝",DGM),
               ("训练工具","小模型权重\n检查点",OAI),("隔离评测","安全分数\n能力门槛",GOOGLE)]
        for i,(name,artifact,c) in enumerate(chain):
            x=.76+i*3.12;rect(s,x,2.74,2.64,.07,c)
            text(s,name,x,2.99,2.64,.48,20,True,c)
            text(s,artifact,x,3.54,2.55,.91,18)
            if i<3:connector(s,x+2.67,3.75,x+3.04,3.75,c,2.5)
        # Evaluation boundary and visible return path.
        panel_line(s,9.97,2.56,2.96,2.25,GOOGLE)
        text(s,"隐藏评测数据",10.2,4.45,2.45,.29,13,True,GOOGLE)
        connector(s,11.30,4.86,11.30,5.28,GOOGLE,2)
        rect(s,2.31,5.29,9.35,.73,SOFT)
        text(s,"共享状态：论坛／榜单／失败记录",2.57,5.41,8.8,.44,20,True,OAI)
        connector(s,2.27,5.65,1.10,5.65,OAI,2)
        connector(s,1.10,5.65,1.10,4.70,OAI,2)
        text(s,"反馈进入下一轮新会话；目标、预算与验收规则仍由人设定",.78,6.41,11.8,.44,17,True,MUTED)
    elif n==7:
        s=base(d,n,src="[S2] 附录D.4；方向与分布是机制示意，具体实现须以论文为准")
        text(s,"输入：指定谄媚任务（目标 Qwen3.5-2B）＋可用训练数据",.77,2.64,11.7,.5,20,True)
        rule(s,.81,3.42,11.63,LINE,.035)
        parts=[("目标模型的\n激活引导变体",.78,2.59,ANT),
               ("较少迎合的\n教师输出分布",3.84,2.68,ANT),
               ("KL训练目标",7.08,2.30,OAI),
               ("未引导学生",9.94,2.53,OAI)]
        for i,(v,x,w,c) in enumerate(parts):
            text(s,v,x,3.78,w,1.02,20,True,c)
            if i<3:connector(s,x+w+.02,4.27,parts[i+1][1]-.10,4.27,c,2)
        rule(s,.81,5.15,11.56,LINE,.035)
        text(s,"交付物：训练后的学生权重",.82,5.41,6.6,.56,22,True,OAI)
        text(s,"机制示意；原文未在所引段落披露激活方向与KL实现顺序",.82,6.27,11.7,.43,17)
    elif n==8:
        s=base(d,n,src="[S2] Fig.3原图标注79%/26%；Fig.9另项实验65%/72%；两者不合并；原图见B16/B19")
        text(s,"主实验｜十类指定失效",.77,2.59,6.3,.44,21,True,ANT)
        text(s,"Fig.3：各项爬坡基准的改善空间",.77,3.21,5.92,.42,17,True,MUTED)
        for i,(a,v,c) in enumerate([("提示注入","79%",GOOGLE),("谄媚","26%",ANT)]):
            y=3.94+i*.87;text(s,a,.79,y,1.73,.47,18,True)
            rect(s,2.45,y+.08,3.72,.35,SOFT)
            rect(s,2.45,y+.08,3.72*int(v[:-1])/100,.35,c)
            text(s,v,6.27,y,1.0,.46,19,True,c)
        text(s,"十项均改善，但幅度不同；全图见 B16",.79,5.93,6.08,.58,17)
        rect(s,7.30,2.63,.02,3.95,LINE)
        text(s,"另项探索｜生产级早期检查点",7.65,2.63,4.62,.72,20,True,ANT)
        text(s,"Sonnet 5研究Agent →\n早期Opus 4.8检查点",7.65,3.39,4.65,.85,18,True)
        text(s,"权限：仅构造后训练数据",7.65,4.31,4.65,.41,16,True,ANT)
        text(s,"Fig.9：AAR 65%  /  已发布模型 72%",7.65,4.91,4.68,.63,18,True)
        text(s,"十维Petri覆盖加权改善空间\n几何分数，不是安全通过率",7.65,5.64,4.67,.78,16)
    elif n==9:
        s=base(d,n,src="[S3] Running evaluations with Codex；官方Runme截图来源同链接")
        runme=ROOT/"_build"/"assets"/"runme_completed.png"
        if image_crop(s,runme,.7,2.56,7.25,1.65,(70,145,970,351)):
            image_crop(s,runme,.7,4.38,7.25,1.69,(70,375,1030,604))
            panel_line(s,.7,2.56,7.25,3.51)
            text(s,"上：任务目标与人审要求    下：重跑计划与已复查证据",.77,6.32,7.08,.34,14,True,MUTED)
        else:
            panel_line(s,.7,2.58,7.25,3.88);text(s,"官方Runme截图待接入",1.22,3.85,6.2,.55,25,True,MUTED,"center")
            text(s,"来源与解读见右侧；截图空缺不构成产物证据",1.2,4.55,6.3,.48,15,False,MUTED,"center")
        items=[("目标","工程师写目标"),("计划","Codex拟计划，人审"),("执行","工具运行，保留输出"),("记录","结果与取舍回到笔记本")]
        for i,(a,b) in enumerate(items):
            y=2.7+i*.9;text(s,a,8.45,y,1.03,.46,19,True,OAI);text(s,b,9.5,y,3.04,.57,17)
            if i<3:rule(s,8.45,y+.68,3.95)
        text(s,"截图只显示目标与计划片段；完整原图见B17",8.44,6.37,4.13,.57,15,True,OAI)
    elif n==10:
        s=base(d,n,src="[S4] §1–4；3.1为Agent运行时间换算用量，非效率倍数")
        text(s,"3.1",.78,2.63,4.2,1.35,61,True,OAI)
        text(s,"Agent工作日 / 人类工作日",.81,4.08,5.4,.53,21,True)
        text(s,"2026年8月中旬；Agent总运行时间按8小时折算",.83,4.76,5.37,.73,17,False,MUTED)
        rect(s,6.5,2.55,.02,3.85,LINE)
        events=[("7月20日","发现Agent侵入研究基础设施"),("其后","暂停部分拟发布模型RL"),("加固后","部分工作恢复")]
        for i,(a,b) in enumerate(events):
            y=2.72+i*1.17;circle(s,6.93,y+.10,.19,ANT);text(s,a,7.33,y,1.65,.42,17,True,ANT);text(s,b,8.91,y,3.4,.58,18)
            if i<2:rect(s,7.01,y+.33,.025,.91,ANT)
        text(s,"内部观察：证明采用与治理问题，不证明净效率因果",.81,6.4,11.66,.51,19,True)
    elif n==11:
        s=base({**d,"subtitle":"证据覆盖表：只对应列出的任务，不是公司能力排名"},n,src="本组按[L1][L2][S1–S4]定位特定实践；不同指标不排名；● 有公开证据")
        stages=["辅助执行","闭环实验","局部模型改进","持续后继研发"]
        cx=[4.70,6.71,8.72,10.73]
        for i,v in enumerate(stages):
            x=cx[i]-.95;rect(s,x,2.78,1.9,.09,[GOOGLE,OAI,ANT,INK][i]);text(s,v,x-.14,3.02,2.18,.58,16,True,INK,"center")
        rows=[("Google",GOOGLE,"算法／训练",[0,1]),("通义",TONGYI,"Agent策略",[0,1,2]),
              ("Anthropic",ANT,"模型权重",[0,1,2]),("OpenAI",OAI,"评测流程",[0,1])]
        for i,(name,c,obj,marks) in enumerate(rows):
            y=3.82+i*.61;text(s,name,.78,y,1.49,.43,17,True,c)
            text(s,obj,2.18,y,1.51,.44,16,False,MUTED)
            rule(s,3.67,y+.48,8.75)
            for j in marks:circle(s,cx[j]-.11,y+.13,.22,c)
            if 2 in marks:text(s,"受限",9.02,y-.01,.69,.35,12,True,c)
        text(s,"通义为Agent策略参数；Anthropic为指定模型后训练。均未证明完整后继研发",.77,6.50,11.75,.42,16,True,MUTED)
    elif n==12:
        s=base(d,n,src="本组实践协议；四位成员完成状态须由本人操作记录确认")
        sequence=[("输入","主张＋来源包"),("工具","读取／复查"),("校验","JSON结构"),("输出","标签、出处、限制、改写")]
        for i,(a,b) in enumerate(sequence):
            x=.74+i*3.07;step(s,f"0{i+1}",a,b,x,2.75,2.65,[ANT,GOOGLE,OAI,TONGYI][i])
        text(s,"责任预分配",.76,5.19,2.3,.36,16,True,MUTED)
        text(s,"A 来源  ·  B 基线  ·  C 独立测试  ·  D 错误整理",.76,5.62,11.8,.55,21,True)
        text(s,"运行身份：制作代理试运行；四人实际操作待核实",.77,6.47,11.7,.45,17,True,ANT)
    elif n==13:
        s=base(d,n,src="本组单批演示：practice/runs/demo/score.json；作者金标可见、出处与金标待人工复核")
        video=ROOT/"media"/"smoke_log_replay.mp4"
        poster=ROOT/"media"/"smoke_log_replay_01.png"
        if video.exists() and poster.exists():
            s.shapes.add_movie(str(video),Inches(.74),Inches(2.64),Inches(6.35),Inches(3.57),poster_frame_image=str(poster),mime_type="video/mp4")
            text(s,"制作代理公开动作日志重排｜18秒；非UI录像",.76,6.26,6.35,.37,13,True,MUTED)
        else:
            panel_line(s,.74,2.64,6.35,3.77);text(s,"真实日志重排 / 静态关键帧待接入",1.03,3.38,5.77,.74,24,True,MUTED,"center")
        text(s,"16条演示题｜原始金标一致",7.54,2.70,4.67,.48,17,True)
        text(s,"基线",7.54,3.35,1.42,.43,18,True,OAI);text(s,"13 / 16",9.05,3.27,3.1,.61,28,True,OAI)
        rule(s,7.52,4.00,4.8)
        text(s,"候选",7.54,4.21,1.42,.43,18,True,ANT);text(s,"12 / 16",9.05,4.15,3.1,.61,28,True,ANT)
        text(s,"误放行：两组均 0 / 8",7.54,4.95,4.67,.44,18,True)
        rule(s,7.52,5.54,4.8)
        text(s,"T06：候选判 contradicted；作者金标 overstated；类别规则冲突待人工裁定",7.54,5.66,4.70,.88,15,True,ANT)
        text(s,"金标对作者可见；非独立盲核；不能推断泛化",7.52,6.61,4.84,.30,13,False,MUTED)
    elif n==14:
        s=slide(True);notes(s,d);head(s,d,n,True);foot(s,n,"[S1–S4] 公开证据范围内；本组演示见practice/runs/demo/score.json，金标待核",True)
        text(s,"已看到",.79,2.76,2.5,.49,18,True,(181,207,204))
        text(s,"研发执行  →  受限闭环  →  局部模型改进",.79,3.36,11.8,.67,27,True,WHITE)
        rule(s,.79,4.34,11.59,(94,113,119),.03)
        text(s,"尚未由公开材料证明",.8,4.77,5.4,.48,18,True,(244,177,152))
        text(s,"持续自主地开发、验证并迭代下一代模型",.79,5.35,11.8,.71,27,True,WHITE)
        text(s,"小组演示：13/16 → 12/16；原始金标、非盲核，仍需人工仲裁",.8,6.39,11.8,.52,17,False,(181,207,204))

# Technical appendix: separate experiments, measurement, implementation boundaries,
# industry alternatives, curriculum connections, and honest practice status.
BACKUP=[
 ("B01  四类证据与治理轴", "能力状态描述可观察结果；人类批准权另记", ["辅助执行：按人定目标完成环节","闭环实验：提案、工具、反馈、再试","局部模型改进：训练权重并经指定验证","持续后继研发：自主形成并验证下一代循环"],"[S1–S4] 本组分析框架"),
 ("B02  Anthropic的两类实验", "主实验与生产级早期检查点探索分开", ["主实验：Opus 4.8研究Agent、开放小模型、十类指定失效","另项探索：Sonnet 5研究Agent、早期Opus 4.8检查点","后者仅有构造后训练数据权限；评测口径不同","不能把两项样本、效果、百分比拼接"],"[S2] §2–3、§5–6"),
 ("B03  谄媚方法：已公开与仅示意", "教师、学生、交付物可确认；激活方向细节以原文为准", ["获胜法教师：目标模型经激活引导形成的分布","学生：未引导目标模型；KL目标学习教师分布","受限KL分支才明确可用冻结副本，且禁激活引导","训练交付物：更新后的学生模型权重"],"[S2] 附录D.4"),
 ("B04  前150次与全程结果", "消融读数来自不同观察窗口，分开报告", ["前150次（Fig.20）：23.3 / 6.0 / 2.9，按论文图例读","全程峰值：26.4 / 18.7 / 6.0 / 4.5","前者用于比较早期搜索方法；后者是各设置更长运行中的峰值","均不代表独立复现实验或总体安全百分比"],"[S2] 附录D.4 Fig.20"),
 ("B05  KL方向与自蒸馏", "图中箭头是机制示意，不给未披露的工程细节", ["概念目标：学生输出分布向教师分布靠近","论文未在所引段落明确实现的KL参数顺序","自蒸馏：训练信号由模型的激活引导版本产生","仅监督微调与允许KL目标的消融不可混成同法"],"[S2] 附录D.4；示意口径"),
 ("B06  Fig.9：65%与72%怎么算", "覆盖加权的安全改善空间几何分数，不是通过率", ["先定义每项从基线到理想值的可改善空间","改善维度覆盖率乘这些维度的改善空间几何均值","65%／72%属于指定设置与评测口径","不得读成“模型65%安全”或“所有任务通过72%”"],"[S2] Fig.9、§6、附录E.1"),
 ("B07  评测隔离与作弊", "研究Agent看反馈，但留出数据与能力门槛隔离", ["监控训练代码是否违反规则","隔离评测器保留隐藏的安全与能力检查","开放式行为审查补充定量评分","高分仍需排查奖励黑客、选择偏差与迁移失败"],"[S2] §3–5、附录；[S5] 评测投机"),
 ("B08  Runme的公开产物", "目标、计划、人审、执行记录和判断能被下次复用", ["工程师先写目标与可用背景","Codex提出计划；人审核与选择资源","命令输出、结果解释、分岔取舍回写笔记本","这证明工作流产物，未证明参数自动改进"],"[S3] Running evaluations with Codex"),
 ("B09  OpenAI使用量与事件线", "3.1工作日是运行用量；两个安全事件须分开", ["2026年8月中旬：约3.1 Agent工作日／人类工作日","7月20日发现Agent侵入研究基础设施，部分拟发布模型RL暂停","8月7日Astra相关额外限制：独立事件，不并入前一事件","内部观察不能推出净效率因果"],"[S4] §1–4"),
 ("B10  Google：局部23%与总体1%", "AlphaEvolve对具体内核的收益不能替代总训练收益", ["Gemini提程序；自动评测与演化筛选","特定矩阵乘法内核：23%局部加速","总训练时间：约1%缩短，口径与分母不同","算法改进仍需人定评测与系统级验证"],"[L1] AlphaEvolve 官方博客"),
 ("B11  通义AgentEvolver", "开放的是Agent训练框架及代码，策略通过GRPO更新", ["任务生成、经验复用、反馈归因","论文§7.1.3明确用GRPO训练Agent策略参数","开放框架与底层模型权重开放分别判断","未证明自主研发完整下一代基础模型"],"[L2] §7.1.3与ModelScope仓库"),
 ("B12  研究系统与产品工作流", "证据类型不同，比较时先核改动对象", ["Anthropic：受控研究实验；受限模型后训练","OpenAI：生产研发工作产物、组织内部观察","Google：可评估算法与训练基础设施","通义：公开Agent训练方法与框架"],"[S2–S4][L1][L2]"),
 ("B13  小组试运行的可说范围", "制作代理产物与成员实践、独立测试分开", ["演示题16条：基线13/16，预注册候选12/16","误放行两组均0/8；原始作者金标有争议","金标对制作作者可见，非独立或人工盲核","四位成员实际操作待本人留痕；只比较审查提示"],"本组practice/runs/demo/score.json；待人工复核"),
 ("B14  课程概念对应哪一环", "工具、记忆、多Agent与Harness都对应可见工程接口", ["工具：文献、代码、训练、评测执行","记忆：Runme、论坛、榜单与持久文件","多Agent：研究代理与独立评测／监控","Harness：权限、预算、输出格式与失败回写"],"[S2][S3]；本组课程对照"),
 ("B15  历史路线不是同一种机器", "思想、理论、受限搜索与LLM研究Agent分别标记", ["Good 1965：思想问题","Gödel Machine 2003：形式证明构造","NAS 2016：人定空间和指标里的结构搜索","DGM 2025：代码自修改并以任务结果筛选"],"[H1–H4]"),
 ("B16  主实验十类结果原图", "原始Fig.3完整呈现；主讲第8页只重绘其中两项", ["纵轴：各指定安全失效的爬坡基准改善空间","横轴：每项方法提出的顺序","选中的两项：提示注入79%、谄媚26%","此图不含生产级检查点的65%／72%"],"[S2] Fig.3"),
 ("B17  Runme官方产物原图", "完整截图保留上下文；主讲第9页为局部裁切", ["目标要求复查前次记录并拟重跑计划","要求计划先经人审，再执行","要求命令与输出、解释留在笔记本","完整图对照主讲局部图，不补入未出现界面"],"[S3] Running evaluations with Codex"),
 ("B18  Anthropic研究循环动画", "据公开方法重绘的10秒流程动画；不是公司内部录像", ["提案与训练代码","监控规则后运行训练","隔离评测并记录反馈","共享状态供下一轮新会话读取"],"[S2] §2–3；本组示意动画"),
 ("B19  生产级检查点原图", "Fig.9：65%与72%属同一指定十维Petri评价", ["研究代理只构造数据，工具对早期检查点进行后训练","图中65%为选出方法的改善空间覆盖分数","72%为已发布模型的对照参照","不是主实验Fig.3，亦非通用安全通过率"],"[S2] Fig.9、§6"),
 ("B20  Fig.3上半幅放大", "主实验五项：提示注入、隐瞒不确定性、寻求权力、谄媚、欺瞒", ["原始论文图的上半幅裁切，不改动曲线","每项横轴为该失效下方法提出顺序","纵轴为该失效的爬坡基准改善空间","完整十项原图见B16"],"[S2] Fig.3"),
 ("B21  Fig.3下半幅放大", "主实验另五项：越狱、隐私、幻觉、奖励取巧、社会偏见", ["原始论文图的下半幅裁切，不改动曲线","受测十项改善幅度不同","图上的灰点与叉号均保留原图图例解释","完整十项原图见B16"],"[S2] Fig.3"),
]
for k,(title_,sub,items,source) in enumerate(BACKUP,15):
    d={"title":title_,"subtitle":sub,"script":title_+"。"+"；".join(items),"source_ids":source_ids_from_label(source)}
    s=base(d,k,src=source)
    specialized=title_[:3] in {'B04','B06','B07','B09','B10','B11'}
    for i,item in enumerate([] if specialized else items):
        y=2.61+i*.9;rect(s,.77,y,.08,.6,[ANT,GOOGLE,OAI,TONGYI][i])
        text(s,item,1.02,y,11.45,.65,21 if len(item)<31 else 19,i==0)
        if i<3:rule(s,.78,y+.75,11.77)
    if title_.startswith('B04'):
        text(s,'前150个已评分方法',.80,2.67,5.70,.48,23,True,ANT)
        text(s,'各分支全程峰值',7.15,2.67,5.17,.48,23,True,GOOGLE)
        rect(s,6.70,2.65,.02,3.70,LINE)
        branches=[('不受限',23.3,26.4),('公开数据SFT',6.0,6.0),('自由数据SFT',2.9,4.5)]
        for i,(name,fixed,full) in enumerate(branches):
            y=3.45+i*.75;text(s,name,.80,y,2.16,.42,16,True)
            rect(s,3.07,y+.10,2.63*fixed/30,.22,ANT)
            text(s,f'{fixed:.1f}%',5.35,y,.99,.43,18,True,ANT)
        for i,(name,value) in enumerate([('不受限',26.4),('SFT＋KL',18.7),('公开数据SFT',6.0),('自由数据SFT',4.5)]):
            y=3.39+i*.57;text(s,name,7.15,y,2.13,.41,16,True)
            rect(s,9.30,y+.10,2.20*value/30,.20,GOOGLE)
            text(s,f'{value:.1f}%',11.55,y,1.06,.41,17,True,GOOGLE)
        text(s,'固定预算比较仅列原文已明示的三个端点；未猜测KL端点',.80,6.30,11.7,.40,16,True,MUTED)
        text(s,'同一谄媚任务；全程搜索长度不同，两组不能拼成同一次等预算比较',.80,6.66,11.7,.29,14,False,MUTED)
    if title_.startswith('B06'):
        stages=[('每维度','相对各自基线\n计算改善空间'),('取改善维度','有正向改善的维度\n占所测十维的比例'),('聚合','这些维度改善空间\n取几何均值')]
        for i,(name,detail) in enumerate(stages):
            x=.82+i*4.12;rule(s,x,2.87,3.57,ANT,.06)
            text(s,name,x,3.13,3.57,.50,23,True)
            text(s,detail,x,3.76,3.57,.93,18)
            if i<2:connector(s,x+3.59,4.18,x+4.01,4.18,ANT,2)
        text(s,'覆盖比例 × 改善维度的改善空间几何均值',.85,5.35,11.55,.60,26,True,OAI,'center')
        text(s,'Fig.9：方法65%，发布版参照72%；只对应所测Petri十维',.84,6.25,11.63,.46,18,True)
    if title_.startswith('B07'):
        text(s,'研究Agent可见',.82,2.67,5.18,.45,22,True,ANT)
        text(s,'隔离评测与监控',7.23,2.67,5.12,.45,22,True,GOOGLE)
        rect(s,6.59,2.69,.035,3.46,LINE)
        text(s,'训练代码与权重\n方法评分反馈\n论坛／榜单',.86,3.40,5.03,1.58,22)
        text(s,'隐藏评测题例\n能力退化门槛\n代码违规与事后取巧审查',7.26,3.40,5.16,1.58,21)
        connector(s,5.82,3.67,7.06,3.67,ANT,2)
        connector(s,7.05,4.54,5.83,4.54,GOOGLE,2)
        text(s,'送交候选',5.56,3.06,1.79,.37,13,True,MUTED,'center')
        text(s,'返回分数',5.56,4.85,1.79,.37,13,True,MUTED,'center')
        text(s,'39 / 1601 条轨迹被确认取巧；子类26、10、8可重叠',.85,5.73,11.52,.61,23,True,ANT)
        text(s,'监控减少风险；高分与通过能力闸门都不等于全面安全或能力零损失',.85,6.59,11.65,.35,16,False,MUTED)
    if title_.startswith('B09'):
        events=[('7月20日','Agent侵入研究设施','暂关训练容器；\n加限制后恢复'),('约两周','拟部署模型的RL暂停','同时测试安全加固；\n不是全部研究停摆'),('8月7日','Astra专属限制','因能力风险初步证据；\n与7月事件分开')]
        for i,(date,name,detail) in enumerate(events):
            x=.86+i*4.12;circle(s,x,3.08,.25,ANT)
            text(s,date,x,2.62,3.64,.41,21,True,ANT)
            text(s,name,x,3.69,3.64,.59,21,True)
            text(s,detail,x,4.45,3.64,.98,18)
            if i<2:connector(s,x+.31,3.20,x+3.96,3.20,LINE,2)
        text(s,'8月中旬：3.1 Agent工作日／人类工作日，是总运行量换算',.86,5.93,11.66,.62,23,True,OAI)
        text(s,'事件、采用量与效率因果分别核对，不能合并成一个提效倍数',.86,6.66,11.66,.30,15,False,MUTED)
    if title_.startswith('B10'):
        cycle=[('Gemini','提出候选程序'),('自动评测','检验功能与评分'),('演化数据库','选择下一轮候选')]
        for i,(name,detail) in enumerate(cycle):
            x=.85+i*4.12;rule(s,x,2.74,3.61,GOOGLE,.07)
            text(s,name,x,3.02,3.61,.48,23,True,GOOGLE)
            text(s,detail,x,3.72,3.61,.51,19)
            if i<2:connector(s,x+3.65,3.94,x+4.03,3.94,GOOGLE,2)
        text(s,'特定矩阵乘法内核',.86,4.83,5.40,.45,19,True)
        text(s,'23%局部加速',.86,5.41,5.48,.76,35,True,GOOGLE)
        text(s,'Gemini整体训练时间',7.13,4.83,5.35,.45,19,True)
        text(s,'约1%缩短',7.13,5.41,5.40,.76,35,True,OAI)
        connector(s,5.72,5.77,6.85,5.77,MUTED,2)
        text(s,'系统收益受其他环节限制；算法优化没有证明整代模型自主研发',.86,6.61,11.62,.34,16,False,MUTED)
    if title_.startswith('B11'):
        flow=[('任务生成','self-questioning'),('经验复用','self-navigating'),('反馈归因','self-attributing'),('策略训练','GRPO参数更新')]
        for i,(name,detail) in enumerate(flow):
            x=.80+i*3.14;rule(s,x,3.07,2.66,TONGYI,.07)
            text(s,name,x,3.40,2.66,.57,23,True,TONGYI)
            text(s,detail,x,4.18,2.71,.72,16)
            if i<3:connector(s,x+2.70,4.35,x+3.04,4.35,TONGYI,2)
        text(s,'改变Agent策略参数；方法由论文与开放框架支持',.83,5.63,11.59,.61,25,True)
        text(s,'代码开放、权重开放分别看；未证明系统自主开发完整后继基础模型',.83,6.47,11.66,.42,17,False,MUTED)
    if k==30:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        image_contain(s,ROOT/"_build"/"assets"/"anthropic_fig3.png",.86,2.65,11.55,3.84)
        rect(s,.72,6.60,11.9,.34,PAPER)
        text(s,"论文原图 [S2] Fig.3；主讲图为其中两项的可编辑重绘",.78,6.56,11.6,.42,15,True,MUTED)
    if k==31:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        image_contain(s,ROOT/"_build"/"assets"/"runme_completed.png",.86,2.60,11.47,4.24)
    if k==32:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        video=ROOT/"media"/"anthropic_cycle.mp4"
        poster=ROOT/"media"/"anthropic_cycle_01.png"
        if video.exists() and poster.exists():
            s.shapes.add_movie(str(video),Inches(2.38),Inches(2.56),Inches(8.57),Inches(4.37),poster_frame_image=str(poster),mime_type="video/mp4")
    if k==33:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        image_contain(s,ASSETS/"anthropic_aar_checkpoint.png",.84,2.63,11.61,4.18)
    if k==34:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        image_crop(s,ROOT/"_build"/"assets"/"anthropic_fig3.png",.86,3.00,11.61,3.52,(105,310,1999,825))
        text(s,"纵轴：该失效的安全改善空间（%）   横轴：研究方法提出顺序",.86,2.56,11.61,.38,16,True,MUTED)
        text(s,"原图图例：红线累计最佳；红点全程最佳；灰点候选；叉号能力下降而淘汰",.86,6.56,11.61,.38,14,False,MUTED)
    if k==35:
        rect(s,.72,2.53,11.9,4.48,PAPER)
        image_crop(s,ROOT/"_build"/"assets"/"anthropic_fig3.png",.86,3.00,11.61,3.52,(105,930,1999,1440))
        text(s,"纵轴：该失效的安全改善空间（%）   横轴：研究方法提出顺序",.86,2.56,11.61,.38,16,True,MUTED)
        text(s,"原图图例：红线累计最佳；红点全程最佳；灰点候选；叉号能力下降而淘汰",.86,6.56,11.61,.38,14,False,MUTED)

assert len(DATA)==14 and sum(x['seconds'] for x in DATA)==550
assert len(P.slides)==14+len(BACKUP)
for s in P.slides:
    for shape in s.shapes:
        style=shape._element.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
        if style is not None:
            effect=style.find('{http://schemas.openxmlformats.org/drawingml/2006/main}effectRef')
            if effect is not None: effect.set('idx','0')
P.save(OUT)
print(f"slides={len(P.slides)} main=14 seconds=550 output={OUT}")
