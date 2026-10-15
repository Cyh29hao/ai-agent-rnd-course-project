# PR怎么提，更新怎么看

适用于四人内容协作。分工已定，不要求人人再学一套Git流程；可以让自己的Codex处理分支、提交和PR。

小PR用来逐步完善，完整初稿计划在2026年10月31日结束前完成，含自己的PPT、逐页文字稿、答辩与实际自检。后续安排由陈云海确定，[详细要求](分工与衔接.md)。未实际审阅或试讲，不因文件生成而填完成。

## 最方便的合作形式

| 你现在要做什么 | 用什么方式 |
|---|---|
| 改自己的讲稿、图示、答辩或交一份具体提案 | 自己分支 → 一个小PR → 组长审阅整合 |
| 只问一句哪里不懂、指出一个错误 | Issue，或先反馈给组长；不必为此准备PR |
| 本地文件已做好，但不会提交或网络不通 | 交回文件和改动说明，由组长代交并记实际建议来源 |
| 改正式PPT、Word或PDF | 先交修改范围，由组长统一整合、导出，避免多人覆盖 |

**不要求先开Issue再开PR。** 已知分工的小修改直接提PR即可；问题还没想清再开Issue讨论。

## 还没加入仓库的人，现在怎么办

现在把GitHub用户名或个人主页链接发给陈云海即可，陈云海核对账号后发邀请。仓库是private，收到邀请后需要本人接受，才能访问；不是把仓库链接发过去就已加入。

组长网页入口：[Settings → Collaborators](https://github.com/Cyh29hao/ai-agent-rnd-course-project/settings/access) → Add people → 搜索并核对账号 → 发邀请。组员检查邀请通知或邮件并接受，然后打开README确认能看到材料。本轮没有收到另外两位的账号，也没有新增或发送邀请，不预填成员账号。

可直接转给小组的文字：

> 还没加入仓库的两位，把GitHub用户名或个人主页链接发我，我邀请你们，收到后记得接受。首页已有分工、材料和各人Codex提示词。我们计划11月前完成各自完整初稿：自己的PPT、文字稿和答辩都认真准备、看熟、试讲，虽然是初稿也尽量做到最好。后续我再视情况安排。改稿可以让Codex帮忙提PR，不熟悉操作也可交文件给我代交。

以上只提供文案，由本人发送。[GitHub官方邀请说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/repository-access-and-collaboration/inviting-collaborators-to-a-personal-repository)

## 提PR的最短流程

1. **更新基准。** 先看`git status`和当前分支，保留本地改动；`git fetch origin main`获取main信息。仅当前main干净且可快进时执行`git pull --ff-only origin main`。已有协作分支则比较差异，不盲目切换或reset。
2. **自己的分支。** 建议`collab/<短名>/<part>-<主题>`，例如`collab/zhang/b-distill`。有既有任务分支就复用，不必为了名字重建。
3. **改一件事。** 先交自己范围内最有价值的1—3处。默认写独立提案；明确约定直接改源稿时，同步必要的关联文件。
4. **运行检查。** `python scripts/check_collaboration_docs.py`及`git diff --check`；涉及事实核原文，涉及素材看实际显示。不可用的检查如实记下。
5. **只提交本任务文件。** commit并push自己的分支，创建PR：**base选main，compare选自己的分支**。标题示例`[B] 讲清教师、学生与蒸馏训练`；需要继续讨论可先建Draft PR。
6. **回应审阅。** 按意见在同一个分支继续提交，同一个PR会更新；不用每轮再开新PR。组长对主要建议说明采纳、调整或暂缓。

PR不是新PPT版本，它是把一组改动拿出来比较和讨论的地方。网页`Files changed`能逐文件看差异、定位评论并提交审阅。[GitHub官方审阅说明](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/reviewing-proposed-changes-in-a-pull-request)

## PR说明只需回答这些问题

使用仓库自动带出的[PR模板](../.github/pull_request_template.md)，不必另写长报告：

- 哪个Part、哪几页、基于哪个提交？任务ID可选，有就填。
- 为什么改？具体换成什么，最多列三处优先建议。
- 改了哪些文件？提案还是直接改源稿？需要组长同步哪些地方？
- 涉及数字或事实，原文在哪一节/图/页？
- 实际检查了什么，哪些没做？当前PPT是否仍为05？

小范围PR更容易接回。不要混入另一个人的改动、批量重命名历史文件或把生成的二进制文件覆盖到旧版。

## 谁合并，怎样才算采用

内容协作默认由组长陈云海或其明确授权者审阅合并，提出者不自行合并自己的PR。组长按内容决定接受或调整，必要时请相邻Part核对；仓库入口维护由组长统一更新。这是组内合作约定，不表示已经配置强制分支保护。

| 状态 | 实际意味着什么 |
|---|---|
| PR打开 / Draft | 有一份建议在讨论，还没进入main |
| 提案PR已合并 | 建议被保存到main；需看逐项决定，不能认为每句都采用 |
| 源稿已整合 | 接受的修改进入相关正文；导出文件可能仍旧 |
| 新交付版已查并发布入口 | 新PPT/PDF等已生成检查，更新当前版本清单 |
| 真人排练通过 | 实际理解、合讲和计时另有记录，不由前几步推断 |

组长不要只回复“收到”：在提案整合区逐项说明决定、正式修订和检查。未采纳内容保持建议状态。需要改进时在同一PR继续，不用强推覆盖历史。

## 一分钟看懂仓库最近发生了什么

| 想知道什么 | 去哪里 |
|---|---|
| 我们最新定了什么？ | [README](../README.md)顶部及[更新速览](../CHANGELOG.md) |
| 我这段下一步改什么？ | [ABCD路线](分工与衔接.md)与[各人提示词](Codex协作提示词.md) |
| 有什么还在讨论、等审核？ | [打开的PR](https://github.com/Cyh29hao/ai-agent-rnd-course-project/pulls) |
| 哪些改动已合并？ | [已合并PR](https://github.com/Cyh29hao/ai-agent-rnd-course-project/pulls?q=is%3Apr+is%3Amerged)；内容维护也可能由组长直接提交 |
| 某文件具体改了哪句？ | 打开文件点History，再点相应提交看差异；或看[main提交记录](https://github.com/Cyh29hao/ai-agent-rnd-course-project/commits/main/) |
| 我该下载哪份正式材料？ | [当前版本清单](当前版本.json)及[V5入口](../v5/从这里开始.md)，不按最近修改时间猜 |
| 检查有没有过？ | PR中的Checks或[Actions](https://github.com/Cyh29hao/ai-agent-rnd-course-project/actions)；绿勾只表示相应自动检查通过 |

浏览器看到了更新，不代表本地已更新。让Codex检查当前分支、未提交改动及与`origin/main`的差异；只有main干净且可快进才pull。不要为了追最新而丢掉正在写的内容。

正式主讲当前仍为V5修订05。新的沟通文档、提案或提交，不自动产生修订06。实践仍为可选未启动，未指派给D。

## 可直接发给自己的Codex

```text
按docs/PR协作与更新速查.md帮助我提交本Part的改稿。先保留工作区，获取并说明最新main、当前分支和我的改动；不reset、不混入他人文件。用自己的collab分支提交本任务，按模板创建base为main的PR，标题标Part和改进目的。任务ID不是必填。只报告真实检查，正式导出仍旧就写清楚。新意见在同一分支继续提交，不重开一串PR，不强推、不自动合并。授权或网络不可用就保留文件并给代交路径。
```
