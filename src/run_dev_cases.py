"""Chạy agent trên một số câu dev và lưu trace riêng."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(
        description="Chạy agent trên danh sách câu hỏi dev"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=2,
        help="Số câu đầu tiên cần chạy",
    )

    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit phải lớn hơn 0")

    cases_path = ROOT / "starter" / "results" / "cases-dev.json"

    cases = json.loads(cases_path.read_text(encoding="utf-8"))

    selected_cases = cases[: args.limit]

    output_dir = ROOT / "starter" / "results" / "dev-agent"
    output_dir.mkdir(parents=True, exist_ok=True)
    issues_dir = ROOT / "starter" / "results" / "dev-agent-issues"
    issues_dir.mkdir(parents=True, exist_ok=True)

    print(f"Sẽ chạy {len(selected_cases)} câu.\n")

    for index, case in enumerate(selected_cases, start=1):
        query_id = case["id"]
        question = case["question"]

        # Chỉ cho phép ID đơn giản để dùng an toàn làm tên file.
        if not re.fullmatch(r"[A-Za-z0-9_-]+", query_id):
            raise ValueError(f"ID không hợp lệ: {query_id}")

        output_path = output_dir / f"{query_id}.json"

        # Tránh ghi đè một trace đã có.
        if output_path.exists():
            print(f"[{index}] Bỏ qua {query_id}: trace đã tồn tại.")
            continue

        command = [
            sys.executable,
            "-X", "utf8",
            str(ROOT / "src" / "agent_demo.py"),
            "--query-id",
            query_id,
            "--question",
            question,
            "--output",
            str(output_path),
        ]

        print(f"\n[{index}/{len(selected_cases)}] Đang chạy {query_id}...")

        result = subprocess.run(command, cwd=ROOT)

        if result.returncode == 0 and output_path.exists():
            print(f"Đã lưu trace: {output_path}")
        else:
            issue = {"query_id": query_id, "status": "needs_investigation",
                     "return_code": result.returncode,
                     "reason": "Không tạo được trace hoàn chỉnh; xem log terminal."}
            (issues_dir / f"{query_id}.json").write_text(
                json.dumps(issue, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"Lần chạy {query_id} chưa tạo được trace. Hãy xem lỗi phía trên.")


if __name__ == "__main__":
    main()
