# Reflection — Triệu Quốc Khánh

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
Mình phụ trách benchmark + eval: bộ câu thử `eval/benchmark.csv` (B06–B22), sửa `eval/metric_spec.yaml` trước khi khoá, thêm `eval/grade_metrics.py` (commit `27aafd8`), viết `spec.md` §5 (`b2a1e78`).
Chạy và ghi lượt 1 `run-1` 12/22 (`77d4b55`) và lượt 2 `run-2` 15/22 (`2cbb49c`), cùng `eval/README.md` và dòng kết quả ở §7. Thêm nhánh OpenRouter trong `codebase/ai.py` (`6342780`) sau khi Khuê đồng ý. Phần chi phí: `simulate` 50 phiên (mình chạy trên máy), `cost/cost-estimate.md`, §8, slide trang 6 (`505799c`).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
Mình dùng Claude Code cho phần lớn việc trên: soạn câu thử và đáp án từ code lab bản gốc, viết script chấm và nhánh OpenRouter, chạy hai lượt eval, chấm cột `pass`, điền phần chi phí, tạo PR; bản reflection này cũng do Claude Code soạn nháp. Mình chưa tự kiểm lại điểm `pass`.
Output AI đã phải sửa: bộ 12 câu đầu không theo format của nhóm, mình yêu cầu bỏ và viết lại theo PR #4; AI từng lấy nhầm commit gốc của lab Day04 (`8f08577`), sau đó đối chiếu lại thành `dfdc975` trước khi viết đáp án.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
B02 (Day14: health khác readiness chỗ nào trong code?). Cả hai lượt, lõi bảo viết `/health` bằng cách sửa `main.py:ask`, trong khi `health` là hàm phải tạo mới. Phần chấm bằng code vẫn cho qua, vì `tro_dung_code` chỉ cần một cặp file + hàm đúng (`redis_healthy`).
Bài học: metric chấm bằng code chỉ lọc được lỗi rõ. Vẫn cần người đọc theo `pass_criterion`, và lần sau nên viết metric đòi đủ các cặp bắt buộc trước khi khoá chuẩn.
