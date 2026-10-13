# 证据审查 Agent：制作材料与运行合同

首次实际运行请先看 [第一次真实Agent运行.md](第一次真实Agent运行.md)：从本地项目、新聊天、复制任务提示，到保存原始动作和校验。下方人工样例自检和评分命令不会启动Agent。

当前状态（2026-10-13）：`smoke/` 是独立教学题，已由制作代理真实调用工具完成资格探测，证据见 `runs/smoke/`；`dev/` 为24条制作代理可见开发题；`demo/` 为16条**制作代理演示题**，作者和同一 Codex 工作区已经见过题目与答案，绝非成员 C 独立保管的盲测或 sealed holdout。`smoke/example_output/` 只是校验器人工样例，不能当真实模型输出。任何目录空白都不代表运行完成。

本轮 `runs/demo/freeze.json` 记录的是两个独立新上下文各自一次处理16题，提示中请求每批最多10次工具调用，未由平台硬限额强制；它与下文规定的逐题独立新会话不同。补证的公开调用事件为基线10、候选13，包含通信；两版执行代码各有10处静态嵌套引用。若把通信也计入所有调用，候选超过名义10次，不能宣称严格等调用预算。demo 的原始输出须全部保存并按实际条件报告，不能把该批次称作按学生最终测试协议完成的实验，也不能声称开发错误驱动了候选优化。两段可重放媒体及其证据边界见 `../media/分镜与证据.md`。

## 最短本地自检

从 `大作业_V3_制作中` 运行：

```powershell
python practice/validate.py --input practice/smoke/example_output/smoke-01.json --claims practice/smoke/claims.json --sources practice/smoke/sources.json
python practice/score.py --claims practice/smoke/claims.json --gold practice/smoke/gold.json --sources practice/smoke/sources.json --variant example=practice/smoke/example_output
```

这只验证脚本，不算 Agent 实验。真实 Agent 应读取 `smoke/sources.json` 里给出的官方 URL 和定位，在可见工具日志中留下读取动作，然后自行写 JSON 并调用校验器。独立 smoke 成功后再运行开发集。

## 固定运行步骤

1. 基线和候选用**同一模型标识、来源包、工具权限、每题工具调用上限、超时、上下文与输出字段**。记录平台版本、日期、采样设置能否固定。每条题目独立新会话；不能把金标文件发给被测 Agent。输入只用 `claims.json` 与 `sources.json`，金标由执行者或评分者在结束后读取。
2. 两套提示各跑24条开发题。保存每例 `runs/dev/{baseline|candidate}/outputs/<id>.json`、公共 `actions.jsonl`、原始可公开运行记录、失败输出和真实时长。禁止自动补写未发生的工具调用。候选修改最多三版，每版先记录实际开发错误、diff、人接受或拒绝理由。
3. **先冻结候选文件与运行配置 SHA-256**，再让同一执行者在同一条件下跑16条 `demo/`。演示集此前已向制作代理暴露，结果仅称“制作代理演示集配对观察”。如果候选在演示结果后修改，此轮结果不能再当冻结比较。
4. 对 C 自己设备准备的真正最终测试，另按 `成员C_独立测试操作.md`，题目和答案在候选冻结前不得进入共同工作区。那批数据应按事实族避开开发集重复。四位成员真实操作才能称“四人实践”。

运行记录 `run_manifest.json` 至少写 `platform`、`model_id`、`started_at`、`ended_at`（ISO时间带时区）、`prompt_sha256`、`config_sha256`、`claims_sha256`、`sources_sha256`、`tool_allowlist`、`max_tool_calls`、`timeout_seconds`、`sampling_settings_or_unknown`、`executor`、`status`。动作行建议为 `{"at":"...","claim_id":"...","tool":"...","target":"...","result":"..."}`。不能伪造采样温度、token成本、人工盲核或独立性。

## 评分

脚本自动给出分类正确数、混淆矩阵、夸大/矛盾题被错判 `supported` 的次数、缺失/格式错误。它只能验证 `fragment_id` 在来源索引存在，**不能自动确认该片段支持该标签**。定位得分须由人逐题核实“来源存在、位置正确、片段支持标签”三项，写 `location_review.json`，格式 `{"baseline":{"D01":true},"candidate":{"D01":false}}`；未核的题用 `null`，不得算正确。A 冻结后匿名核两个输出，C 记录分歧和裁定。输入与金标分开存放，执行 Agent 不读金标。

```powershell
python practice/score.py --claims practice/dev/claims.json --gold practice/dev/gold.json --sources practice/sources.json --variant baseline=practice/runs/dev/baseline/outputs --variant candidate=practice/runs/dev/candidate/outputs --out practice/runs/dev/score.json
```

演示集将 `dev` 换为 `demo`。一题为16题总数的6.25个百分点；报告保留分子/分母及逐题配对，不能用小样本声称稳健或因果提升。工具读取次数与耗时从**真实**动作日志和时间戳统计，不能用提示字数估算。已知来源摘要在 `sources.json`，正式核引仍回读一手 URL，具体核实卡见 `../sources/00_一手来源定位包.md`。
