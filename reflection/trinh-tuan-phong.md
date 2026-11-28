# Reflection — Trịnh Tuấn Phong

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
Mình phụ trách feature 3, phiên Feynman (`codebase/feynman.py`, `tests/test_feynman.py`, kịch bản mức 3 `data/knowledge/Day13/kich_ban.json`, commit `98b43b9`, PR #17). Agent đóng vai người mới hỏi theo 3 mức: M1 giải thích bằng lời thường (AI chấm, chỉ đối chiếu đoạn slide), M2 chỉ ra `file:hàm` (code chấm), M3 đoán khi đổi điều kiện (đáp án là số đã chạy sẵn trên slide, không chạy code lab).
Trước đó mình viết `data/DATA_CARD.md` và gói kiến thức Day13 `data/knowledge/Day13/slides.md` (s12, s14, s17) (`0f736a2`, `4c51d62`, PR #8). Mình cũng sửa lõi để `tim_file_khung` bỏ qua ghi chú `.md` trong thư mục ẩn của repo đã làm (`06c2094`, PR #16), và điền slide trang 3–8 của `demo-slides.pdf` theo số `run-1`, `run-2` (`49daff4`, PR #29).

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
Mình dùng Claude Code (Claude Opus) để viết `feynman.py` + test, data card, tóm tắt slide Day13 và điền slide demo. Những chỗ không tin được ngay output AI, phải tự đối chiếu nguồn:
- Kịch bản `s17-do-nhay-xem-lai` dùng số "tỉ lệ chạy lại 3.743 → 3.829 đ" nhưng `slides.md` không có. Mình mở PDF slide gốc Day13 trang 17 để xác nhận số có thật rồi mới thêm vào `slides.md` (`6e2fdd0`), vì M1 chỉ chấm dựa trên `slides.md`.
- Trên slide demo, mỗi lỗi đưa vào đều đối chiếu với `eval/run-*.csv` và trace. Ví dụ B14: đọc trace mới biết chính model trả `main.py:ask`, không phải bước 6 làm mất hàm `health`. Ô nào chưa có số simulate thì để "chờ", không điền số đoán.
- Lỗi mình bỏ sót: câu hỏi M1 bảo học viên "nói bằng lời thường", nhưng prompt chấm `SYSTEM_M1` lại đòi "các ý chính của đoạn slide". Đoạn `Day13-s14` chứa 3 khái niệm kèm công thức, nên giải thích đúng bằng lời vẫn bị chấm "còn thiếu công thức". Test M1 của mình dùng model giả (`monkeypatch` `call_model`), nên chỉ kiểm logic, không bắt được chỗ câu hỏi và prompt chấm mâu thuẫn nhau. Phải chạy model thật với một câu giải thích đúng mới thấy. Mình hết token trước CP4 nên Khuê sửa prompt giúp ở PR #34, để quay video demo.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
B08 ("Lab Day13, CP1. Công thức chi phí trong bài giảng được viết thành những hàm nào?") dùng chính gói kiến thức Day13 của mình. Ở lượt 1, agent trỏ đủ 4 hàm nhưng phần slide ra `khong_co_can_cu`, dù đoạn `Day13-s12` có trong gói. Lý do: model chép mã thành `[Day13-sNN]` có ngoặc vuông, bước 6 so khớp chặt nên bỏ mất mã đúng. Sau khi sửa lõi đọc được mã có ngoặc, lượt 2 qua (trích được `Day13-s12` / `s14`).
Mình học được rằng một bước kiểm quá chặt, hoặc một nguồn thiếu, sẽ làm hệ thống nói "không có căn cứ" khi thật ra có căn cứ. Lỗi này khó thấy hơn lỗi bịa, vì output trông vẫn "an toàn". Với F3 cũng vậy: gói kiến thức là nguồn duy nhất để chấm, nên mọi số dùng trong kịch bản phải có trong gói và đối chiếu được với slide gốc.
