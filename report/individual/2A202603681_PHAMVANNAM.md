# Báo cáo Day 7 — Phạm Văn Nam (2A202603681)



## Dữ liệu và benchmark

- **Nguồn, quyền sử dụng, số trang và số chunk:** bản gốc Luật An ninh mạng 24/2018/QH14, PDF 32 trang; 169 chunk "B". Nguồn và cách đếm trang ghi trong manifest Day 6; dữ liệu dùng lại từ corpus Day 6 (cần quyền sử dụng tài liệu khi tái lập).
- **Vector store, embedding model, phiên bản và số chiều:** PostgreSQL 16.16 + pgvector 0.8.7, embedding `openai/text-embedding-3-small` (1536 chiều), độ đo cosine, gọi qua OpenRouter.
- **Agent model, cách chạy và phân chia dev/test:** agent `openai/gpt-4o-mini`, chọn gọi tool, tối đa một vòng tool + một lượt trả lời cuối; thực tế query giữ nguyên câu hỏi gốc. Split: **17 câu dev có đáp án + 2 câu dev thiếu bằng chứng**; **5 câu test mới có đáp án + 2 câu test thiếu bằng chứng** (tổng 22 câu có evidence, 4 câu thiếu evidence). File: `data/questions-dev.json`, `data/dev_missing_evidence.json`, `data/test_draft.json`. Không gửi gold/answerable tới model. Cấu hình được khóa trước khi chạy test tại `docs/chot-cau-hinh-dev.md`.
- **Cách xác định câu có/thiếu evidence và tiêu chí chấm:** câu có đáp án lấy từ Day 6 với evidence theo trang/vùng. Câu thiếu bằng chứng được rà soát trích xuất toàn bộ 32 trang PDF (`artifacts/kiem-tra-thieu-evidence.md`); còn khả năng lỗi trích xuất hoặc cách diễn đạt khác — chưa xác nhận tuyệt đối, cần đọc lại PDF. Chấm: retrieval (Hit@1/Hit@3/Context Evidence), grounded answer thủ công 0/1/2, citation hỗ trợ, abstention đúng/nhầm.

## Retrieval và thử nghiệm

Số retrieval dưới đây đo trên 17 câu dev / 5 câu test **có đáp án** (nguồn: `artifacts/retrieval/*.json` và `artifacts/metrics-*.json`). Một cấu hình vừa là phương pháp mới vừa là bước cải thiện được chú thích rõ.


| Cấu hình               | Phương pháp, top-k, filter, rerank, context budget                    | Giả thuyết / thay đổi                                 | Split | Hit@1        | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí                          |
| ---------------------- | --------------------------------------------------------------------- | ----------------------------------------------------- | ----- | ------------ | -------------- | --------------------- | -------------------------------------------- |
| Baseline               | TF-IDF tách từ đơn giản, top-3, không filter/rerank, budget 800 ký tự | Mốc so sánh                                           | dev   | 11/17 (0.65) | 13/17 (0.76)   | 11/17 (0.65)          | median retrieval ≈0.35 ms; cost 0            |
| Phương pháp 2 (dense)  | Dense pgvector chiến lược B, top-3, cosine, budget 800                | Semantic match thay cho khớp từ                       | dev   | 12/17 (0.71) | 13/17 (0.76)   | 12/17 (0.71)          | median ≈689 ms; token embedding chưa quy giá |
| Phương pháp 3 (hybrid) | Hybrid: 3 ứng viên TF-IDF + 3 dense, RRF k=60, top-3, budget 800      | Kết hợp lexical + semantic                            | dev   | 13/17 (0.76) | 16/17 (0.94)   | 13/17 (0.76)          | avg context 591 ký tự                        |
| Cải thiện 1            | Hybrid như trên, **budget 1600** ký tự                                | Evidence ở top-3 nhưng bị budget 800 cắt khỏi context | dev   | 13/17 (0.76) | 16/17 (0.94)   | **16/17 (0.94)**      | avg context 591→1336 ký tự                   |
| Cải thiện 2            | Prompt citation chỉ ID (bỏ tiền tố `chunk-id:`)                       | Giảm citation sai định dạng                           | dev   | —            | —              | —                     | thử lại riêng q03/q04 (xem phân tích lỗi)    |
| **Cấu hình đã chọn**   | Hybrid RRF k=60, top-3, budget 1600, prompt citation chỉ ID           | Chốt trên dev, đo test sau                            | test  | 3/5 (0.60)   | 5/5 (1.00)     | 5/5 (1.00)            | agent median 4166 ms                         |
| Baseline               | TF-IDF top-3, budget 800                                              | So sánh trên test                                     | test  | 3/5 (0.60)   | 5/5 (1.00)     | 3/5 (0.60)            | agent median 3182 ms                         |


