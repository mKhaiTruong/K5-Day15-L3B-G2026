# Tổng hợp bằng chứng pain

> Điền ở guide bước 1.2, xong trước **CP3 10:00 Thứ Bảy 28/11**. Chấm ở rubric R1.
> Ba nguồn ngang nhau — tối thiểu **≥1 nguồn đạt ngưỡng**. Mạnh nhất: đào data ra insight → hỏi người dùng để kiểm lại (hoặc ngược lại).

## 1. Nguồn đã dùng

| Nguồn | Đạt ngưỡng? | File |
|---|---|---|
| Đào data (x/N, %, cách đếm chạy lại được, ≥5 ví dụ) | ☑ | `evidence/data-mining.md` |
| Phỏng vấn (≥3 người ngoài nhóm, đúng người dùng) | ☐ | — *(chưa thực hiện)* |
| Khảo sát (≥20 người ngoài nhóm, đúng người dùng) | ☐ | `evidence/survey/results.csv` *(12/20 người ngoài nhóm — dùng bổ trợ)* |

## 2. Số chính

- **Đào data** (`data/preclass/answers.csv`, 3.776 dòng, Day01–Day13):
  - `480/503` (`95,4%`) bước mini lab làm đúng ngay lần đầu, nhưng chỉ `18/109` (`16,5%`) học viên làm mini lab từng tự giải thích.
  - `15/48` (`31,3%`) học viên sai ≥1 khái niệm ở bài ôn cuối ngày dù đã làm đúng khái niệm đó ở mini lab trước đó (`20/148` câu ôn = `13,5%`).
  - `909/1.223` (`74,3%`) câu nhắn AI không có ý riêng (`rubric_y_moi = 0`).
- **Phỏng vấn:** `0/3` *(chưa thực hiện)*.
- **Khảo sát** (`n = 12` học viên ngoài nhóm; đã loại 4 phiếu của thành viên nhóm và xoá tên/email):
  - `11/12` code chủ yếu do AI viết (`6/12` gần như AI viết hết · `5/12` phần lớn AI viết, mình sửa · `1/12` tự viết hết).
  - `8/12` không tự tin diễn giải các checkpoint khi mới làm xong (`1/12` không chắc · `3/12` tự tin).
  - `10/12` không chỉ được chính xác khái niệm nằm ở file/hàm nào khi không mở code (`8/12` nhớ mang máng file, không nhớ hàm · `2/12` không chỉ được · `1/12` bỏ trống · chỉ `1/12` chỉ được chính xác).
  - `8/12` từng mở lại slide bài giảng để đối chiếu với code (`5/12` hơn 1 lần · `3/12` 1 lần · `4/12` chưa bao giờ / không).
  - `9/12` hỏi ChatGPT/Claude khi muốn hiểu lại lab (`2/12` chưa từng muốn · `1/12` hỏi bạn/mentor).

## 3. ≥5 trích dẫn hoặc ví dụ nguyên văn (có nguồn, bỏ tên)

*(6 ví dụ nguyên văn từ data preclass `data/preclass/answers.csv` — các học viên đều đã làm đúng bước mini lab `thuc_hanh` cùng `kc_code` trước đó, nhưng khi làm bài ôn cuối ngày `pre_post_post` lần 1 đều chọn sai; đã bỏ mã học viên):*

1. `A03725`: bài ôn `program-day02:ai-problem-definition`, mã câu hỏi `d02-on-can-agent` (`kc_code = select_rule_workflow_agent_level`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A03725` (`evidence/data-mining.md`)
2. `A00948`: bài ôn `program-day03:chatbot-to-agentic-agent`, mã câu hỏi `d03-on-tong-5-diem` (`kc_code = agentic_fit_scoring_decision`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A00948` (`evidence/data-mining.md`)
3. `A00945`: bài ôn `program-day03:chatbot-to-agentic-agent`, mã câu hỏi `d03-on-tong-5-diem` (`kc_code = agentic_fit_scoring_decision`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A00945` (`evidence/data-mining.md`)
4. `A02946`: bài ôn `program-day03:chatbot-to-agentic-agent`, mã câu hỏi `d03-on-tong-5-diem` (`kc_code = agentic_fit_scoring_decision`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A02946` (`evidence/data-mining.md`)
5. `A00012`: bài ôn `program-day06:data-engineering-for-agents`, mã câu hỏi `d06-on-gate-muc-canh-bao` (`kc_code = gate_severity_and_strictness`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A00012` (`evidence/data-mining.md`)
6. `A02071`: bài ôn `program-day06:data-engineering-for-agents`, mã câu hỏi `d06-on-gate-muc-canh-bao` (`kc_code = gate_severity_and_strictness`), lần thử 1 sai (`was_correct = False`), dù trước đó đã qua bước mini lab cùng `kc_code` — dòng data `A02071` (`evidence/data-mining.md`)

*(Ví dụ bổ trợ từ khảo sát Google Form đã ẩn danh — `evidence/survey/results.csv`:)*
- `P05`: `"Phần lớn do AI viết, mình sửa"` · tự tin diễn giải checkpoint: `"Không"` · chỉ file/hàm: `"Nhớ mang máng file, không nhớ hàm"` · mở slide đối chiếu: `"Có, 1 lần"` · cách hiểu lại: `"Hỏi ChatGPT/Claude"` — phiếu khảo sát `P05`

## 4. Các nguồn có khớp nhau không

Data nói `95,4%` bước mini lab qua ngay lần đầu nhưng chỉ `16,5%` từng tự giải thích và `31,3%` học viên sai lại chính khái niệm đã qua ở bài ôn cuối ngày. Khảo sát ngoài nhóm (`n = 12`) nói `11/12` code chủ yếu do AI viết, `8/12` không tự tin diễn giải checkpoint sau khi làm xong và `10/12` không chỉ được chính xác `file:hàm` của khái niệm — **hai nguồn khớp nhau** ở chỗ "làm qua bài ≠ hiểu khái niệm và không định vị được khái niệm trong code". Điểm bổ sung từ khảo sát: `8/12` từng chủ động mở lại slide để đối chiếu với code, chứng tỏ người học có nhu cầu nối bài giảng ↔ code chứ không phải bỏ qua slide.

## 5. Kết luận

Giả thuyết ở `evidence/hypothesis.md`: **đúng phần lớn** — vì cả data preclass (`15/48` sai khái niệm đã qua lab, `18/109` tự giải thích) lẫn khảo sát (`8/12` không tự tin diễn giải, `10/12` không chỉ được chính xác `file:hàm`, vượt ngưỡng `≥50%` đặt ra ở giả thuyết) đều cho thấy học viên làm xong lab nhờ AI nhưng bị đứt gãy giữa khái niệm bài giảng và vị trí `file:hàm` trong code. Điều vẫn chưa biết: trong 2 tuần qua `9/12` chọn `Chưa bị hỏi` về code đã nộp nên chưa đo được tỷ lệ bị hỏi vấn đáp thực tế; và chưa có phỏng vấn sâu (≥3 người) để đo số phút cụ thể mỗi lần tự nối slide với code.
