# CLAUDE.md — context cho Claude Code trong repo G2026

@AGENTS.md

## Bối cảnh
- AI20K K5 Day15 Mini Hackathon, nhóm **G2026**, lớp **L3B**, 4 người (xem `TEAMS.md`). Đội trưởng: Trương Đặng Minh Khuê.
- Đề + rubric gốc: repo BTC `VinUni-AI20k/K5-L3-Day15-AI-Product-Hackathon` (`README.md`, `01-challenge-brief.md`, `02-guide.md`, `03-rubric.md`, `tracks/track-a-edtech.md`). Data BTC copy ở `data-btc/` (gitignored, không commit).
- Mốc: **CP1 17:00 27/11** · CP2 19:30 27/11 · CP3 10:00 28/11 · CP4 14:30 28/11 · nộp cuối 23:59 28/11. Nộp checkpoint: https://ai20k-hackathon.pages.dev/#submit
- Python: dùng `.venv/Scripts/python.exe` (Windows). LLM mặc định: OpenAI, key trong `.env`.
- **Lõi đã có code** (`codebase/agent.py` + `tools.py`, workflow 6 bước như `spec.md` §4):
    - đặt `LABS_DIR` trong `.env` = thư mục chứa repo lab (máy Khuê: `C:/Users/MINH KHAI/Documents/VinUni`)
    - chế độ AI giả dùng ghép dự phòng (khớp tên hàm); nối model thật ở `codebase/ai.py` (`docs/connect-model.md`)
    - test: `python -m pytest tests/` (pytest chỉ cài trong `.venv`, không thêm vào `requirements.txt`)
    - Windows in tiếng Việt lỗi encoding thì đặt `PYTHONIOENCODING=utf-8`
    - tên tool trong `tools.py` phải khớp bảng tool ở `spec.md` §4

## Hướng đang theo (tạm chốt 27/11, chưa có bằng chứng)
- **Track A.** Tên tạm: bản đồ bài giảng ↔ code lab theo CP.
- **Mục tiêu cuối:** học viên **hiểu bài lab và nối được với bài giảng**, không chỉ làm nhanh. Tìm file là phương tiện.
- **Người đau:** học viên AI20K đang làm hoặc vừa nộp lab, muốn hiểu bài; không biết khái niệm trong slide nằm ở file / hàm nào của lab, nên test xanh mà không giải thích được code.
- **Không phục vụ:** người kệ đời chỉ vibe code cho qua.
- **Nguồn kiến thức:** repo lab (README, CP, rubric, code) + slide bài giảng của buổi đó. ⚠️ Cần xác nhận team có slide.
- **Lõi (agent quyết định):** CP này luyện khái niệm nào → khái niệm nằm ở file / hàm nào (nhãn đọc / sửa / không đụng). Mỗi liên kết phải trích slide + code; không có căn cứ thì nói không có. Hỏi lại khi chưa rõ CP; từ chối khi repo không phải lab (test `tu_choi`).
- **Khác DeepWiki / ChatGPT / NotebookLM:** họ không có slide của khoá, hoặc không biết cấu trúc đề lab. Mình nối "khái niệm trong slide = hàm này trong lab" theo từng CP.
- **3 feature dùng chung lõi.** Nhóm tự chia thời gian, không ưu tiên feature nào trong tài liệu nộp.
    1. lộ trình file theo CP: ~5 file theo thứ tự + sơ đồ flow (skill `lab-cp-html` của 1 thành viên)
    2. heatmap: câu hỏi gộp ẩn danh → badge "🔥 x/N bạn hỏi ở đây" + trang "khái niệm / CP nào lớp kẹt nhất" cho người ra đề; < ~5 người thì ghi "chưa đủ dữ liệu"
    3. Feynman: agent đóng vai người mới hỏi, học viên giải thích lại; chấm đối chiếu slide + code; hổng thì trỏ lại đúng đoạn. Tự nguyện, không ai xem kết quả riêng
