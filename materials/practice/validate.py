"""Validate one evidence-review JSON without external dependencies."""
import argparse
import json
from pathlib import Path
import sys

FIELDS = {"claim_id", "label", "source_id", "fragment_id", "rationale", "limitation", "suggested_wording"}
LABELS = {"supported", "overstated", "contradicted", "insufficient"}


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def validate(record, claim_ids=None, fragments=None):
    errors = []
    if not isinstance(record, dict):
        return ["root: expected JSON object"]
    for key in sorted(FIELDS - record.keys()):
        errors.append(f"{key}: missing")
    for key in sorted(record.keys() - FIELDS):
        errors.append(f"{key}: unknown field")
    for key in sorted(FIELDS & record.keys()):
        if not isinstance(record[key], str) or not record[key].strip():
            errors.append(f"{key}: expected nonempty string")
    if isinstance(record.get("label"), str) and record["label"] not in LABELS:
        errors.append("label: invalid category")
    if claim_ids is not None and record.get("claim_id") not in claim_ids:
        errors.append("claim_id: not in input set")
    if fragments is not None:
        source_id, fragment_id = record.get("source_id"), record.get("fragment_id")
        if source_id not in fragments:
            errors.append("source_id: not in source index")
        elif fragment_id not in fragments[source_id]:
            errors.append("fragment_id: not in indicated source")
    return errors


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", required=True)
    p.add_argument("--claims")
    p.add_argument("--sources")
    args = p.parse_args()
    try:
        record = read_json(args.input)
        claims = read_json(args.claims) if args.claims else None
        sources = read_json(args.sources) if args.sources else None
        claim_ids = {x["claim_id"] for x in claims} if claims is not None else None
        fragments = {s["source_id"]: {f["fragment_id"] for f in s["fragments"]} for s in sources} if sources is not None else None
        errors = validate(record, claim_ids, fragments)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors = [f"read/parse: {exc}"]
    if errors:
        print("INVALID: " + "; ".join(errors), file=sys.stderr)
        return 1
    print(f"VALID {record['claim_id']} {record['label']} {record['source_id']}#{record['fragment_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
