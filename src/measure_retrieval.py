"""Measure held-out evidence against already collected ranked agent traces."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "starter"))
from baseline import hit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--questions", type=Path, required=True)
    parser.add_argument("--traces", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads(args.questions.read_text(encoding="utf-8"))
    cases = [case for case in cases if case.get("answerable") is not False]
    traces = json.loads(args.traces.read_text(encoding="utf-8"))
    by_id = {trace["query_id"]: trace for trace in traces}
    if len(by_id) != len(traces) or not cases:
        raise ValueError("Duplicate trace IDs or no answerable cases")
    rows = []
    for case in cases:
        trace = by_id[case["id"]]
        if trace["question"] != case["question"]:
            raise ValueError(f"Question mismatch: {case['id']}")
        events = [event for event in trace["events"] if event.get("event") == "search"]
        if len(events) != 1:
            raise ValueError(f"Expected one search: {case['id']}")
        event = events[0]
        results, ids, gold = event["results"], event["context_ids"], case["gold"]
        rows.append({"id": case["id"],
                     "hit1": bool(results and hit(results[0], gold)),
                     "hit3": any(hit(row, gold) for row in results[:3]),
                     "context_hit": any(hit(row, gold) and row["id"] in ids for row in results)})
    result = {"n": len(rows), **{k: sum(row[k] for row in rows) for k in ("hit1", "hit3", "context_hit")}, "per_query": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
