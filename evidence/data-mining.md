# Đào data — cách đếm và kết quả

> Điền ở guide bước 1.2. Repo chỉ chứa số đã tổng hợp và vài mã dòng ví dụ, không chép lại nguyên file data.

## 1. Cách đếm — viết TRƯỚC khi chạy

- **Data dùng:** `data/preclass/answers.csv` do BTC cấp (3.776 dòng, 05/11 → 25/11/2026, Day01–Day13). Bản local ở `data-btc/preclass/`, gitignored.
- **Câu hỏi:** học viên làm qua mini lab có hiểu được khái niệm của lab đó không, và có tự giải thích lại không?
- **Đếm gì:**
    1. Tỷ lệ bước mini lab làm đúng ngay lần đầu
       - tập: `nguon = thuc_hanh`, `lan_thu = 1`
       - mẫu số: số bước đã làm lần đầu
    2. Trong số học viên có làm mini lab, bao nhiêu người từng tự giải thích
       - tập: học viên có ≥1 dòng `thuc_hanh` từ 07/11 (ngày `giai_thich` bắt đầu được ghi)
       - đếm: những người có ≥1 dòng `giai_thich`
       - mẫu số: số học viên làm mini lab từ 07/11
    3. **Qua lab nhưng sai khái niệm đó ở bài ôn cuối ngày**
       - với mỗi cặp (học viên, `kc_code`) đã làm đúng ≥1 bước mini lab, lấy các câu ôn cuối ngày cùng `kc_code`, lần đầu, có chấm đúng/sai
       - chỉ lấy câu trả lời **sau** lần đầu tiên làm đúng lab
       - mẫu số: số câu trả lời như vậy, và số học viên có ít nhất 1 câu như vậy
       - tập câu ôn: `nguon = pre_post_post`, `lan_thu = 1`, `was_correct` ∈ {True, False}
    4. Câu nhắn AI có ý riêng của học viên không
       - tập: `nguon = chat`, `trang_thai_cham = da_cham`
       - đếm: số câu có `rubric_y_moi = 0` (chép hoặc hỏi lại nguyên văn)
       - mẫu số: số câu chat đã chấm
- **Script:**
    - `evidence/count_answers.py`: đếm 2 và 4
    - `evidence/count_lab.py`: đếm 1 và 3
    - chỉ dùng thư viện chuẩn, chạy từ gốc repo: `python evidence/count_lab.py data-btc/preclass/answers.csv`

## 2. Đọc trước, đếm sau

Đã đọc `README.md` + `column_dictionary.csv` của data, và đếm phân bố theo `nguon`. Các kiểu hành vi thấy được:
- `pre_post_post` 1.970 dòng (ôn cuối ngày)
- `chat` 1.260 dòng
- `thuc_hanh` 519 dòng (bước mini lab)
- `giai_thich` chỉ 20 dòng (tự giải thích vì sao chọn đáp án)
- `video_quiz` 7 dòng
- Mọi dòng `thuc_hanh` và `pre_post_post` đều có `kc_code`, nên nối được "lab luyện khái niệm X" với "câu ôn hỏi khái niệm X".

## 3. Kết quả

| Đếm gì | x / N | % | Ghi chú |
|---|---|---|---|
| 1. Bước mini lab làm đúng ngay lần đầu | 480 / 503 | 95,4% | Qua lab rất dễ |
| 2. Học viên làm mini lab từng tự giải thích | 18 / 109 | 16,5% | Từ 07/11, khi `giai_thich` bắt đầu được ghi |
| 3a. Câu ôn cuối ngày sai, trên khái niệm học viên đã làm đúng ở lab | 20 / 148 | 13,5% | Chỉ tính câu trả lời sau khi đã qua lab |
| 3b. Học viên sai ≥1 khái niệm mình đã qua ở lab | 15 / 48 | 31,3% | Cùng tập với 3a |
| 4. Câu nhắn AI không có ý riêng (`rubric_y_moi = 0`) | 909 / 1.223 | 74,3% | Chép hoặc hỏi lại nguyên văn |

**Kết luận sơ bộ:**
- Qua lab gần như chắc chắn (95,4%), nhưng chỉ 16,5% người làm lab từng tự giải thích lại.
- Cứ khoảng 1/3 học viên (15/48) sai ở bài ôn đúng khái niệm mình vừa làm qua trong lab.
- Như vậy, ủng hộ một phần giả thuyết "qua lab ≠ hiểu khái niệm".

## 4. ≥5 ví dụ cụ thể (mã dòng đã ẩn danh)

Câu ôn cuối ngày làm sai, trên khái niệm học viên đã làm đúng ở mini lab trước đó:
1. `A03725`: `select_rule_workflow_agent_level`
2. `A00948`: `agentic_fit_scoring_decision`
3. `A00945`: `agentic_fit_scoring_decision`
4. `A02946`: `agentic_fit_scoring_decision`
5. `A00012`: `gate_severity_and_strictness`
6. `A02071`: `gate_severity_and_strictness`

## 5. Giới hạn của data

- **Mini lab ≠ repo lab GitHub.** Đây là bước thực hành trên trang pre-class, không phải repo lab hằng ngày mà sản phẩm nhắm tới. Số chỉ là tín hiệu gián tiếp.
- **Không có câu chữ học viên viết** (chỉ có độ dài), nên không biết vì sao họ sai.
- `giai_thich` chỉ có 20 dòng. Tỷ lệ thấp ở mục 2 có thể một phần do giao diện ít mời học viên tự giải thích, không hẳn vì học viên không muốn.
- Sai ở mục 3 có thể do câu ôn khó hơn lab, chưa chắc do không hiểu.
- `rubric_y_moi` là điểm giám khảo AI chấm, chưa kiểm lại bằng người.

→ Kiểm lại bằng Google Form (≥20 học viên): câu 4–5 hỏi khái niệm của lab vừa nộp và khái niệm đó nằm ở đâu trong code; câu 6 hỏi có mở lại slide đối chiếu không.