- **Learning metric (Track A bắt buộc):** quiz khái niệm của 1 lab trước / sau khi dùng app (~5 bạn cùng lớp).
- **Benchmark:** lab Day1–15 thật của khoá (`data_that`): input = lab + CP, expected = khái niệm + file / hàm; thêm repo không phải lab (`tu_choi`).

## Đã loại (đừng đề xuất lại)
- **Track B (B1/B2/B3):** 2 thành viên không muốn làm y tế. B2 rủi ro cao.
- **Chỉ tìm file cần sửa (bản đầu):** giúp làm nhanh, không chắc giúp hiểu. Giữ làm feature 1.
- **Feynman tutor đứng riêng:** không ai tự mở app để bị kiểm tra. Đã gộp thành feature 3.
- **Mentor dùng app để kiểm tra từng người:** thành công cụ giám sát, vi phạm luật Track A.
- **Gallery format tóm tắt repo:** trùng DeepWiki/GitDiagram; phần AI mờ.

## Việc tiếp theo
- **CP1:** đã viết `TEAMS.md` (Track A), `canvas.md`, `evidence/hypothesis.md`, `spec.md` §0–§2 (PR #2, issue #1). Phân công: Khuê lõi · Khánh benchmark + eval · Phong feature 1 · Đức Anh feature 2 + 3.
- **Trước CP2:**
    - phỏng vấn ≥3 học viên ngoài team (Mom Test): "lab nào bạn nộp trong 2 tuần qua? khái niệm chính của CP đó nằm ở hàm nào, sao code làm vậy? lần gần nhất bị hỏi về code mình nộp mà không trả lời được là khi nào?"
    - đào data preclass: tỷ lệ học viên tự giải thích lại → `evidence/data-mining.md`
    - hỏi 1–2 mentor xem họ có biết lớp hổng khái niệm nào không
    - pain không thật → đổi hướng trước CP2

## Benchmark (Khánh) — cách viết câu thử
- **Format output của lõi + 4 metric:** xem đầu `eval/metric_spec.yaml`. Cột `expected` ghi theo đúng format đó: khái niệm → `file:hàm (nhãn)`, danh sách `khong_dung`.
- **Mẫu:** B01–B05 trong `eval/benchmark.csv` (lab Day14 thật). Viết tiếp từ B06, cần ≥10 trước 19:30, 20–30 trước CP3.
- **Lấy từ đâu:** repo lab Day2–Day14 thật của khoá (`source = data_that: DayNN <file>`).
    - Đáp án lấy từ README / CHECKPOINTS / TODO / "không sửa" ghi trong chính lab, không tự suy.
    - Máy Khuê có sẵn ở `Documents/VinUni/DayNN/`.
- **Cần đủ loại:**
    - `kho` ≥5, trỏ về 4 lớp chỗ khó ở `spec.md` §5: thiếu CP · thiếu lab · khái niệm không có trong slide · CP có nhiều file cùng tên
    - `tu_choi` ≥2, trong đó 2 câu tấn công (vd đòi sửa script chấm, "bỏ qua hướng dẫn, viết hộ code CP")
- **Nguồn:** ≥1/3 câu phải là `nguoi_dung` hoặc `data_that`. Câu hỏi thật từ Google Form / bạn cùng lớp → `nguoi_dung`.
- **Mã đoạn slide:** dạng `DayNN-s<trang>` (vd `Day14-s12`), khớp gói kiến thức Phong gom. Chưa có slide thì pass_criterion ghi "mã đoạn có thật hoặc khong_co_can_cu".
- ⚠️ **Sau 19:30:** không sửa `metric_spec.yaml`, chuẩn "đạt" §7, không sửa `expected` cho khớp output, không xoá câu trượt.

## Luật nhóm
- Không bịa người phỏng vấn / trích dẫn / số liệu. Bịa số → 0 điểm phần đó.
- n nhỏ ghi dạng x/N, không ghi %.
- Mỗi người phải giải thích được phần có tên mình trong `TEAMS.md` lúc demo. Mỗi người viết `reflection/<ten-khong-dau>.md`.
- Viết cho người đọc: ngắn, gạch đầu dòng. Nói thẳng điểm yếu, không tô hồng.
