# CLAUDE.md — context cho Claude Code trong repo G2026

@AGENTS.md

## Bối cảnh
- AI20K K5 Day15 Mini Hackathon, nhóm **G2026**, lớp **L3B**, 4 người (xem `TEAMS.md`). Đội trưởng: Trương Đặng Minh Khuê.
- Đề + rubric gốc: repo BTC `VinUni-AI20k/K5-L3-Day15-AI-Product-Hackathon` (`README.md`, `01-challenge-brief.md`, `02-guide.md`, `03-rubric.md`, `tracks/track-a-edtech.md`). Data BTC copy ở `data-btc/` (gitignored, không commit).
- Mốc: **CP1 17:00 27/11** · CP2 19:30 27/11 · CP3 10:00 28/11 · CP4 14:30 28/11 · nộp cuối 23:59 28/11. Nộp checkpoint: https://ai20k-hackathon.pages.dev/#submit
- Python: dùng `.venv/Scripts/python.exe` (Windows). LLM mặc định: OpenAI, key trong `.env`.

## Hướng đang theo (tạm chốt 27/11, chưa có bằng chứng)
- **Track A.** Tên tạm: agent chỉ đường repo lab.
- **Người đau:** sinh viên vừa nhận repo lab, muốn làm đúng nhưng không biết bắt đầu từ đâu, file nào sửa, file nào cấm đụng.
- **Không phục vụ:** người kệ đời chỉ vibe code cho qua.
- **Lát cắt:** sinh viên đưa repo lab + chọn CP (và mục tiêu: làm bài / hiểu lại / tìm lỗi) → agent trả lộ trình ~5 file theo thứ tự, mỗi file gắn nhãn đọc / sửa / không đụng + 1 câu lý do, kèm sơ đồ flow.
- **Agent quyết định:** lộ trình theo CP; hỏi lại khi chưa rõ CP/mục tiêu; từ chối khi repo không phải lab (dùng cho test `tu_choi`).
- **Khác DeepWiki/ChatGPT:** họ giải thích mọi file như nhau. Agent này biết cấu trúc đề lab (checkpoint, rubric, file cấm sửa) và chỉ đường theo nhiệm vụ.
- **Cấu trúc:** lõi (phân tích repo lab + CP, tìm file / folder / khái niệm quan trọng) + 3 feature dùng chung lõi. Nhóm tự chia thời gian, không ưu tiên feature nào trong tài liệu nộp.
    1. lộ trình file theo CP (mô tả ở trên)
    2. heatmap: câu hỏi gộp ẩn danh → badge "🔥 x/N bạn hỏi ở đây" trên cây file + trang "CP nào lớp kẹt nhất" cho người ra đề; < ~5 người thì ghi "chưa đủ dữ liệu"
    3. Feynman: sau khi làm, agent đóng vai người mới hỏi, học viên giải thích lại; chấm đối chiếu slide + code; hổng thì trỏ lại đoạn slide / code. Tự nguyện, không ai xem kết quả riêng
- **Số muốn đo:** thời gian tới lần mở đúng file cần sửa, có agent so với không có (5 bạn cùng lớp, 1 lab lạ).
- **Benchmark:** lấy từ lab Day1–15 thật của khóa (`data_that`) + repo không phải lab (`tu_choi`).

## Đã loại (đừng đề xuất lại)
- **Track B (B1/B2/B3):** 2 thành viên không muốn làm y tế. B2 rủi ro cao.
- **Feynman tutor đứng riêng:** không ai tự mở app để bị kiểm tra. Đã gộp thành feature 3.
- **Mentor dùng app để kiểm tra từng người:** thành công cụ giám sát, vi phạm luật Track A.
- **Gallery format tóm tắt repo:** trùng DeepWiki/GitDiagram; phần AI mờ. Chỉ giữ ý sơ đồ flow (skill `lab-cp-html` của 1 thành viên).

## Việc tiếp theo
- **CP1:** đã viết nháp `TEAMS.md` (Track A), `canvas.md`, `evidence/hypothesis.md`, `spec.md` §0–§2. Còn thiếu: phân công trong canvas dòng 7 + cột "Phần việc chính" của `TEAMS.md`.
- **Trước CP2:**
    - phỏng vấn ≥3 sinh viên ngoài team, hỏi kiểu Mom Test: "lần gần nhất nhận repo lab mở file nào đầu tiên, mất bao lâu tìm ra file cần sửa, từng sửa nhầm file cấm chưa?"
    - hỏi 1–2 mentor xem họ có biết lớp kẹt ở đâu không
    - pain không thật → đổi hướng trước CP2

## Luật nhóm
- Không bịa người phỏng vấn / trích dẫn / số liệu. Bịa số → 0 điểm phần đó.
- n nhỏ ghi dạng x/N, không ghi %.
- Mỗi người phải giải thích được phần có tên mình trong `TEAMS.md` lúc demo. Mỗi người viết `reflection/<ten-khong-dau>.md`.
- Viết cho người đọc: ngắn, gạch đầu dòng. Nói thẳng điểm yếu, không tô hồng.
