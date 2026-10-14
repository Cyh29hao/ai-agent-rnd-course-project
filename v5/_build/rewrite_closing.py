"""Refine the talk's language while retaining its facts, order and design."""
from pathlib import Path
import json,re,shutil
ROOT=Path(__file__).resolve().parents[1]
hist=ROOT/'qa/history/before_closing_edit';hist.mkdir(parents=True,exist_ok=True)
for name in ['主讲内容.json','01_自然口播稿.md','02_四人速读与排练.md','05_课程报告.md']:
    dst=hist/name
    if not dst.exists():shutil.copy2(ROOT/name,dst)
data=json.loads((ROOT/'主讲内容.json').read_text(encoding='utf-8'))
by={d['n']:d for d in data}
by[3]['body'][2]='检查行为改善\n和能力损失'
by[3]['body'][3]='记录失败\n决定下一次尝试'
by[5]['body'][-1]='改进能否让下一轮研发做得更好'
by[5]['script']='下面先跟着一个改模型的任务走：任务怎么交给Agent，方法怎么进入模型，结果又怎么用于下一次尝试。看完这些具体工作，再回到题目：这些改进能不能让下一轮研发做得更好？'
by[6]['script']='我们重点选这两家，是想展开研发中的两个环节。Anthropic的公开研究能看到训练方法和目标模型的变化，OpenAI作者的案例能看到评测任务怎样执行、怎样留下记录。Google和开放研究再补上算法、策略和代码。一起看，就能知道Agent进入了哪些研发工作。'
by[16]['script']='Runme把命令放在笔记里执行，输出也能跟着保存。请从上到下看：目标和计划说明为什么做，命令和输出记录具体发生了什么，解释与取舍交代下一步怎么选。换一个会话，Codex就能读取这些记录，接着处理任务。它和前面的共享实验记录有一个共同点：上次怎么做、哪里失败、为什么这样决定，都能留给下一次。这里的记忆就保存在这些可读取的记录中。'
by[18]['script']='这个案例报告，一个矩阵乘法kernel加速了23%，对应Gemini总训练时间减少1%。左边说的是一个算子，右边说的是完整训练。训练还有其他大量工作，所以一个环节快了很多，整段训练的收益仍可能比较小。23%落在这个算子上，1%才对应总训练时间。这个例子让我们看到，Agent找到的一项程序改动，怎样实际进入大模型训练。'
by[19]['script']='开放研究还展示了两个改动对象。通义团队的AgentEvolver通过生成任务、复用经验和轨迹贡献归因来训练Agent策略。Sakana的Darwin Gödel Machine会修改Agent自身代码，用基准评价，再保留候选谱系，让不同版本继续探索。策略训练和代码修改发生在不同位置。框架公开以后，这些改动更容易查清；训练数据和模型权重是否开放，还要分别看项目给出的资料。'
by[20]['script']='大家看中间这一列，每个案例到底改了什么。Anthropic训练的是目标模型，OpenAI留下的是评测流程和研究记录，Google修改训练相关程序，开放研究还会改Agent策略和代码。再看右边，效果分别落在行为、任务结果或程序性能上。把这些位置分清以后，下一轮研发的问题就具体了：这轮的成果会留在哪里，接下来谁来用它？'
by[21]['title']='把上一轮的成果带进下一轮研发'
by[21]['body']=['实验记录留下来，下次接着试','DGM让改好的Agent继续探索','下一代基础模型，能否也这样持续改进？']
by[21]['script']='先看上面的流程。研究Agent做完实验，把方法和结果留下来，下一次尝试就有了起点。前面的共享记录和Runme，都在做这件事。DGM还往前走了一步：它改的是Agent自身代码，改好的版本可以继续探索新的修改。于是，下一轮既能接着用以前的记录，也可能换成一个改进后的研究Agent。把问题推进到基础模型，就要继续观察：这样一轮轮做下去，能不能持续研发出更强的后继模型？'
by[21]['note']='下方回流特指DGM在Agent代码层的迭代，不表示AAR把Qwen替换成Opus研究Agent。最后一问讨论基础模型的持续后继研发。'
by[22]['title']='下一轮，能不能研究得更好？'
by[22]['body']=['换一组新任务，还能做好吗？','同样的时间和算力，能找到更好的方法吗？','连续改几轮，会退步或钻测试的空子吗？']
by[22]['script']='可以让原版和改进后的版本，各做一轮研究，用同一组新任务，也给同样的时间和算力。先比较它们找到的方法好不好，再换任务、继续迭代几轮。这样能看清几件事：它是不是只擅长刚才那批题，下一轮有没有研究得更有效，还有会不会退步或钻测试的空子。对基础模型研发来说，跟踪这些连续变化，比只看某一轮的最高分更有说服力。'
by[22]['note']='本页是对后续比较方法的讨论，不是已执行的实验，也不是要求本组新增实验。泛化、等预算比较、多轮收益与代价均为本报告分析问题。'
by[23]['title']='AI已经参与研发，接下来要看下一轮'
by[23]['seconds']=25
by[23]['body']=['能改模型，也能改进研发Agent','我们看到了训练办法、评测记录、算法和代码','改进后的系统，能否接着研发更强的基础模型？']
by[23]['script']='回到开头Good提出的问题。今天，Agent已经能提出训练办法、跑评测、优化程序，也开始改进自身代码。接下来最值得看的，是改进后的研究系统做下一轮研发时，能否继续产出更强的基础模型。沿着这一轮轮的结果往下看，才能理解AI辅助研发会走到哪里。'
(ROOT/'主讲内容.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
secs=sum(d['seconds'] for d in data)
groups=[('A','问题与动机、案例进入',1,7),('B','模型改进机制与结果',8,13),('C','研发流程与训练算法',14,18),('D','开放研究与递归问题',19,24)]
lines=['# V5自然口播稿 精修版','',f'对应24页主讲。正文和媒体预算{secs}秒，另留约50秒交接，合计约15分钟。实际时长未真人计时。',
       '','本组实践暂时搁置。A/B/C/D尚未对应成员姓名。页脚来源不用朗读；第11页短片边播放边解释，播放失败讲同页静态图。','']
for role,topic,start,end in groups:
    lines.extend([f'## {role} {topic}',''])
    for d in data[start-1:end]:
        lines.extend([f'### {d["n"]:02} {d["title"]} 预算{d["seconds"]}秒','',d['script'],''])
(ROOT/'01_自然口播稿.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'slides':len(data),'seconds':secs,'chinese_script_chars':sum(len(re.findall(r'[\u4e00-\u9fff]',d['script'])) for d in data)}))
