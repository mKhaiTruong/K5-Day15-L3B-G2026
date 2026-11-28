# Báo cáo đánh giá — lượt 1 → một cải tiến → lượt 2

> Điền ở guide bước 4.1. Lượt 1 trước **CP3 10:00 Thứ Bảy 28/11**, lượt 2 trước **CP4 14:30 Thứ Bảy 28/11**, cùng bộ câu thử, cùng cách chấm. Chấm ở rubric R5.
> Số lấy từ `python run.py score eval/run-1.csv` (và `run-2.csv`) sau khi điền cột `pass`. **Kết quả thấp ghi thật vẫn đủ điểm.**
> Không được: sửa chuẩn "đạt", bỏ câu thử trượt, sửa `expected` cho khớp output, sửa kết quả lượt đã chạy.

## 1. Kết quả

| Lượt | Run ID | Đạt / tổng | % | thuong | kho | tu_choi | So với chuẩn "đạt" |
|---|---|---|---|---|---|---|---|
| 1 | `run-1@20261128-002639` | 12/22 | 55% | 5/9 | 4/8 | 3/5 | chưa đạt (55% < 80%, tu_choi 3/5) |
| 2 | `run-2@20261128-124725` | 15/22 | 68% | 5/9 | 5/8 | 5/5 | chưa đạt (68% < 80%); tu_choi 5/5, 0 câu gắn sửa file khung |

Kết quả từng câu: `eval/run-1.csv`, `eval/run-2.csv`. Trace: `traces/run-1.jsonl`, `traces/run-2.jsonl`.

## 2. Lỗi lượt 1 — gom thành nhóm có tên

| Nhóm lỗi | Số câu | Câu |
|---|---|---|
| vd: bịa nguồn *(ví dụ)* | | |
| vd: đoán khi thiếu thông tin *(ví dụ)* | | |
| | | |

**≥3 lỗi cụ thể:**

| Câu | Input | Output | Vì sao sai |
|---|---|---|---|
| | | | |
| | | | |
| | | | |

## 3. Một lần cải tiến

- Nhắm vào nhóm lỗi: **không từ chối khi bị ép / đòi dữ liệu từng bạn** (B18, B22) — vì sao là nhóm **đau nhất với người dùng**: bị ép coi repo ngoài khoá là lab thì trả bản đồ sai mà trông có căn cứ; lộ câu hỏi từng bạn là trái luật Track A
- Đã sửa gì: luật từ chối bằng code trước khi gọi model (PR #18); cùng đợt còn sửa timeout 60 → 120s (B11), đọc đúng mã slide, chỉ đưa model hàm mà TODO của CP chỉ tới (PR #21) — nhiều thay đổi cùng lúc, không tách được tác động từng cái (xem `eval/README.md`, `spec.md` §10)
- Kết quả: nhóm lỗi đó (tu_choi) 3/5 → 5/5 · tổng 55% → 68% (12/22 → 15/22)
- Câu nào **tệ đi** sau khi sửa: B19 (lượt 1 qua → lượt 2 gắn `main.py:ask` vừa `sua` vừa `doc`); mỗi câu chạy 1 lần nên có thể do model trả khác

## 4. Còn lại

- Lỗi chưa sửa + nguy hiểm thế nào: __
- Nếu có thêm 1 tuần: __
