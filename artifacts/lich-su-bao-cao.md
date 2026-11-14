## Lịch sử làm việc trước khi đánh giá test

> Bản làm việc chưa hoàn chỉnh. Kết quả test độc lập, nhãn chấm agent đầy đủ và chi phí API chưa được xác nhận; không dùng báo cáo này để khẳng định đã hoàn thành bài.

## Tiến độ thực tế

- Corpus Day 6: Luật An ninh mạng số 24/2018/QH14, 32 trang PDF; nguồn và thông tin sử dụng xem manifest Day 6. Index B có 169 chunk, PostgreSQL 16.16, pgvector 0.8.7, embedding `openai/text-embedding-3-small` qua OpenRouter, 1536 chiều, cosine.
- So sánh retrieval trên cùng 17 câu dev có đáp án, không filter, top-3. TF-IDF: Hit@1 11/17, Hit@3 13/17, context 11/17. Dense: 12/17, 13/17, 12/17. Hybrid RRF (lấy 3 ứng viên mỗi nguồn, RRF k=60): 13/17, 16/17, 13/17. Các cấu hình dùng context 800 ký tự; đây không phải kết quả agent test.
- Hybrid giữ nguyên ranking và tăng budget từ 800 lên 1600 ký tự: context evidence 13/17 lên 16/17; context trung bình từ khoảng 591 lên 1336 ký tự. Đổi budget không đổi Hit@1/Hit@3. Chưa đo tác động đến chi phí và chất lượng câu trả lời.
- Trace agent hybrid đã chạy trên 19 câu dev, gồm 17 câu có đáp án và hai câu dự kiến thiếu bằng chứng. Hai nhãn thiếu bằng chứng cần tiếp tục đối chiếu toàn văn trước khi chốt. Q01 và Q02 là trace đã tạo trước đợt chạy; các câu còn lại tạo sau. Tất cả cần review thủ công; chưa tổng hợp điểm grounded answer hay abstention chính thức.
- Lỗi dev: q03 và q04 tạo citation dạng `[chunk-id: ...]`, không khớp ID thực trong context. Sau khi thay chỉ dẫn trích dẫn, chạy lại riêng q03 và q04 đều có ID hợp lệ trong hai lần thử; model có tính ngẫu nhiên, chưa chứng minh sửa được mọi trường hợp. Trace trước: `starter/results/dev-agent/q03.json`, `q04.json`; sau: `starter/results/improvement-q03.json`, `improvement-q04.json`.
- Lỗi dev khác: q12, q15, q16 tìm thấy evidence trong hybrid top-3 nhưng context budget 800 không giữ được; thử 1600 giữ được cả ba. Kết quả trong `starter/results/dev-hybrid/` và `starter/results/dev-hybrid-1600/`.
- Cần review q11: model nêu thêm thông tin sai sự thật và xúi giục phạm tội như các ví dụ cùng nhóm tuyên truyền chống Nhà nước, trong khi các mảnh context trích dẫn thuộc những nội dung khác; không mặc nhiên coi toàn bộ phân loại đó được hỗ trợ. Các citation còn chứa tiền tố sai. Đây là lỗi nội dung tiềm năng, chưa có kết quả khắc phục.
- Kết quả hybrid retrieval dùng ranking dense đã lưu: thời gian offline không tính embedding/API và không thể so trực tiếp với thời gian end-to-end. Trace agent cũ có trung vị khoảng 3732 ms trên 19 lượt; không phải thống kê trên test. Chi phí chưa đo.
- Chưa chốt và chạy test độc lập; chưa so sánh agent baseline và agent cải thiện trên cùng test. Một số kết quả trong `starter/results/` bị `.gitignore` và cần được chia sẻ có chủ đích hoặc có hướng dẫn tái tạo.
- Đã tạo `data/test_draft.json`: 5 câu dự kiến có đáp án và 2 câu dự kiến thiếu evidence. Đã kiểm tra 5 evidence trùng nguyên văn chunk đúng nguồn/trang; hai câu thiếu evidence chưa được đọc đối chiếu toàn văn. Chưa chạy test, chưa có kết quả test.
- Snapshot trace dev và các bảng retrieval được sao chép sang `artifacts/` để không mất do `.gitignore`. Các trace giữ trạng thái `pending_review`, không được xem là nhãn chấm chính thức.

## Dữ liệu và benchmark

- Nguồn, quyền sử dụng, số trang và số chunk:
- Vector store, embedding model, phiên bản và số chiều:
- Agent model, cách chạy và phân chia dev/test:
- Cách xác định câu có/thiếu evidence và tiêu chí chấm:

## Retrieval và thử nghiệm

| Cấu hình | Phương pháp, top-k, filter, rerank, context budget | Giả thuyết / thay đổi | Split | Hit@1 | Evidence Hit@3 | Context Evidence Rate | Thời gian / chi phí |
|---|---|---|---|---|---|---|---|
| Baseline | | | dev | | | | |
| Phương pháp 2 | | | dev | | | | |
| Phương pháp 3 | | | dev | | | | |
| Cải thiện 1 | | | dev | | | | |
| Cải thiện 2 | | | dev | | | | |
| Cấu hình đã chọn | | | test | | | | |
| Baseline | | | test | | | | |

Một cấu hình có thể đồng thời là phương pháp mới và cải thiện; giải thích rõ. Báo `n/N` và tỷ lệ, ghi đơn vị thời gian/chi phí, so sánh test sau khi chốt. Nêu hai lỗi dev, nguyên nhân, cách thử và lý do chọn cấu hình:

## Agent và đánh giá

- Tool, số lượt gọi, điều kiện dừng, cách chọn context và xử lý lỗi:

| Cấu hình / split | Tool use | Số lượt gọi | Grounded answer 0/1/2 và trung bình | Citation hợp lệ | Câu có citation | Abstention đúng | Từ chối nhầm |
|---|---|---|---|---|---|---|---|

| Query ID | Loại câu | Tool call và kết quả | Câu trả lời và citation | Nhãn, lý do |
|---|---|---|---|---|

- Đường dẫn trace, nhãn, lệnh chạy, thời gian và chi phí:
- Kết quả trước/sau, ví dụ lỗi, đánh đổi và giới hạn:

## Thử thách nâng cao (nếu thực hiện)

- Tài liệu, nguồn, quyền sử dụng, số trang và phiên bản:
- Cách xử lý text, bảng, ảnh, biểu đồ; phạm vi index và phần chưa xử lý:
- Cách chia benchmark, schema evidence, model và cấu hình đã chốt trên dev:

| Nhóm test | Đạt / tổng | Tỷ lệ | Lỗi / nhận xét |
|---|---|---|---|
| Bảng | | | |
| Ảnh, sơ đồ | | | |
| Biểu đồ | | | |
| Multi-hop | | | |
| Text | | | |
| Thiếu bằng chứng | | | |
| **Toàn bộ** | | | |

- Trace, nhãn và evidence từng câu; thời gian, chi phí, lỗi hệ thống:
- Giới hạn, cách tái lập và đường dẫn benchmark:
