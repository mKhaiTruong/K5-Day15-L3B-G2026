# Reflection — Cung Đức Anh

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
Mình phụ trách tổng hợp bằng chứng pain (`evidence/summary.md`, commits `3f8e195`, `0cfd96f`, `95d9def`), xây dựng Feature 2 heatmap ẩn danh (`codebase/f2_heatmap.py`, `tests/test_f2_heatmap.py`, commits `e892683`, `a2eaef5`, `b457dda`), đóng góp phần `data/DATA_CARD.md` (commits `0f736a2`, `4c51d62`), và cùng Phong dựng `demo-slides.pdf`.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
Mình dùng Antigravity và Claude Code/ChatGPT để phác thảo code module `f2_heatmap.py` kèm unit test, tổng hợp bảng số liệu trong `evidence/summary.md`, và dựng layout HTML/CSS xuất `demo-slides.pdf`. Tuy nhiên nhiều chỗ vẫn phải tự kiểm và sửa lại output AI: tách rõ mẫu số `luot_hoi` vs `nguoi` ẩn danh trong `f2_heatmap.py` (commit `b457dda`), bỏ tính `%` khi cỡ mẫu nhỏ `n = 12` để đúng luật nhóm (commit `0cfd96f`), và chỉnh lại giao diện slide từ cuộn dọc sang dạng next từng trang không bị cắt chữ ở footer.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
Trong lúc test lõi trên repo thật, nhóm gặp lỗi nối hàm ngoài chủ đề và trích slide không khớp (như `Day13 CP1` gắn nhầm 6 hàm thống kê vào `Day13-s17`). Bài học rút ra là không thể chỉ nhắc LLM bằng prompt, mà phải thu hẹp ngữ cảnh đầu vào bằng code (chỉ đưa các hàm thuộc đúng CP đang hỏi) kết hợp kiểm tra lại đầu ra bằng code ở bước 6. *(Sau khi có kết quả cuối ở `eval/report.md`, bổ sung thêm mã câu thử cụ thể nếu cần.)*
