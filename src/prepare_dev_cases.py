"""Chuẩn bị danh sách câu hỏi dev cho đánh giá agent."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main():
    # 1. Đọc câu hỏi có đáp án đã chuyển từ Day 6.
    questions_path = ROOT / "starter" / "data" / "converted" / "questions.json"

    questions = json.loads(
        questions_path.read_text(encoding="utf-8")
    )

    # 2. Đọc các câu dự kiến thiếu bằng chứng.
    missing_path = ROOT / "data" / "dev_missing_evidence.json"

    missing_questions = json.loads(
        missing_path.read_text(encoding="utf-8")
    )

    # 3. Tạo danh sách case có đáp án.
    cases = []

    for question in questions:
        if question["split"] == "dev":
            cases.append({
                "id": question["id"],
                "split": "dev",
                "question": question["question"],
                "answerable": True,
            })

    # 4. Thêm các case dự kiến thiếu bằng chứng.
    for question in missing_questions:
        if question["split"] == "dev":
            cases.append({
                "id": question["id"],
                "split": "dev",
                "question": question["question"],
                "answerable": False,
                "absence_reason": question["absence_reason"],
            })

    # 5. Kiểm tra các mã câu hỏi không bị trùng.
    ids = [case["id"] for case in cases]

    if len(ids) != len(set(ids)):
        raise ValueError("Có mã câu hỏi bị trùng.")

    # 6. Lưu danh sách case.
    output_path = ROOT / "starter" / "results" / "cases-dev.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(
        json.dumps(cases, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    answerable_count = sum(case["answerable"] for case in cases)
    missing_count = len(cases) - answerable_count

    print(f"Tổng số câu dev: {len(cases)}")
    print(f"Có đáp án: {answerable_count}")
    print(f"Dự kiến thiếu bằng chứng: {missing_count}")
    print(f"Đã lưu: {output_path}")


if __name__ == "__main__":
    main()
