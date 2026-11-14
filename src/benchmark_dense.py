"""Benchmark Day 6 pgvector retrieval against the Day 7 dev baseline."""
import json
import os
import statistics
import sys
import time
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
# Đường dẫn starter Day 6: ưu tiên biến môi trường DAY6_STARTER, mặc định tìm
# repo Day 6 cạnh repo Day 7 để người chấm không cần sửa code.
DAY6 = Path(os.getenv(
    "DAY6_STARTER",
    str(ROOT.parent / "K5-L3A-Day06-PHAMVANNAM-2A202603681-DataIngestionEngineering" / "starter"),
))
sys.path.insert(0, str(DAY6))
sys.path.insert(0, str(ROOT / "starter"))
from src.embeddings import MyEmbedder  # type: ignore
from src.store import PgVectorStore  # type: ignore
from baseline import hit, pack_context, validate  # type: ignore


def main():
    load_dotenv(DAY6 / ".env")
    chunks = json.loads((ROOT / "starter/data/converted/chunks.json").read_text(encoding="utf-8"))
    all_questions = json.loads((ROOT / "starter/data/converted/questions.json").read_text(encoding="utf-8"))
    questions = [q for q in all_questions if q.get("split") == "dev"]
    validate(chunks, questions)
    embedder = MyEmbedder(model_name="openai/text-embedding-3-small")
    store = PgVectorStore(os.environ["DATABASE_URL"], 1536)
    traces = []
    try:
        for question in questions:
            started = time.perf_counter()
            vector = embedder.embed_query(question["question"])
            if len(vector) != 1536:
                raise ValueError("Query embedding không có 1536 chiều")
            rows = store.search("B", vector, top_k=3, filters=None)
            results = [{"id": r["chunk_id"], "source_id": r["document_id"],
                        "source": r["source"], "page": r["page"], "text": r["text"],
                        "metadata": {"chapter": r["chapter"]}, "score": r["score"],
                        "hit": hit({"source_id": r["document_id"], "page": r["page"], "text": r["text"]}, question["gold"])}
                       for r in rows]
            context, ids = pack_context(results, budget=800)
            traces.append({"query_id": question["id"], "question": question["question"],
                           "results": results, "context": context, "context_ids": ids,
                           "hit1": bool(results and results[0]["hit"]),
                           "hit3": any(r["hit"] for r in results),
                           "context_hit": any(r["hit"] and r["id"] in ids for r in results),
                           "context_chars": len(context),
                           "elapsed_ms": (time.perf_counter() - started) * 1000})
            print(f"Đã xử lý {len(traces)}/{len(questions)}: {question['id']}", flush=True)
    finally:
        store.conn.close()
    summary = {"strategy": "dense_pgvector_B", "split": "dev", "n": len(traces),
               "hit1": sum(t["hit1"] for t in traces), "hit3": sum(t["hit3"] for t in traces),
               "context_hit": sum(t["context_hit"] for t in traces),
               "avg_context_chars": statistics.mean(t["context_chars"] for t in traces),
               "median_ms": statistics.median(t["elapsed_ms"] for t in traces),
               "service_cost_usd": None}
    output = ROOT / "starter/results/dev-dense"
    output.mkdir(parents=True, exist_ok=True)
    for name, value in (("summary.json", summary), ("traces.json", traces)):
        (output / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
