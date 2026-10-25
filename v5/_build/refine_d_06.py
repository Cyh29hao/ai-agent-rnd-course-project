"""Apply the D-only editorial revision; do not regenerate historical QA."""
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
path=ROOT/'主讲内容.json'
before=json.loads(path.read_text(encoding='utf-8'))
updates={
19:dict(script='前面改的是模型和训练程序。开放研究还把Agent自身作为改进对象。左边的AgentEvolver会生成任务、复用经验，再把行动的贡献用于奖励，训练Agent的策略。右边的DGM会改自己的工具和流程代码，比如增加补丁检查；运行评测后，把不同版本存进档案，供后续继续探索。这里要分清，训练策略与修改代码，是两种不同的改进。',body=['AgentEvolver：生成任务、复用经验，用奖励训练策略','DGM：修改工具与流程代码，评测后从版本档案继续探索','策略训练会更新模型参数；DGM此实验固定底层模型'],note='D部分06修订。采用曹天卓来稿区分改策略与改代码的讲法；档案不是只保留当前最高分版本。AgentEvolver v1 §3—5；DGM v1 §3、官方Introduction。基准分母与具体例子见10_D部分答辩备课。'),
20:dict(script='把前面的案例放在一起看，先问它改了哪个对象。Anthropic训练目标模型，OpenAI这个案例改进评测流程、留下研究记录，Google优化训练程序。刚才的开放研究，则训练Agent策略或修改自身代码。这些结果分别体现在模型行为、任务完成情况和程序性能上。下一步就要问：这轮留下的成果，会怎样进入下一轮研究？'),
21:dict(script='上一轮的成果，有两种接法。第一种是把实验记录留下来，下次读取成功和失败，接着提出方法。前面的共享记录和Runme就是这样。第二种更进一步：DGM改了Agent自身，后续还能从这些版本继续探索。图中两条返回的箭头，分别表示带回记录和带回修改后的Agent。如果要把这个思路推广到基础模型研发，还要看它能否持续做出更强的后继模型。',body=['实验记录留下来，下一轮接着试','DGM让修改后的Agent继续探索','基础模型后继研发，需要继续跟踪多轮结果']),
22:dict(script='怎样判断它下一轮真的研究得更好了？可以让原版和改进版，在同样预算下研究同一组新任务。先看找到的方法是否更好，再换任务、连续观察几轮，同时记录失败和人工帮助。这样有助于判断，它有没有只适应刚才那批题，是否提高研发效率，以及会不会退步或钻测试空子。这是我们提出的比较思路，本组没有做这项实验。',body=['换一组新任务，改进还能保持吗？','同样的预算，能找到更好的方法吗？','连续几轮，会退步或钻测试空子吗？'],note='本页是本报告提出的后续比较思路，不是已执行实验，也不要求本组新增实践。预算宜记录时间、计算/调用成本和人工帮助；新任务用于检查迁移，多轮结果包括失败与代价。有限测试有助判断，不能保证普遍持续改进。'),
23:dict(title='局部自改已经发生，下一步看持续研发',script='所以，回到开头的问题，我们已经看到特定任务里的局部自我改进：Agent能帮助改模型，也能修改自身代码并继续探索。对于今天关注的大模型研发，下一步要检验的是，这些改进能否持续提高下一轮研究的能力，产出更强的基础模型。这就是我们对“距离递归自我改进还有多远”的回答：已有具体进展，持续的后继研发还需要跨轮次检验。',body=['已有特定任务中的局部自改','训练方法、评测流程、算法和代码都已有实例','改进后的研究系统，能否持续研发更强的基础模型？']),
24:dict(script='谢谢大家，欢迎提问。')
}
after=json.loads(json.dumps(before,ensure_ascii=False))
for slide in after:
    if slide['n'] in updates:slide.update(updates[slide['n']])
assert before[:18]==after[:18]
assert [x['seconds'] for x in before]==[x['seconds'] for x in after]
path.write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')

p=ROOT/'01_自然口播稿.md';text=p.read_text(encoding='utf-8');start=text.index('## D 曹天卓')
d='## D 曹天卓｜开放研究与递归问题\n\n'
for s in after[18:24]:d+=f"### {s['n']:02} {s['title']} 预算{s['seconds']}秒\n\n{s['script']}\n\n"
p.write_text(text[:start]+d.rstrip()+'\n',encoding='utf-8',newline='\n')

practice='''# D部分口播与练习

这六页接在C的训练程序优化之后，回答“Agent自身能否被改进，这些改进怎样帮助下一轮研发”。采用曹天卓来稿的两条路线引入，经AI精修。设计预算3分10秒，尚未真人计时。

先记住一句话：**已经有特定任务里的局部自改；持续提高基础模型研发能力，要看后续多轮的真实表现。**

练习时先顺着讲一遍，标出自己不明白或讲不顺的句子，再看[组长答辩备课](10_D部分答辩备课.md)的对应解释。成员无需另补一套研究说明与问答。现场暂按组长一人答辩准备。

'''
actions={19:'先指左边，再指右边；明确训练策略与修改代码。',20:'沿表格逐行看改动对象，最后问成果交给谁。',21:'先讲上面的研究过程，再顺着两条返回箭头解释记录与Agent版本。',22:'指三项检查，末句说明这是建议而非本组实验。',23:'先给已有局部自改的答案，再解释持续后继研发的问题。',24:'停留在结束页，按问题进入备份材料。'}
for s in after[18:24]:practice+=f"## {s['n']} {s['title']}\n\n{s['script']}\n\n**指图与动作：**{actions[s['n']]}\n\n"
practice+='''## 最后试讲时看什么

把自己不熟悉的术语换成能解释的说法；出现AgentEvolver、DGM时稍作停顿。若超时，先删重复解释，机制和结论保留。3分10秒只是预算，实际时长由本人讲过后记录。需要深入答辩时，组长查配套备课材料即可，不把整本问答塞进口播。
'''
(ROOT/'11_D部分口播与练习.md').write_text(practice,encoding='utf-8',newline='\n')

p=ROOT/'02_四人速读与排练.md';text=p.read_text(encoding='utf-8')
start=text.index('## D｜');end=text.index('## 合起来',start)
replacement='''## D｜曹天卓｜19—24页｜3分10秒

**记住的结论：** AgentEvolver训练策略，DGM修改Agent代码并从版本档案继续探索；已出现任务内局部自改。我们关注的持续基础模型后继研发，还需要跨轮次检验。

**指图顺序：** 两种改进对象 → 全场研发地图 → 记录和Agent版本分别返回 → 新任务、同预算、多轮比较 → 明确回答题目。

**练习与追问：** 先看[六页口播与练习](11_D部分口播与练习.md)。组长答辩查[机制、例子与追问](10_D部分答辩备课.md)，包括DGM固定底模、档案多样性和基准分母。成员只需理解并练熟自己部分。

**收尾：** 23页先说已有特定任务中的局部自改，再说明基础模型后继研发还要观察多轮；24页进入提问。

'''
text=text[:start]+replacement+text[end:]
text=text.replace('每人先熟悉自己的图，再按顺序合讲一次，记录实际总时长和卡住的位置。','成员先练熟自己的部分，组长再按全场顺序试讲，记录实际总时长和卡住的位置。')
p.write_text(text,encoding='utf-8',newline='\n')
print(json.dumps({'DChineseCharacters':sum(len(re.findall(r'[\u4e00-\u9fff]',s['script'])) for s in after[18:24]),'designSeconds':sum(s['seconds'] for s in after[18:24]),'ABCUnchanged':True}))
