"""Apply the confirmed seven-page A narrative; preserve B, C and D sources."""
from pathlib import Path
import json,re,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'主讲内容.json';before=json.loads(p.read_text(encoding='utf-8'))
updates=[
dict(title='智能体在大模型产业研发中的应用',seconds=15,
body=['AI辅助研发距离递归自我改进还有多远？','以Anthropic、OpenAI等公司的公开实践为例'],
script='大家好。今天我们看智能体怎样参与大模型研发。AI不只在帮助完成任务，也开始帮助研发AI本身。那么，这些改进能不能让下一轮研发变得更快、更好？',
note='A08开场。封面沿用正式07视觉；提出由D回答的全场问题。'),
dict(title='RSI：让改进能力进入下一轮',seconds=25,
body=['Recursive Self-Improvement｜递归自我改进','改进后的研究系统，继续推动后续改进','1965：Good提出机器设计更好机器的设想'],
script='RSI的英文是Recursive Self-Improvement，中文叫递归自我改进。这里的递归，是说改进后的系统还能继续参与后续改进。早在1965年，Good就设想过机器设计更好的机器。今天我们把这个问题落到研发上：不只看它产出了什么，还要看它是否更有能力做下一轮研究。',
note='[1]为历史背景；[10]为完整后继研发愿景。RSI也有Agent代码层的局部用法，不用固定底模或人工参与直接否定一切RSI。'),
dict(title='autoresearch：先把实验循环交给AI',seconds=35,
body=['Karpathy，2026年3月：单GPU上的小模型训练研究','改代码 → 训练 → 比较指标 → 保留或丢弃 → 再试','自动研究，进一步走向研究者自身的改进'],
script='一个直观入口是Karpathy今年三月开源的autoresearch。AI修改训练代码，让小模型训练五分钟，再看验证指标，保留有效修改，继续尝试。原版用一张GPU就能开始。它把研究中的实验循环自动化了。RSI则进一步追问：这些成果能不能让研究者自己更会研究？所以，自动研究是走向递归自改的一条路径，但完成一次实验循环，还没有回答后一个问题。',
note='[12]README How it works / Design choices。5分钟是训练墙钟预算，不含启动和编译，不是整个实验总时长。原项目不自动更新研究Agent基础模型。自动研究方向早于该项目，见[14]，不称Karpathy首创整个概念。'),
dict(title='研发能力也能改进，意义就不止一次提效',seconds=30,
body=['更强的AI → 更有效的研发 → 更强的系统','成果回到下一轮，可能形成复利式加速','每轮增益、资源与评测，决定齿轮能转多快'],
script='这正是它值得重视的地方。一次提效，只让眼前任务做得更快；如果改进还能提高研发能力，就可能让下一轮更容易找到好方法。更强的AI帮助研发，研发再带来更强的系统，形成正反馈。它有机会产生复利式、甚至指数式的增长。不过，这需要增益持续成立、资源和评测跟得上，不能把一张反馈图当成已经发生的智能爆炸。',
note='正反馈示意为本报告分析，不是数据图。[10]讨论持续加速与S形停滞的不同情景；[15]为反馈条件的建模研究，不是已验证的增长定律。'),
dict(title='小实验能起步，前沿规模还要过资源关',seconds=40,
body=['会研究：模型能力、工具与研究判断','跑得起：推理成本、训练算力、实验周期','能成立：同预算、新任务与跨规模验证'],
script='但从小实验走到前沿模型，是另一道门槛。研究Agent需要有用的想法和工具，试验要付出推理成本，模型训练还需要相应算力。方法在小模型上有效，也要检验放大后是否仍有效。这让我们判断所谓RSI算法时，不能只看名字，要看实际规模、预算和可重复的提升。数据和benchmark本身可以有价值，但有这些产品，不等于已经实现持续自我改进。算法能省多少资源，资源又允许验证到哪一步，要放在一起看。',
note='[12]单GPU说明起步不必自有大集群；[10]讨论研究工具、资源、能源与算力约束。“跨规模验证”是本报告的审查建议，不声称某论文已证明所有规模。没有证据支持很多公司普遍炒作或业务无用，不点名归因。'),
dict(title='从自动实验，追到下一轮研发',seconds=30,
body=['Anthropic：训练方法怎样进入模型','OpenAI、Google：评测与程序怎样改进','开放研究：Agent怎样改变自身，再继续研究'],
script='现在，自动跑实验、优化训练程序，以及Agent修改自身代码，都已有公开实例。最近的AIDE²也报告了研究Agent代码层的连续改进。接下来，我们重点看Anthropic怎样改模型，OpenAI作者怎样组织评测，再用Google和开放研究补齐程序与Agent。沿着这条研发链，最后再回答：哪些成果已经回到下一轮，还有哪些能力需要继续验证？',
note='已有案例[4]—[8]；AIDE²[13]为2026-09-22预印本作者报告。这里只提一句，不展开新基准和数字。主实验固定各循环底模、改harness代码；不是前沿基础模型多代训练。'),
dict(title='任务：让模型少迎合错误观点',seconds=30,
body=['研究Agent：提出并实施训练方法','目标模型：Qwen3.5-2B，接受后训练','评测器：检查谄媚改善与能力副作用'],
script='先落到Anthropic Fellows的一项对齐研究：让模型少迎合用户的错误观点。这里有三个角色。Claude Opus 4.8驱动研究Agent，负责想方法、写实现；Qwen3.5-2B是被训练的目标模型；评测器检查行为改善和能力副作用。先分清谁在研究、谁被改变，下面再看Agent怎样把一个想法变成训练和评测。',
note='[4]§2—3、App.D.4。保留与B第8页的角色和术语，具体实验规则及机制由B展开。')]
after=json.loads(json.dumps(before,ensure_ascii=False))
source_ids=[[],[1,10],[12],[10,15],[10,12],[4,5,6,7,8,13],[4]]
for i,u in enumerate(updates):
    after[i].update(u)
    after[i]['sources']=source_ids[i]
assert after[7:]==before[7:]
assert sum(s['seconds'] for s in after[:7])==205
assert sum(s['seconds'] for s in after)==850
p.write_text(json.dumps(after,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
p=ROOT/'01_自然口播稿.md';text=p.read_text(encoding='utf-8')
start=text.index('## A ');end=text.index('## B ',start)
text=text[:start]+'## A 陈云海｜问题、自动研究与递归改进\n\n'+''.join(f"### {s['n']:02} {s['title']} 预算{s['seconds']}秒\n\n{s['script']}\n\n" for s in after[:7])+text[end:]
p.write_text(text,encoding='utf-8',newline='\n')
qa=ROOT/'qa/a_refinement_08';qa.mkdir(parents=True,exist_ok=True)
receipt={'baseRelease':'V5-07','ASeconds':205,'totalContentSeconds':850,'ACount':7,'BCDSourceUnchanged':True,
         'AChineseCharacters':sum(len(re.findall(r'[\u4e00-\u9fff]',s['script'])) for s in after[:7]),'humanTimingVerified':False}
(qa/'editorial.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