**Hai lỗi dev, nguyên nhân, cách thử, lý do chọn:**

1. **q12/q15/q16 (budget cắt evidence):** evidence nằm trong top-3 nhưng budget 800 loại khỏi context. Thử **Cải thiện 1** (budget 1600) → Context Evidence Rate 13/17 → **16/17**, context trung bình 591→1336 ký tự.
2. **q03/q04 (citation sai định dạng):** prompt ban đầu sinh citation kèm tiền tố `chunk-id:` → citation không hợp lệ. **Cải thiện 2** (chỉ dẫn ID nguyên văn) → chạy lại riêng q03/q04 cho citation hợp lệ. **Chưa đủ chứng minh hiệu quả tổng thể**: q11, q17 vẫn có khẳng định ngoài citation; q15 hybrid nhầm lực lượng chuyên trách với lực lượng bảo vệ nói chung.

**Lý do chọn cấu hình:** hybrid budget 1600 cho Hit@3 16/17 (so TF-IDF 13/17) và giữ evidence trong context 16/17. Cấu hình được khóa tại `docs/chot-cau-hinh-dev.md` **trước** khi xem test; không chỉnh cấu hình sau khi đọc kết quả test.

## Agent và đánh giá

- **Tool, số lượt gọi, điều kiện dừng, cách chọn context, xử lý lỗi:** agent dùng model thật chọn gọi một tool retrieval, tối đa một vòng tool + một lượt trả lời; context lấy top-3 chunk theo cấu hình đến khi đầy budget. Trường hợp model không gọi tool hoặc tool lỗi **chưa có trace agent chuẩn** — runner ghi nhận sự cố riêng. Kiểm tra citation ID chỉ là kiểm tra hình thức; nội dung nguồn được trợ lý đối chiếu thủ công trong review.


| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và TB /2 | Citation hợp lệ¹ | Câu có citation | Abstention đúng | Từ chối nhầm |
| ---------------- | -------- | ----------- | ------------------------------ | ---------------- | --------------- | --------------- | ------------ |
| dev / TF-IDF     | 19/19    | 1 mỗi câu   | 5/2/10 — 1.29                  | 11/17            | 16/16           | 2/2             | 1/17         |
| dev / Hybrid     | 19/19    | 1 mỗi câu   | 0/4/13 — 1.76                  | 15/18            | 17/17           | 2/2             | 0/17         |
| test / TF-IDF    | 7/7      | 1 mỗi câu   | 1/1/3 — 1.40                   | 4/5              | 5/5             | 2/2             | 0/5          |
| test / Hybrid    | 7/7      | 1 mỗi câu   | 0/0/5 — 2.00                   | 5/5              | 5/5             | 2/2             | 0/5          |


¹ **Citation hợp lệ** đếm theo **từng citation** (không theo câu), nên mẫu số có thể khác số câu (ví dụ hybrid dev 15/18 = 15 trong 18 citation hợp lệ). Các cột còn lại tính theo câu. Grounded answer chấm thủ công; context grade thủ công cho 5 câu test có đáp án: TF-IDF 1/1/3, hybrid 0/0/5.

**Bảng per-query — cấu hình đã chọn (Hybrid, split test):**


