"""Fixed, deterministic label scoring. Evidence quality requires a separate human review."""
import argparse
from collections import Counter
import json
from pathlib import Path
from validate import read_json, validate


def score(claims, gold, outputs, fragments, reviewed=None):
    ids = [c["claim_id"] for c in claims]
    if len(ids) != len(set(ids)) or set(ids) != set(gold):
        raise ValueError("Claim IDs must be unique and exactly match gold IDs")
    correct = 0
    false_release = 0
    risky = 0
    valid = 0
    location_ok = 0
    location_reviewed = 0
    matrix = Counter()
    rows = []
    for claim_id in ids:
        truth = gold[claim_id]
        if truth not in {"supported", "overstated", "contradicted", "insufficient"}:
            raise ValueError(f"Invalid gold label: {claim_id}")
        if truth in {"overstated", "contradicted"}:
            risky += 1
        path = outputs / f"{claim_id}.json"
        try:
            result = read_json(path)
            issues = validate(result, set(ids), fragments)
            if result.get("claim_id") != claim_id:
                issues.append("claim_id: filename mismatch")
        except (OSError, ValueError, TypeError) as exc:
            result, issues = {}, [f"read/parse: {exc}"]
        label = result.get("label") if not issues else "INVALID"
        if not issues:
            valid += 1
        is_correct = label == truth
        correct += is_correct
        false_release += truth in {"overstated", "contradicted"} and label == "supported"
        matrix[(truth, label)] += 1
        loc = None if reviewed is None else reviewed.get(claim_id)
        if loc not in (None, True, False):
            raise ValueError(f"Location review must be true/false/null: {claim_id}")
        if loc is not None:
            location_reviewed += 1
            location_ok += bool(loc)
        rows.append({"claim_id": claim_id, "gold": truth, "predicted": label,
                     "correct": is_correct, "location_review": loc, "issues": issues})
    return {"total": len(ids), "valid_outputs": valid, "label_correct": correct,
            "false_release": false_release, "risky_gold_total": risky,
            "location_correct": location_ok if reviewed is not None else None,
            "location_reviewed": location_reviewed if reviewed is not None else None,
            "matrix": [{"gold": g, "predicted": p, "count": n} for (g, p), n in sorted(matrix.items())],
            "rows": rows}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--claims", required=True)
    p.add_argument("--gold", required=True)
    p.add_argument("--sources", required=True)
    p.add_argument("--variant", action="append", required=True, help="NAME=OUTPUT_DIRECTORY")
    p.add_argument("--location-review", help="JSON mapping variant -> claim_id -> true/false/null")
    p.add_argument("--out")
    args = p.parse_args()
    claims, gold, sources = (read_json(x) for x in (args.claims, args.gold, args.sources))
    fragments = {s["source_id"]: {f["fragment_id"] for f in s["fragments"]} for s in sources}
    location = read_json(args.location_review) if args.location_review else {}
    report = {"note": "Script scores labels only. Location is manually reviewed, not inferred from fragment existence.",
              "variants": {}}
    for spec in args.variant:
        name, sep, directory = spec.partition("=")
        if not sep or not name or name in report["variants"]:
            p.error(f"Invalid or repeated variant: {spec}")
        report["variants"][name] = score(claims, gold, Path(directory), fragments, location.get(name))
    data = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        Path(args.out).write_text(data, encoding="utf-8")
    print(data)


if __name__ == "__main__":
    main()
