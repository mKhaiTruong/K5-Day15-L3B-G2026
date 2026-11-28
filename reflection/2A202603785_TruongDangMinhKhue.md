# Reflection — Trương Đặng Minh Khuê

> Làm ở guide bước 5.3. Mỗi người một file: chép file này thành `reflection/<ten-khong-dau>.md` (viết thường, không dấu). Hạn: **23:59 Thứ Bảy 28/11**. Mỗi câu 3–6 dòng.

1. Vai trò + phần mình làm (trỏ tới file / commit):
Mình là đội trưởng, phụ trách lõi `codebase/agent.py` + `tools.py` (workflow 6 bước, nối OpenAI `e2b7e34`, gắn nhãn theo TODO `25f8cd4`, từ chối repo ngoài khoá / dữ liệu từng bạn `331cc67`, chỉ đưa model hàm mà TODO của CP chỉ tới `6726a2e`) và feature 1 lộ trình + sơ đồ cấp hàm (`codebase/f1_lo_trinh.py`, `3a969eb`).
Mình làm giao diện web gom lõi + 3 feature (`codebase/web.py`, `codebase/web/index.html`, `0af9c35`, `9b5aa05`, tab "Lớp kẹt ở đâu" `a37c1fe`) và theo ý Phong cho app đọc repo đã làm xong của học viên qua link GitHub, lọc hàm theo `git diff` (`bbdbf6e`, `6cb7a78`).
Ngoài code: viết `spec.md` §0–§6, §9, chia việc (issue #9, #20), review / merge PR của nhóm và nộp checkpoint.

2. AI hỗ trợ mình thế nào (việc gì, công cụ gì, chỗ nào phải sửa lại output AI):
Mình dùng Claude Code (Claude Opus) để viết phần lớn code + test pytest, review PR, đối chiếu số liệu slide với data, và chụp màn hình UI bằng Edge headless để kiểm giao diện.
Những chỗ output AI sai và phải sửa lại, đều bắt được nhờ test, chạy thật hoặc nhìn ảnh chụp chứ không nhờ đọc lướt: bộ lọc TODO coi dòng docstring "TODO CP1…CP4" là TODO thật (CP4 bị gán nhầm hàm); route ảnh SVG bản đầu lọt được `..\` trên Windows; heatmap bản đầu đo "người sai ≥1 khái niệm" nên ô nào cũng đậm và Day chỉ 2–4 người vẫn được tô màu; sơ đồ SVG thu nhỏ tới mức không đọc được; một bản nháp `spec.md` ghi nhầm mã câu tấn công (B21 thay vì B05).
Bài học: việc mình phải làm là quyết hướng (vd đọc repo đã làm xong thay vì đề trống) và kiểm số trước khi merge; AI viết nhanh nhưng không tự biết khi nào số đo sai.

3. Một câu thử trượt của nhóm và mình học được gì từ nó:
B19 qua ở lượt 1 nhưng trượt ở lượt 2: cùng một câu, cùng code lõi, model lần sau gắn `main.py:ask` vừa `sua` vừa `doc`, nên học viên không biết có phải sửa hàm đó không. Lượt 1 → 2 tổng tăng 12/22 → 15/22, nhưng riêng câu này tệ đi mà không do mình đổi gì liên quan.
Mình học được hai điều. Một: mỗi câu chỉ chạy một lần thì chênh lệch từng câu có thể chỉ là model trả khác, không đủ để kết luận "cải tiến có tác dụng"; muốn chắc phải chạy mỗi câu ≥3 lần. Hai: luật "mỗi hàm chỉ một nhãn" không nên giao cho prompt mà phải ép bằng code ở bước 6, giống cách nhóm đã ép `khong_dung` cho file khung (0 câu sai ở cả hai lượt).
