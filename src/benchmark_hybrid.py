"""Combine cached dense rankings and TF-IDF rankings using RRF on dev."""
import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "starter"))
from baseline import TfidfIndex, hit, pack_context, validate


def main():
    parser = argparse.ArgumentParser(description="Đánh giá hybrid RRF trên dev")
    parser.add_argument("--budget", type=int, default=800, help="Giới hạn context theo ký tự")
    parser.add_argument("--output", type=Path, default=ROOT / "starter/results/dev-hybrid")
    args = parser.parse_args()
    if args.budget < 1:
        parser.error("--budget phải lớn hơn 0")
    chunks = json.loads((ROOT / "starter/data/converted/chunks.json").read_text(encoding="utf-8"))
    questions = json.loads((ROOT / "starter/data/converted/questions.json").read_text(encoding="utf-8"))
    questions = [q for q in questions if q.get("split") == "dev"]
    validate(chunks, questions)
    dense = json.loads((ROOT / "starter/results/dev-dense/traces.json").read_text(encoding="utf-8"))
    dense_by_id = {row["query_id"]: row for row in dense}
    if len(dense_by_id) != len(dense) or set(dense_by_id) != {q["id"] for q in questions}:
        raise ValueError("Dense trace không khớp bộ câu hỏi dev")
    chunks_by_id = {c["id"]: c for c in chunks}
    index = TfidfIndex(chunks)
    traces = []
    for q in questions:
        dense_trace = dense_by_id[q["id"]]
        if dense_trace["question"] != q["question"]:
            raise ValueError(f"Câu hỏi {q['id']} đã thay đổi; chạy lại dense benchmark")
        start = time.perf_counter()
        lexical = index.search(q["question"], top_k=3)
        scores, ranks = {}, {}
        for name, ranking in (("tfidf", lexical), ("dense", dense_trace["results"])):
            for rank, candidate in enumerate(ranking, 1):
                cid = candidate["id"]
                if cid not in chunks_by_id or candidate["text"] != chunks_by_id[cid]["text"]:
                    raise ValueError(f"Chunk {cid} không khớp corpus; chạy lại dense benchmark")
                scores[cid] = scores.get(cid, 0.0) + 1 / (60 + rank)
                ranks.setdefault(cid, {})[name] = rank
        ids = sorted(scores, key=lambda cid: (-scores[cid], cid))[:3]
        results = [{**chunks_by_id[cid], "score": scores[cid], "ranks": ranks[cid],
                    "hit": hit(chunks_by_id[cid], q["gold"])} for cid in ids]
        context, context_ids = pack_context(results, budget=args.budget)
        traces.append({"query_id": q["id"], "question": q["question"],
                       "results": results, "context": context, "context_ids": context_ids,
                       "hit1": bool(results and results[0]["hit"]),
                       "hit3": any(c["hit"] for c in results),
                       "context_hit": any(c["hit"] and c["id"] in context_ids for c in results),
                       "context_chars": len(context),
                       "offline_fusion_ms": (time.perf_counter() - start) * 1000})
    summary = {"strategy": "hybrid_rrf", "split": "dev", "n": len(traces),
               "candidate_top_k_each": 3, "rrf_k": 60, "output_top_k": 3, "budget_chars": args.budget,
               "hit1": sum(t["hit1"] for t in traces), "hit3": sum(t["hit3"] for t in traces),
               "context_hit": sum(t["context_hit"] for t in traces),
               "avg_context_chars": statistics.mean(t["context_chars"] for t in traces),
               "median_offline_fusion_ms": statistics.median(t["offline_fusion_ms"] for t in traces),
               "note": "Dense rankings cached: offline timing excludes embedding and pgvector; cost not measured."}
    output = args.output
    output.mkdir(parents=True, exist_ok=True)
    for name, obj in (("traces.json", traces), ("summary.json", summary)):
        (output / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
