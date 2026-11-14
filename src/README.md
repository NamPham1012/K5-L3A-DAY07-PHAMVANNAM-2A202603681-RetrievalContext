# Code Day 7: cách chạy lại

Chương trình dùng repo Day 6, OpenRouter, PostgreSQL/pgvector và model ngôn ngữ. Gọi API có thể tốn phí. Không commit API key hoặc `.env`.

## Chuẩn bị

1. Cài Python 3.11+, Docker Desktop và dependencies từ `starter/requirements.txt` của repo Day 6.
2. Khởi động PostgreSQL Day 6, giữ volume và index B 1536 chiều; kiểm tra `scripts/check_setup.py` ở Day 6. Index phải tạo bằng `openai/text-embedding-3-small`, nội dung và ID khớp `data/day6-chunks-b.json`.
3. `.env` trong `starter` Day 6 cần `DATABASE_URL` và `OPENROUTER_API_KEY`; `OPENROUTER_CHAT_MODEL` tùy chọn, mặc định `openai/gpt-4o-mini`.
4. Từ Git Bash ở repo Day 7, kích hoạt môi trường Day 6. Cả `agent_demo.py`, `benchmark_dense.py`, `day6_search.py` đọc biến `DAY6_STARTER`; mặc định tìm repo Day 6 nằm **cạnh** repo Day 7 (`../K5-L3A-Day06-.../starter`). Đặt `export DAY6_STARTER="/d/.../starter"` nếu đường dẫn khác máy.

### Dựng lại index nếu người chấm không có volume PostgreSQL

Phần dense/hybrid cần index pgvector B 1536 chiều của Day 6. Nếu không có sẵn volume, dựng lại từ Day 6: chạy pipeline ingestion Day 6 với embedding `openai/text-embedding-3-small` trên đúng corpus trong `data/day6-chunks-b.json` (nội dung và ID chunk phải khớp). Khi chưa có index, chỉ nhánh **TF-IDF** (`--strategy tfidf`) chạy được offline, không cần PostgreSQL hay API embedding; nhánh hybrid/dense sẽ báo thiếu `DATABASE_URL`.

```bash
source "/d/AI THUC CHIEN VIN/code/LAB/K5-L3A-Day06-PHAMVANNAM-2A202603681-DataIngestionEngineering/starter/.venv/Scripts/activate"
export PYTHONUTF8=1
python -m unittest discover -s tests -v
```

Điều chỉnh đường dẫn cho máy khác. Các test dùng mock chỉ kiểm tra code.

## Hỏi một câu

```bash
python src/agent_demo.py --strategy hybrid --query-id demo --question "An ninh mạng là gì?" --show-context --output starter/results/demo.json
```

Đổi `--strategy hybrid` thành `--strategy tfidf` để dùng baseline. Mặc định hybrid budget 1600 ký tự, TF-IDF 800; đổi được bằng `--budget`. ID citation hợp lệ không chứng minh câu trả lời được hỗ trợ. Trace `pending_review` cần chấm thủ công.

## Chạy hàng loạt

```bash
python src/run_benchmark_agent.py --cases artifacts/cases-dev-v1.json --strategy hybrid --output starter/results/dev-hybrid-new --workers 2
python src/run_benchmark_agent.py --cases data/test_draft.json --strategy tfidf --output starter/results/test-tfidf-new --workers 2
```

Runner chỉ chuyển ID và câu hỏi cho agent, không chuyển gold hoặc `answerable`. Chạy test sau khi khóa cấu hình trên dev. Kết quả đã có được lưu trong `artifacts/`. Runner bỏ qua trace có sẵn; dùng thư mục mới cho lần chạy mới. Trường hợp không tạo trace được ghi nhận dưới `issues/`, không phải nhãn chất lượng.

## Tổng hợp

`artifacts/reviews-*.json` là nhãn trợ lý đề xuất, cần học viên review. `traces-*-reviewed.json` là bản sao có trạng thái để tổng hợp, trace gốc vẫn riêng.

```bash
python starter/agent_metrics.py --cases artifacts/cases-test.json --traces artifacts/traces-test-hybrid-reviewed.json --reviews artifacts/reviews-test-hybrid.json --split test --output starter/results/check-test-metrics.json
```

Script tổng hợp grounded answer, citation và abstention, không tự đánh giá nội dung. Retrieval/context được ghi trong `artifacts/metrics-test-hybrid.json`; nhãn chấm context có trong reviews. Đối chiếu câu thiếu evidence tại `artifacts/kiem-tra-thieu-evidence.md` và PDF gốc.

Tính lại Hit@1, Hit@3 và context evidence từ trace đã lưu, không gọi API:

```bash
python src/measure_retrieval.py --questions data/test_draft.json --traces artifacts/traces-test-hybrid-reviewed.json --output starter/results/recheck-retrieval.json
```
