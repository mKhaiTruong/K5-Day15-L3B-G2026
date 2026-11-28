# Tóm tắt mô phỏng simulate-1@20261128-201545

Do `python run.py simulate` sinh ra — không sửa tay. Chép bảng sang `cost/cost-estimate.md`.

| Persona | Số phiên mô phỏng | Lượt hỏi / phiên | Token vào / phiên | Token ra / phiên | Gọi model / phiên | Gọi công cụ / phiên |
|---|---:|---:|---:|---:|---:|---:|
| dung_it | 23 | 1 | 1033 | 1858 | 1.0 | 11.0 |
| dung_vua | 19 | 3 | 2672 | 5673 | 2.5 | 30.5 |
| dung_nhieu | 8 | 5 | 3732 | 6528 | 3.5 | 41.1 |

Tỉ lệ đạt dùng để tính: 15/22 (68%) — lượt run-2@20261128-124725

- Tỉ lệ đạt lấy từ lượt nhóm chọn: eval/run-2.csv (--rate-from).

| Model (giá) | Chi phí / phiên | Chi phí / task thành công | Chi phí / câu hỏi đạt | Chi phí / tháng — thấp (300 người) | Chi phí / tháng — cơ sở (700 người) | Chi phí / tháng — cao (1.000 người) | Chi phí / người / tháng (cơ sở) |
|---|---:|---:|---:|---:|---:|---:|---:|
| gpt-5-mini (vào 0.25 · ra 2.0 $/1M) | $0.0086 | $0.0127 | $0.0053 | $29.98 | $69.96 | $99.94 | $0.0999 |
| openai/gpt-5-mini (vào 0.264 · ra 2.11 $/1M) | $0.0091 | $0.0134 | $0.0056 | $31.63 | $73.81 | $105.45 | $0.1054 |
| gpt-5.4-mini (vào 0.75 · ra 4.5 $/1M) | $0.0198 | $0.0291 | $0.0121 | $68.87 | $160.69 | $229.56 | $0.2296 |

- Chi phí / task thành công = chi phí / phiên ÷ tỉ lệ đạt. Chi phí / câu hỏi đạt = chi phí / phiên ÷ số lượt hỏi trung bình mỗi phiên (2.4) ÷ tỉ lệ đạt — tỉ lệ đạt đo theo từng câu thử.
- Token đo trên model: openai/gpt-5-mini. Giá tính theo từng model trong bảng — model khác bộ tách token thì số token thật có thể lệch; ghi rõ "đo trên model X, tính giá model Y" trong cost/cost-estimate.md.
- Phiên lỗi (không tính vào trung bình): 0/50.
