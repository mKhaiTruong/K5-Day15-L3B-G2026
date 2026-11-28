# Gói kiến thức Day13 — Launch & Economics

> Nhóm tự viết lại từ slide buổi Day13 (`docs/Ngay13_Slide_Launch_Economics.pdf` trong repo lab Day13), chỉ các trang benchmark trích.
> Không phải nguyên văn slide. Mỗi đoạn mở đầu bằng `## Day13-s<trang>` để `codebase/tools.py` đọc.

## Day13-s12
Chi phí mỗi việc thành công  = (token + tool + chạy lại + xem lại + làm lại) ÷ số việc thành công.
Tử số được tính với mọi lần chạy, kể cả những lần bị hỏng. Mẫu số chỉ đếm việc đã thành công, nên chi phí của lần hỏng sẽ dồn vào các việc thành công.
Phải định nghĩa về "thành công" trước khi tính.

## Day13-s14
Chạy lại: mỗi lần chạy đúng với xác suất thành công p, nếu lỗi thì cho phép chạy lại tối đa đến k lần. Tử số và mẫu số cùng tăng.
Số lần chạy kỳ vọng = (1 − (1 − p)^k) ÷ p. 
Tỉ lệ thành công = 1 − (1 − p)^k.
Chi phí mỗi việc thành công = số lần chạy ÷ tỉ lệ thành công = 1 ÷ p lần giá một lần chạy, không đổi theo k.
Ví dụ p = 0,8, k = 2: 1,20 lần chạy, tỉ lệ thành công 96%, hệ số chi phí 1,25.

## Day13-s17
Phân tích độ nhạy: nếu đổi từng yếu tố một, giữ các yếu tố khác như mốc tháng 10 (3.771 đ mỗi việc thành công), xem chi phí đổi bao nhiêu.
Nhạy nhất là tỉ lệ cần xem lại (5% → 30%: 2.343 → 5.914 đ). Giá token và tool ít nhạy (100 → 400 đ: 3.600 → 4.114 đ). Tỉ lệ chạy lại ít nhạy nhất (10% → 40%: 3.743 → 3.829 đ).
Kết luận: thời gian nhân viên quan trọng hơn giá token.
