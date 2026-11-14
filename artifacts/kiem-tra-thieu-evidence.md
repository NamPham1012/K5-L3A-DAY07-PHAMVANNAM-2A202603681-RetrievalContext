# Kiểm tra sơ bộ câu thiếu bằng chứng

Người rà soát: trợ lý; học viên cần review kết luận. Nguồn: `starter/data/24-2018-qh14.pdf` ở repo Day 6, 32 trang; SHA-256 `7BA6B742325359B442B4E5A7A905DEFBA286EEDB39210F59A1D8983D3D916A4A`. Trích xuất toàn bộ 32 trang bằng pypdf `extraction_mode=layout`; 0 trang trống, 67.400 ký tự. Tìm không phân biệt hoa thường trong toàn văn và kiểm tra các đoạn khớp. Kết quả chỉ áp dụng tài liệu gốc này, không phải mọi văn bản hoặc quy định hiện hành.

- dev_absent_01: không thấy cụm `lệ phí`, `chứng chỉ` trong văn bản trích xuất; chưa tìm được mức lệ phí cấp chứng chỉ.
- dev_absent_02: không thấy `mật khẩu`, `độ dài`; chưa tìm được quy định về chiều dài mật khẩu.
- test_absent_01: không thấy `điện thoại`, `đường dây`, `liên hệ`; chưa tìm được số điện thoại đường dây nóng.
- test_absent_02: không thấy `bit`, `độ dài`; `khóa` chỉ xuất hiện ở trang 32 trong cụm `khóa XIV`. Các trang chứa `mật mã` là 2, 4, 11, 12, 17, 30, 31; không thấy quy định chiều dài khóa trong các đoạn trích. Trang 17 có `mã hóa` về sản phẩm, không có chiều dài khóa.

Đây là bằng chứng kiểm tra toàn văn trích xuất, không phải chứng minh tuyệt đối: lỗi trích xuất hoặc cách diễn đạt khác có thể bỏ sót. Cần học viên đối chiếu PDF khi review; đánh giá chỉ trong corpus, không suy luận pháp luật bên ngoài.