| Query ID         | Loại câu         | Tool call và kết quả                          | Câu trả lời và citation                                  | Nhãn, lý do                                              |
| ---------------- | ---------------- | --------------------------------------------- | -------------------------------------------------------- | -------------------------------------------------------- |
| test\_new\_01    | Có đáp án        | retrieval hybrid → hit (top-3)                | Nguyên tắc hợp tác quốc tế; `luat-anm-2018-p5-p3`        | grounded 2, ctx 2 — p5-p3 nêu nguyên tắc hợp tác quốc tế |
| test\_new\_02    | Có đáp án        | retrieval hybrid → hit                        | Quyền của trẻ em; `luat-anm-2018-p26-p3`                 | grounded 2, ctx 2 — đúng câu hỏi                         |
| test\_new\_03    | Có đáp án        | retrieval hybrid → hit                        | Môn giáo dục quốc phòng–an ninh; `luat-anm-2018-p28-p2`  | grounded 2, ctx 2                                        |
| test\_new\_04    | Có đáp án        | retrieval hybrid → hit                        | Cảnh báo và biện pháp phòng ngừa; `luat-anm-2018-p31-p2` | grounded 2, ctx 2                                        |
| test\_new\_05    | Có đáp án        | retrieval hybrid → hit                        | Trách nhiệm UBND cấp tỉnh; `luat-anm-2018-p28-p5`        | grounded 2, ctx 2                                        |
| test\_absent\_01 | Thiếu bằng chứng | retrieval hybrid → không có số đường dây nóng | Từ chối trả lời, không citation                          | abstention đúng — rà soát PDF không tìm được             |
| test\_absent\_02 | Thiếu bằng chứng | retrieval hybrid → không có độ dài khóa (bit) | Từ chối trả lời, không citation                          | abstention đúng — rà soát PDF không tìm được             |


- **Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:** trace gốc theo thư mục `artifacts/dev-hybrid-v2/`, `artifacts/dev-tfidf-agent/`, `artifacts/test-hybrid/`, `artifacts/test-tfidf/`; nhãn và lý do ở `artifacts/reviews-dev-tfidf.json`, `reviews-dev-hybrid-v2.json`, `reviews-test-tfidf.json`, `reviews-test-hybrid.json`; bản gộp `traces-*-reviewed.json`. Lệnh chạy: xem `src/README.md` và `docs/HUONG-DAN-TIEP-TUC.md`.
  - **Thời gian (median lượt thực tế):** dev TF-IDF ≈3361 ms, dev hybrid ≈4184 ms; test TF-IDF ≈3182 ms, test hybrid ≈4166 ms. Chịu ảnh hưởng mạng/API, không đại diện benchmark hạ tầng ổn định.
  - **Token LLM test:** TF-IDF vào/ra 3557/636; hybrid 5127/569 (chưa gồm token embedding).
  - **Chi phí API (`service_cost_usd`): chưa đo** — cần đối chiếu OpenRouter Usage; **không ghi 0**. TF-IDF baseline không gọi embedding trong lượt chạy; hybrid gọi embedding cho query.
- **Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:** budget 800→1600 nâng Context Evidence 13/17→16/17 nhưng tăng token vào và thời gian (hybrid chậm hơn TF-IDF ~800–1000 ms/câu do gọi embedding). test TF-IDF câu 01 trả "hình thức hợp tác" thay vì "nguyên tắc" vì context thiếu evidence; câu 02 chỉ nêu quyền bảo vệ — hybrid giữ đúng evidence cả hai. **Đánh đổi:** hybrid chất lượng cao hơn, chi phí/thời gian cao hơn; TF-IDF rẻ và nhanh nhất nhưng recall context kém.

## Giới hạn và tái lập

- **Giới hạn:** mẫu nhỏ; câu thiếu evidence dựa vào rà soát PDF trích xuất, chưa xác nhận tuyệt đối mọi cách diễn đạt — cần học viên đọc lại PDF. TF-IDF tách từ đơn giản; hybrid chỉ lấy 3 ứng viên mỗi nguồn. Hệ thống demo không xác minh hỗ trợ ngữ nghĩa hay chặn mọi citation không hợp lệ trước khi trả lời; chưa lưu error chuẩn cho mọi lỗi provider. Chỉ chạy một lần, chưa có khoảng tin cậy. **Không làm thử thách nâng cao.**
- **Cách tái lập:** xem `docs/HUONG-DAN-TIEP-TUC.md` và `src/README.md`. Cần repo Day 6, PostgreSQL/pgvector và API key riêng; tài liệu phải có quyền sử dụng. Không đưa `.env`/key vào repo. Dữ liệu và trace công khai ở `data/` và `artifacts/`; các thư mục kết quả starter khác bị `.gitignore`. Chạy test: `python -m pytest tests/` (15 passed).

## Thử thách nâng cao

Không thực hiện.