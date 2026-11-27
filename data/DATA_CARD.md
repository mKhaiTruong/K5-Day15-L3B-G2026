# Data card — dữ liệu bản chạy thử dùng



Tóm tắt: 4 dataset, **không có data `synthetic`**. Trong repo: bộ câu thử (Dataset 4) và gói kiến thức tự viết lại (Dataset 2); repo lab và data BTC để ngoài repo (gitignored)

## Dataset 1 · Repo lab của khoá

| | |
|---|---|
| Dùng để làm gì | Input của lõi: `tim_repo`, `kiem_ham_ton_tai`… đọc repo qua `LABS_DIR` · nguồn đáp án cho bộ câu thử (`source = data_that`) |
| Từ đâu | Repo lab BTC phát cho học viên AI20K K5 (README, CHECKPOINTS, TODO, ghi chú "không sửa" trong chính lab) |
| Xử lý những bước gì | Không sửa nội dung. Chỉ đọc file (`ast`, không chạy code). Đáp án benchmark lấy từ README / CHECKPOINTS / TODO, không tự suy |
| Số dòng / số đoạn | 4 lab, 13 câu thử `data_that`: Day04 (4) · Day14 (4) · Day13 (4) · Day07 (1) |
| Phiên bản / ngày lấy | Day04 `@dfdc975` · Day07 `@c67ec62` · Day13 `@4f3f1a6` · Day14 `@83e677f` |
| Nhãn | thật |
| Giới hạn | Mới phủ 4/13 ngày có lab. Để ngoài repo (`data/labs/` gitignored hoặc `LABS_DIR`), máy không có lab thì lõi không chạy được câu đó |

## Dataset 2 · Gói kiến thức (slide bài giảng)

| | |
|---|---|
| Dùng để làm gì | Căn cứ cho `tim_slide` (tìm đoạn slide theo khái niệm) và `ma_slide_ton_tai` (bắt mã slide bịa) |
| Từ đâu | Slide buổi Day13 "Launch & Economics" (`docs/Ngay13_Slide_Launch_Economics.pdf` trong repo lab Day13) |
| Xử lý những bước gì | Chọn các trang benchmark trích (tr.12, 14, 17) · nhóm **viết lại bằng lời mình**, không chép nguyên slide · đánh mã `Day13-s<trang>` · lưu `data/knowledge/Day13/slides.md` |
| Số dòng / số đoạn | 3 đoạn: `Day13-s12` chi phí mỗi việc thành công · `Day13-s14` chạy lại · `Day13-s17` phân tích độ nhạy |
| Phiên bản / ngày lấy | Slide trong repo lab Day13 `@4f3f1a6` · viết lại 27/11/2026 |
| Nhãn | thật (bản viết lại từ tài liệu khoá) |
| Giới hạn | Mới có 1 ngày, 3 trang · bản viết lại có thể lệch ý slide gốc · commit bản viết lại (không commit nguyên slide) để người chấm chạy lại `run.py eval` được; lab chưa có gói thì `tim_slide` trả rỗng và mọi khái niệm ghi `khong_co_can_cu` |

## Dataset 3 · Data preclass BTC

| | |
|---|---|
| Dùng để làm gì | Chỉ để đào bằng chứng pain (`evidence/data-mining.md`). Không đưa vào sản phẩm, không đưa vào model |
| Từ đâu | Data BTC cấp: `data/preclass/` trong repo đề `K5-L3-Day15-AI-Product-Hackathon` · bản local ở `data-btc/preclass/` |
| Xử lý những bước gì | BTC đã ẩn danh (mã `L0001…`, `A00001…`, không có tên / email / câu chữ học viên) · nhóm lọc theo `nguon`, `lan_thu = 1`, mốc 07/11 cho `giai_thich` · đếm bằng `evidence/count_answers.py`, `evidence/count_lab.py` (chỉ thư viện chuẩn) |
| Số dòng / số đoạn | Dùng chính `answers.csv` 3.776 dòng · gói còn `events.csv` 107.709 · `learners.csv` 721 · `chat.csv` 1.260 |
| Phiên bản / ngày lấy | 05/11 → 25/11/2026, Day01–Day13 · lấy 27/11/2026 |
| Nhãn | thật |
| Giới hạn | Mini lab trên trang pre-class ≠ repo lab GitHub (tín hiệu gián tiếp) · không có câu chữ học viên viết · `giai_thich` chỉ 20 dòng · `rubric_y_moi` do AI chấm. Repo chỉ chứa số đã tổng hợp và mã dòng ví dụ |

## Dataset 4 · Bộ câu thử

| | |
|---|---|
| Dùng để làm gì | Chấm lõi bằng `python run.py eval` theo `eval/metric_spec.yaml` |
| Từ đâu | Nhóm viết (Khánh), đáp án lấy từ Dataset 1 và 2 |
| Xử lý những bước gì | Mỗi câu ghi `source`: 13 câu `data_that` (lab và slide thật) · 5 câu `tu_viet` (repo không phải lab, thiếu thông tin, 2 câu tấn công) |
| Số dòng / số đoạn | 18 câu: `thuong` 7 · `kho` 7 · `tu_choi` 4 · `data_that` 13/18 |
| Phiên bản / ngày lấy | `eval/benchmark.csv` trên `main`, 27/11/2026 |
| Nhãn | thật (`data_that`) · nhóm tự viết (`tu_viet`), Khánh dùng Claude Code hỗ trợ soạn B06–B18, đáp án đối chiếu README / CHECKPOINTS của lab |
| Giới hạn | Chưa có câu `nguoi_dung` (chờ Google Form / phỏng vấn) · lệch về Day04 và Day14 · chưa đủ 20–30 câu cho CP3 |
