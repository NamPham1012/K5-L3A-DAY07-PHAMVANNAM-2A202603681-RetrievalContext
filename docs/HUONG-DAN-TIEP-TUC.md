# Hướng dẫn học và hoàn thành Day 7

Đây là hướng dẫn học lại các bước. Bản test và các nhãn do trợ lý chấm hiện có tại `artifacts/`, cần học viên review; xem kết quả cập nhật trong báo cáo. Một số hướng dẫn bên dưới mô tả thứ tự đã thực hiện, không yêu cầu chạy test lại để chỉnh model.

## 1. Xem retrieval và context

Trong Git Bash, kích hoạt môi trường Day 6, rồi xem `starter/results/dev-tfidf/summary.json`, `dev-dense/summary.json`, `dev-hybrid/summary.json` và `dev-hybrid-1600/summary.json`. Hit@3 hỏi evidence có trong ba kết quả đầu không; context hit hỏi evidence có còn trong context cuối không. Context 800 và 1600 dùng cùng ranking; tăng budget giúp giữ thêm ba evidence nhưng có thể tăng chi phí model.

## 2. Đọc trace agent dev

Thư mục `starter/results/dev-agent/` có 19 trace, trong đó q01/q02 được chạy trước. Mở một file JSON: đọc `question`, mỗi event `actual_query` và `context`, `answer`, `citations`, `invalid_citations`, `elapsed_ms`, token. Một ID hợp lệ không chứng minh câu được hỗ trợ. Q03 và q04 ban đầu thêm tiền tố `chunk-id:`. Xem `starter/results/improvement-q03.json` và `improvement-q04.json` để so sánh sau thay chỉ dẫn; không chỉnh trace cũ.

Đánh giá từng câu có đáp án: chấm 0, 1 hoặc 2 bằng cách đọc câu trả lời, đáp án và nội dung nguồn. Với mỗi citation, kiểm tra ID có trong context và đoạn đó hỗ trợ nội dung; lưu lý do. Với câu thiếu bằng chứng, xác nhận toàn văn trước khi ghi nhãn, rồi chấm agent có thực sự từ chối. Trạng thái `pending_review` chưa được script metric chấp nhận. Không tự đánh đồng lỗi model/tool với abstention.

## 3. Ghép và tổng hợp

Chuẩn bị riêng JSON arrays `cases`, `traces`, `reviews` theo `starter/README.md` và `starter/agent_metrics.py`. Tạo bản trace đã review, giữ nguyên trace gốc; gán `answered`, `abstain` hoặc `error` theo sự thật. Script metric loại các `error` và gọi chúng là provider_errors nên ghi rõ nguyên nhân thực tế ở báo cáo; không gộp một lần model không gọi tool thành lỗi provider nếu chưa xác định. Chạy `python starter/agent_metrics.py --cases <cases.json> --traces <traces.json> --reviews <reviews.json> --split dev --output <summary.json>` sau khi thay đường dẫn. Không gửi nhãn `answerable`, gold hoặc đáp án vào agent.

## 4. Tạo test độc lập và chạy đánh giá

Trước test hoàn tất đánh giá dev và ghi cấu hình chọn. `docs/chot-cau-hinh-dev.md` lưu cấu hình dự kiến; nếu thay đổi bằng dữ liệu dev, cập nhật lịch sử và ghi rõ trước khi chạy test. Chuẩn bị ít nhất 5 câu có đáp án mới với nguồn, trang và evidence, cùng 2 câu thiếu evidence được kiểm tra toàn văn. Không tái sử dụng test Day 6 đã xem để chỉnh. Chạy baseline và cấu hình chọn trên cùng test, lưu trace retrieval lẫn agent; đọc 5 câu có đáp án, 2 câu thiếu evidence và chấm citation/context theo BENCHMARK.md. Không điều chỉnh theo test; nếu dùng test để chỉnh, tạo test độc lập mới.

## 5. Hoàn thiện báo cáo

Điền `report/individual/2A202603681_PHAMVANNAM.md`: bảng kết quả n/N, nhãn và lý do từng câu, hai lỗi và trước/sau, token/chi phí đo được, thời gian, lỗi, hạn chế, nguồn và hướng dẫn tái lập. Nếu chưa có dữ liệu thì ghi chưa đo, không tự suy diễn. `starter/data/` và `starter/results/` bị Git bỏ qua: chia sẻ có chủ đích dữ liệu được phép hoặc cung cấp lệnh tái tạo; không commit `.env` và API key.

Code mặc định tìm repo Day 6 cạnh repo Day 7; có thể chỉ định `DAY6_STARTER`. Người chấm vẫn cần repo Day 6, PostgreSQL pgvector và API key riêng. Hiện đã có trace baseline và hybrid trên test nhưng chưa lưu mọi lỗi theo schema metric; code không tự đánh giá tính hỗ trợ ngữ nghĩa của citation. Học viên cần review nhãn trước khi nộp.
