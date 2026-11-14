"""Run a fixed agent configuration; gold and labels stay outside the agent."""
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--strategy", choices=("tfidf", "hybrid"), required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    def run(case):
        cid = case["id"]
        if not cid.replace("_", "").replace("-", "").isalnum():
            raise ValueError("Invalid case ID")
        output = args.output / (cid + ".json")
        if output.exists():
            return cid, "existing"
        cmd = [sys.executable, "-X", "utf8", str(ROOT / "src/agent_demo.py"),
               "--query-id", cid, "--question", case["question"],
               "--strategy", args.strategy, "--output", str(output.resolve())]
        try:
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
            if result.returncode != 0 or not output.exists():
                # No secrets or request headers are written to artifact logs.
                return cid, f"failed exit={result.returncode}; no trace={not output.exists()}"
            return cid, "ok"
        except subprocess.TimeoutExpired:
            return cid, "timeout"
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as executor:
        for future in as_completed([executor.submit(run, c) for c in cases]):
            cid, status = future.result()
            if status not in ("ok", "existing"):
                issues = args.output / "issues"
                issues.mkdir(exist_ok=True)
                (issues / (cid + ".json")).write_text(
                    json.dumps({"query_id": cid, "status": "needs_investigation", "detail": status},
                               ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"{cid}: {status}", flush=True)


if __name__ == "__main__":
    main()
