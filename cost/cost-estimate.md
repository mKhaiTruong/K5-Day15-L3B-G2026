# Chi phí khi dùng thật

> Số lấy từ `cost/simulate-1-summary.md` (do `python run.py simulate` sinh). Chi phí tính theo giá gói trả phí.

## 1. Đầu vào

- **Persona** (`cost/personas.yaml`), cả ba kiểu đều **(tự ước tính)**, chưa có số đo tần suất dùng:

| Persona | Tỉ lệ người dùng | Phiên / người / tháng | Lượt hỏi / phiên |
|---|---:|---:|---:|
| dung_it | 50% | 4 | 1 |
| dung_vua | 30% | 10 | 3 |
| dung_nhieu | 20% | 20 | 5 |

- **Số người dùng thật:** thấp 300 · cơ sở 700 · cao 1.000. Cơ sở: lớp L3 hơn 700 học viên (README repo đề); thấp và cao *(tự ước tính)*
- **Giá** (USD / 1 triệu token vào · ra, xem `cost/personas.yaml` cho link và ngày xem): `openai/gpt-5-mini` qua OpenRouter 0,264 · 2,11 (gồm phí nạp credit 5,5%) · `gpt-5-mini` 0,25 · 2,00 · `gpt-5.4-mini` 0,75 · 4,50
- **Tỉ lệ đạt:** 15/22 (68%), lượt `run-2@20261128-124725`. Lượt này **chưa đạt chuẩn** của nhóm (cần ≥ 80%)
- **Token đo trên** `openai/gpt-5-mini`; hai dòng giá còn lại dùng **cùng số token đó**, model khác có thể ra số token khác
- Mỗi lượt hỏi lấy ngẫu nhiên một câu `thuong` / `kho` trong `eval/benchmark.csv`, không phải câu hỏi thu từ người dùng thật

## 2. Kết quả mô phỏng

Lượt mô phỏng: `cost/simulate-1.csv` · run ID `simulate-1@20261128-201545` · 50 phiên · seed 42 · 0 phiên lỗi · cache tắt · trace `traces/simulate-1.jsonl`

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 23 | 1 | 1033 | 1858 | 1.0 | 11.0 |
| dung_vua | 19 | 3 | 2672 | 5673 | 2.5 | 30.5 |
| dung_nhieu | 8 | 5 | 3732 | 6528 | 3.5 | 41.1 |

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (300 người) | Chi phí / tháng — cơ sở (700 người) | Chi phí / tháng — cao (1.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-5-mini (vào 0.25 · ra 2.0 $/1M) | $0.0086 | $0.0127 | $0.0053 | $29.98 | $69.96 | $99.94 | $0.0999 |
| openai/gpt-5-mini (vào 0.264 · ra 2.11 $/1M) | $0.0091 | $0.0134 | $0.0056 | $31.63 | $73.81 | $105.45 | $0.1054 |
| gpt-5.4-mini (vào 0.75 · ra 4.5 $/1M) | $0.0198 | $0.0291 | $0.0121 | $68.87 | $160.69 | $229.56 | $0.2296 |

- Chi phí / task thành công = chi phí trung bình mỗi phiên ÷ tỉ lệ đạt (không coi như đạt 100%). "Task" ở đây là một phiên

## 3. So với impact

- **Impact** (`spec.md` §2): ≈ 4.375 lượt "xong lab mà không nối được khái niệm với code" / tháng, tức ≈ 6,25 lượt / người / tháng khi chia cho 700 người
    - **(tự ước tính):** phép nhân 700 × 15/48 × ~20 lab giả định tỉ lệ 15/48 lặp lại ở mỗi lab. Data chỉ cho biết 15/48 học viên sai ít nhất 1 lần trong cả đợt dữ liệu, đo trên mini lab của trang pre-class
    - Chưa quy ra giờ hay tiền: chưa có số phút mỗi lượt (phỏng vấn 0/3)
- **Chi phí** (cơ sở, `openai/gpt-5-mini`): **$0,1054 / người / tháng** · $73,81 / tháng · chia đều cho 4.375 lượt là ≈ $0,017 / lượt
    - Phép chia này giả định toàn bộ chi phí phục vụ các lượt đó; **không cho biết sản phẩm gỡ được bao nhiêu lượt** (chưa đo)
- **Kết luận một dòng:** chi phí model thấp (≈ $0,11 / người / tháng) nên không phải rào cản; chưa đủ căn cứ để mở rộng, vì tỉ lệ đạt 68% dưới chuẩn 80% và chưa đo được mức giảm impact → **làm tiếp để sửa lỗi và đo, chưa triển khai rộng**

## 4. Độ nhạy và giới hạn

- **Tỉ lệ đạt:** mô phỏng chỉ hỏi câu `thuong` / `kho`, nhưng khung chia cho tỉ lệ đạt của cả 22 câu (gồm 5/5 câu từ chối). Nếu chỉ tính nhóm `thuong` + `kho` của lượt 2 (10/17), chi phí / task thành công là **$0,0155** thay vì $0,0134
- **Giá model:** cùng số token, `gpt-5.4-mini` tốn $160,69 / tháng ở mức cơ sở, gấp ≈ 2,2 lần $73,81; tỉ lệ đạt của model này chưa đo
- **Số lượt dùng** là *(tự ước tính)* và chi phí tháng phụ thuộc trực tiếp vào nó
- **Chưa tính:** hosting, lưu trữ, giờ công người duyệt / cập nhật gói slide, chi phí gọi model của Feynman (F3)
