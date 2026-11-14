# Chốt cấu hình dự kiến trước test

Ngày thực hiện: 2026-11-14. Chọn dự kiến theo dev: hybrid TF-IDF + dense pgvector chiến lược B, lấy 3 ứng viên mỗi nguồn, RRF k=60, top-3, context 1600 ký tự; câu query thực tế là câu hỏi gốc. Model `openai/gpt-4o-mini`, embedding `openai/text-embedding-3-small`, 1536 chiều. Prompt yêu cầu citation chỉ có ID. Baseline cần so sánh: TF-IDF top-3, context 800 ký tự, cùng corpus và câu hỏi.

Lý do: trên 17 câu dev có đáp án, hybrid Hit@3 16/17 so với TF-IDF 13/17; budget 1600 giữ evidence 16/17 so với hybrid budget 800 đạt 13/17. Prompt citation đã thử lại riêng q03/q04; đây không đủ chứng minh hiệu quả tổng thể. Cần hoàn tất đánh giá agent dev, xác nhận nhãn thiếu evidence và cài đặt, đo agent baseline trước khi báo cáo test. Nếu sửa tiếp dựa trên test, phải tạo test mới.

## Khóa cấu hình trước chạy test

Đã chạy lại 19 câu dev cho hai agent tại `artifacts/dev-hybrid-v2/` và `artifacts/dev-tfidf-agent/` với cùng model và prompt, truy vấn gốc và corpus B. Kết quả retrieval trên 17 câu có evidence: hybrid 13/17 Hit@1, 16/17 Hit@3, context 16/17; TF-IDF 11/17, 13/17, context 11/17. Hai câu thiếu evidence còn cần người học review nhãn. Chọn hybrid top-3/RRF 60/budget 1600; so với baseline TF-IDF top-3/budget 800. Thay đổi prompt citation giữ nguyên cho cả hai cấu hình test. Cấu hình này không được sửa dựa trên kết quả test; nếu sửa cần test mới. Review chất lượng câu trả lời dev chưa hoàn tất tại thời điểm khóa; không suy ra chính xác agent chỉ từ retrieval.
