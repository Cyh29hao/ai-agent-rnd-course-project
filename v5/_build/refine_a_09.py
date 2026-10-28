"""Clarify the course application story and synchronize the part navigation."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'主讲内容.json';before=json.loads(p.read_text(encoding='utf-8'))
nav=['一  选题与主线','二  Anthropic：模型训练','三  OpenAI与Google：研发流程与程序优化','四  Agent自我改进与下一轮研发']
updates=[
dict(title='智能体在AI研发中的应用',seconds=25,body=['从改进模型与工具，到改进Agent自身','主题一：行业应用案例研究'],sources=[10],
script='从聊天问答到调用工具完成任务，Agent正进入更多应用。要让它们更好用，模型、工具和行动流程都得继续改进。过去主要由人做的研发，今天也开始交给Agent。我们选的行业就是AI研发：看Agent怎样在人类设定目标和审核下，参与改进模型与Agent自身。',
note='采用用户的课程应用案例视角。不是宣称chatbot已消失，或所有Agent研发都等同RSI；研究对象兼有模型、工具、流程与Agent自身。[10]展示人类与AI研发分工的变化。'),
dict(title='从已有系统出发，沿四部分看它怎样变好',seconds=20,body=nav,sources=[],
script='整场沿一条主线：从已有系统出发，Agent参与修改和验证，让它更好。先讲选题与主线，再看Anthropic的模型训练，接着看OpenAI与Google的研发流程和程序优化，最后看Agent自我改进与下一轮研发。',
note='四部分目录与后续页眉逐字对应。保持A01—07、B08—13、C14—18、D19—24分工；千问AgentEvolver属于D，不静默移到C。不是所有案例都训练同一个baseline Agent。'),
dict(title='从自动研究，走向递归自我改进',seconds=40,body=['RSI：Recursive Self-Improvement｜递归自我改进','autoresearch：改代码、训练、比较，再继续','RSI进一步看：成果能否提高下一轮研发能力'],sources=[1,10,12],
script='RSI是Recursive Self-Improvement，递归自我改进：改进后的系统还能推动下一轮改进。Karpathy今年三月开源的autoresearch提供了一个小入口：Agent改训练代码，让小模型训练五分钟，比较结果，再继续。这是自动研究；要进一步谈RSI，还得看成果能否让研究者自己更会研究。',
note='[12]原版单GPU；五分钟只指训练预算，不含启动和编译。[1]Good1965历史、[14]更早自动研究放入备课，不挤目录。Agent程序层局部RSI可成立，不限定必须训练基础模型权重。'),
dict(seconds=30),
dict(seconds=35),
dict(seconds=25,script='Agent的能力由模型、工具和运行流程共同支撑。所以我们选Anthropic看模型训练，选OpenAI与Google看评测和程序优化，再用开放研究看Agent自身改进。AIDE²也报告了代码层的连续改进。这样，后面每个案例都能接回同一个研发问题。'),
dict(seconds=30,script='先从Agent的重要基础——模型能力看起。Anthropic Fellows的一项研究要减少模型迎合错误观点。Claude Opus 4.8驱动研究Agent，提出方法和实现；Qwen3.5-2B是被训练的目标模型；评测器检查改善和能力副作用。这里，Agent是研发者，模型是改进对象。下面看它怎样把想法变成训练和评测。')]
after=json.loads(json.dumps(before,ensure_ascii=False))
for i,u in enumerate(updates):after[i].update(u)
for i,s in enumerate(after):s['section']=nav[0 if i<7 else 1 if i<13 else 2 if i<18 else 3]
assert sum(s['seconds'] for s in after[:7])==205 and sum(s['seconds'] for s in after)==850
assert all({k:v for k,v in a.items() if k!='section'}=={k:v for k,v in b.items() if k!='section'} for a,b in zip(before[7:],after[7:]))
p.write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=ROOT/'01_自然口播稿.md';t=p.read_text(encoding='utf-8');start=t.index('## A ');end=t.index('## B ',start)
new='## A 陈云海｜选题与主线\n\n'+''.join(f"### {s['n']:02} {s['title']} 预算{s['seconds']}秒\n\n{s['script']}\n\n" for s in after[:7])
p.write_text(t[:start]+new+t[end:],encoding='utf-8',newline='\n')
p=ROOT/'17_A部分口播与练习.md'
intro='# A部分口播与练习\n\n对应01—07页。主题一采用行业应用案例研究：看Agent怎样参与AI研发，改进模型、工具与Agent自身。7页205秒为设计预算，尚未真人计时。先对照投影讲一遍，深入追问查[组长A备课](18_A部分答辩备课.md)。\n\n'
cues=['先点明应用行业和改进对象，不把AI研发泛化成所有软件开发。','沿四行目录往下讲；主线是已有系统、修改、验证与保留。','先解释RSI英文，再指自动实验循环和研究者能力回流的区别。','沿上方三块和返回箭头讲研发正反馈，末句交代条件。','区分会研究、跑得起与能成立，算法和资源一起判断。','把模型、工具和Agent三种改进位置接到后面案例。','指三个角色，明确本例先改模型，由下一页展开训练流程。']
p.write_text(intro+''.join(f"## {s['n']:02} {s['title']}\n\n{s['script']}\n\n**指图与动作：**{cues[i]}\n\n" for i,s in enumerate(after[:7])).rstrip()+'\n',encoding='utf-8',newline='\n')
qa=ROOT/'qa/opening_09';qa.mkdir(parents=True,exist_ok=True)
(qa/'editorial.json').write_text(json.dumps({'ASeconds':205,'AChineseCharacters':sum(len(re.findall(r'[\u4e00-\u9fff]',s['script'])) for s in after[:7]),'navigation':nav,'mainSlides':24,'totalSlides':34,'BCDContentUnchanged':True,'humanTimingVerified':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
print('A09_SOURCE_AND_NAVIGATION_READY')
