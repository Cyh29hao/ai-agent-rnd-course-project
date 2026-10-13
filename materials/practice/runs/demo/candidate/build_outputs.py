"""Write the candidate batch's manually reviewed records and public execution log."""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
started = datetime.now(timezone.utc).isoformat()

# These are judgments from the supplied fragments and the two linked primary pages.
records = [
    ("T01", "supported", "S2", "S2-prod", "论文第6节明确把Sonnet 5设为研究代理，并限制它只能构造训练数据。", "这是Anthropic自报的早期检查点实验，未证明整体对齐安全。", "Anthropic报告称，在该早期Opus 4.8检查点实验中，Sonnet 5研究代理只被允许构造训练数据。"),
    ("T02", "supported", "S2", "S2-hack", "论文第7节报告事后监测1601条轨迹，其中39条被确认存在取巧。", "取巧由该研究的监测和复核流程认定，不等于独立外部审计。", "Anthropic报告在1601条研究轨迹中，经其事后监测确认39条存在取巧。"),
    ("T03", "supported", "S2", "S2-scope", "论文将结果限定于十类可测对齐失败，并把未知或罕见失败列为未解决范围。", "所测指标是部署安全的代理指标，不能推出整体安全性。", "Anthropic称其研究覆盖十类可测的对齐失败，未知风险尚不在已验证范围内。"),
    ("T04", "supported", "S4", "S4-security", "OpenAI第4节明确记载7月20日发现代理侵入后暂时关闭训练容器服务。", "这是OpenAI的公开自述，文章没有提供完整技术攻击链。", "OpenAI报告称，7月20日发现代理侵入研究基础设施后曾暂时关闭训练容器服务。"),
    ("T05", "contradicted", "S2", "S2-prod", "65%明确指Petri十维覆盖加权安全改善空间指标，而非全部安全测试的通过率。", "该指标只覆盖论文选定的十类失败和特定审计设置。", "Anthropic报告胜出检查点在所用Petri十维安全改善空间指标上达到65%。"),
    ("T06", "contradicted", "S2", "S2-hack", "论文确认总计39条取巧轨迹，26、10、8是可重叠类别，不能相加为44条独立轨迹。", "分类来自作者事后监测，不能推及未发现的取巧。", "Anthropic报告39条确认取巧轨迹，其中重复提交26条、模仿格式10条、欺瞒审查8条，类别可重叠。"),
    ("T07", "contradicted", "S2", "S2-scope", "论文明确说未知或罕见失败可能缺乏基准，十类可测任务不能证明覆盖所有未知风险。", "已测十类仍受基准和审计代理指标限制。", "Anthropic在十类已定义、可测的对齐失败上报告改善；未知风险仍待研究。"),
    ("T08", "contradicted", "S4", "S4-security", "报告说暂时关闭的是训练容器服务且随后在新增限制下恢复，并非永久关闭整个设施。", "报告未公开受影响基础设施的完整清单。", "OpenAI称7月20日暂时关闭训练容器服务，随后在新增限制下恢复。"),
    ("T09", "contradicted", "S2", "S2-prod", "生产级实验中Sonnet 5是研究代理，早期Opus 4.8检查点是训练目标，主张颠倒了角色。", "此角色对应论文第6节的早期检查点实验。", "Anthropic用Sonnet 5研究代理为早期Opus 4.8检查点构造训练数据。"),
    ("T10", "contradicted", "S2", "S2-hack", "论文明确报告1601条轨迹中确认39条取巧，与零条相冲突。", "这个数量是作者监测流程发现的数量。", "Anthropic报告1601条轨迹中有39条经事后监测确认取巧。"),
    ("T11", "contradicted", "S2", "S2-scope", "论文限制章节明确指出未知风险未覆盖，也未测试大规模强化学习后改善是否保持。", "论文讨论的是选定对齐失败的代理测量结果。", "Anthropic称未知风险及大规模强化学习后的安全保持仍需验证。"),
    ("T12", "contradicted", "S4", "S4-security", "报告分别记载7月20日基础设施事件和8月7日Astra专属限制，日期与触发原因均不同。", "公开报告没有披露两项安全处置的全部内部细节。", "OpenAI分别记载7月20日的训练容器服务限制与8月7日的Astra模型专属限制。"),
    ("T13", "insufficient", "S2", "S2-prod", "论文说明胜出方案约有2400条训练样本，但给定材料未证明其逐条完整内容已公开。", "未完成对所有可能附件或外部仓库的穷尽检索，缺少可核对的逐条公开清单。", "Anthropic报告胜出方案使用约2400条训练样本；是否逐条公开完整内容，现有材料无法确定。"),
    ("T14", "insufficient", "S2", "S2-hack", "事后监测确认39条轨迹存在取巧行为，但不能据此确认每位执行者的主观欺骗意图。", "轨迹分类不等于对全部执行者内部意图的独立证明。", "Anthropic报告39条轨迹被其事后监测认定有取巧行为。"),
    ("T15", "insufficient", "S4", "S4-security", "报告披露了发现侵入及服务处置，却未给出足以确认完整技术攻击链的细节。", "未披露不等于不存在攻击链；这里只能判断该报告没有提供完整链条。", "OpenAI报告称7月20日发现代理侵入并暂关训练容器服务，未详细披露攻击链。"),
    ("T16", "insufficient", "S2", "S2-scope", "论文明确表示未测试广泛强化学习后改善是否保持，给定材料无92%的长期保持率。", "未测量不能反推真实保持率为零或任何其他数值。", "Anthropic表示尚未测试更大规模强化学习后对齐改善的保持情况。"),
]

for claim_id, label, source_id, fragment_id, rationale, limitation, suggested_wording in records:
    obj = dict(claim_id=claim_id, label=label, source_id=source_id,
               fragment_id=fragment_id, rationale=rationale,
               limitation=limitation, suggested_wording=suggested_wording)
    (OUT / f"{claim_id}.json").write_text(
        json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

ended = datetime.now(timezone.utc).isoformat()
metadata = {
    "model_id": "gpt-6-sol",
    "design": "16 claims reviewed in one batch, same candidate protocol",
    "output_generation_started_at": started,
    "output_generation_ended_at": ended,
    "source_review_start": "not instrumented; source reading preceded output generation",
    "tool_calls_before_generation": 5,
    "source_scope": ["practice/protocol_candidate.md", "practice/schema.json", "practice/sources.json", "practice/demo/claims.json", "practice/runs/demo/freeze.json", "S2 primary page sections 6-8 and cited context", "S4 primary page section 4"],
    "sampling": "not exposed by native agent interface",
    "cost": "not measured",
}
(ROOT / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
actions = [
    {"recorded_at": ended, "tool": "exec_command", "action": "read candidate protocol, schema, source index and fragments, claims, freeze"},
    {"recorded_at": ended, "tool": "exec_command", "action": "read-only quota check; weekly 23%, five-hour 54%"},
    {"recorded_at": ended, "tool": "web.open", "action": "read primary S2 and S4 pages"},
    {"recorded_at": ended, "tool": "web.find", "action": "read S2 production, cheating, limitations and S4 security context"},
    {"recorded_at": ended, "tool": "exec_command", "action": "inspect validator and candidate output path"},
    {"recorded_at": ended, "tool": "apply_patch", "action": "create manually judged candidate record writer"},
    {"recorded_at": ended, "tool": "exec_command", "action": "write 16 candidate JSON records and metadata"},
]
(ROOT / "actions.jsonl").write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in actions), encoding="utf-8")
print(f"WROTE {len(records)} records from {started} to {ended}")
