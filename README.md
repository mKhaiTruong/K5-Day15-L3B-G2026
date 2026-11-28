# G2026 — Bản đồ bài giảng ↔ code lab theo CP

**Thành viên, lớp, track:** xem [TEAMS.md](TEAMS.md). **Điền TEAMS.md đúng format**: khi chấm và đánh giá, BTC quét file này để ghép điểm cho từng người.

*Lát cắt = phần nhỏ nhất làm xong được trong hackathon: một người dùng · một việc · một quyết định AI · một kết quả.*

---

## Nhóm làm gì, khung làm gì

| Nhóm quyết định và viết | Khung làm sẵn (không cần sửa) |
|---|---|
| Người dùng, pain, bằng chứng, impact (`evidence/`, `spec.md` §1–§2) | — |
| Hình dạng giải pháp, công cụ, prompt, luồng (`spec.md` §4, `codebase/agent.py`, `tools.py`, `ai.py`) | Ghi mọi lần gọi model / công cụ vào trace, cộng token (`codebase/tracing.py`) |
| Bộ câu thử, metric, chuẩn "đạt" (`eval/benchmark.csv`, `eval/metric_spec.yaml`, `spec.md` §7) | Kiểm đủ cột, đủ câu `kho` / `tu_choi`, đủ ≥1/3 câu từ người dùng / data thật (`run.py check`) |
| Chấm cột `pass` theo metric spec | Chạy cả bộ một lệnh, có run ID, model, token từng câu (`run.py eval`) · tính % đạt (`run.py score`) |
| Persona, số người dùng thật, giá model (`cost/personas.yaml`) | Sinh ~50 phiên, chạy thật qua bản chạy thử, tính chi phí / phiên, / task thành công, / tháng 3 kịch bản (`run.py simulate`) |

*Ví dụ track A (ví dụ cỡ, không phải lời giải):* nhóm viết công cụ `search_lesson` tra bài pre-class đã đánh mã đoạn, luồng "tra đoạn → model trả lời kèm mã đoạn, không có thì nói không có", metric "mọi khẳng định có mã đoạn đúng", persona "ôn dồn trước kiểm tra". Khung chạy 25 câu thử ra `run-1.csv`, nhóm chấm `pass`, `score` in % đạt; `simulate` chạy 50 phiên ra chi phí / task thành công cho hai model.

## Chạy trong 3 phút

Bộ khung cần **Python 3.10 trở lên** (Python 3.9 có sẵn trên macOS vẫn chạy được, chỉ in một dòng nhắc). **Không cần `pip install`.**

**Bước 1 — Mở cửa sổ lệnh ngay trong thư mục repo**

| Windows (PowerShell) | macOS |
|---|---|
| Mở thư mục repo bằng File Explorer → bấm vào thanh địa chỉ → gõ `powershell` → Enter | Mở **Terminal** (Cmd + Space, gõ "Terminal") → gõ `cd ` (có dấu cách) → kéo thả thư mục repo vào → Enter |

Gõ `dir` (Windows) hoặc `ls` (macOS / Linux): thấy `run.py` và `README.md` là đang đứng đúng chỗ.

**Bước 2 — Kiểm Python và chạy thử**

| Việc | Windows (PowerShell) | macOS / Linux |
|---|---|---|
| Kiểm Python | `python --version` (không được thì `py --version`) | `python3 --version` |
| Chạy bản chạy thử (chế độ giả, chưa gọi model) | `python run.py` | `python3 run.py` |
| Kiểm bộ câu thử | `python run.py check` | `python3 run.py check` |
| Tạo file `.env` để nối model | `copy .env.example .env` | `cp .env.example .env` |

- Windows: gõ `python` mà mở Microsoft Store hoặc báo không có lệnh → dùng `py`. Chưa có Python: cài từ python.org, **tick "Add python.exe to PATH"**, mở lại PowerShell.
- macOS: báo `command not found: python` là bình thường → dùng `python3`.
- `python run.py` in ra "[câu trả lời giả — chưa nối model] …" là khung chạy đúng. Nối model thật: [docs/connect-model.md](docs/connect-model.md).

Trong README này lệnh viết là `python …`; máy nhóm cần `python3` hay `py` thì gõ thay.

## Giao diện web (bản demo)

Một trang gom cả lõi + 3 feature, 2 tab:

- **Hỏi bài:** hỏi 1 câu → sơ đồ hàm của CP → khái niệm ↔ `file : hàm` kèm mã slide → "Thử thách tôi" (Feynman, F3: giải thích lại cho AI đóng vai người mới)
- **Lớp kẹt ở đâu** (F2, cho người ra đề / mentor): số gộp từ data preclass BTC (Day × khái niệm, số người sai lần đầu ở bài ôn) + từ câu hỏi ẩn danh trên app. < 5 người → "chưa đủ dữ liệu", không có trang xem từng người

1. Điền `.env` (copy từ `.env.example`):
    - `MODEL_PROVIDER=openai` · `MODEL_NAME=gpt-5-mini` · `API_KEY=<khoá OpenAI>`
    - `LABS_DIR=<thư mục chứa các repo lab DayNN>` (repo lab của khoá không commit vào đây)
2. Chạy:
    ```
    python codebase/web.py            # tự mở http://127.0.0.1:8000
    python codebase/web.py --port 8080 --no-open
    ```
3. Thử: bấm chip "Day13 CP1: công thức chi phí" (gọi model thật, ~20–60 giây) → bấm "Thử thách tôi" trên 1 card → bấm chip "Thử nhờ làm hộ" để thấy bị từ chối.
    - mở thẳng 1 câu: `http://127.0.0.1:8000/?q=Lab Day13, CP1. Công thức chi phí trong bài giảng được viết thành những hàm nào?`
    - đọc repo **đã làm xong của chính bạn**: dán link GitHub (công khai, tên có `DAYnn`) vào ô "Repo của bạn" → lõi tải về `data/repos/` (gitignored) và đọc code bạn đã viết; xoá hết `# TODO` rồi thì lõi lọc hàm theo `git diff` so với commit đầu (đề lúc tạo repo)
    - mở thẳng tab heatmap: `http://127.0.0.1:8000/?tab=heat` (cần `data-btc/preclass/answers.csv` trên máy, không commit)

- Chân trang hiện model · token vào / ra · thời gian: bằng chứng gọi AI thật. Bật `CACHE=1` thì không gọi model (token = 0), **quay demo / video thì để `CACHE` trống**.
- Chạy web thì bật log ẩn danh cho heatmap (`HEATMAP_LOG=1`: chỉ ghi lab, CP, tên khái niệm; không ghi câu hỏi, không ghi người). Tắt: `--no-log`.
- Chỉ chạy local (`127.0.0.1`), không deploy: lõi đọc repo lab + slide của khoá, đưa lên server công khai là public tài liệu khoá + code học viên, kèm khoá API ai cũng gọi được.
- Chỉ thư viện chuẩn Python (`http.server`), không cần `pip install`. Code: `codebase/web.py` (API) + `codebase/web/index.html` (giao diện, theme jade).

## Lệnh

| Lệnh | Làm gì |
|---|---|
| `python run.py` | Chạy bản chạy thử (gõ đầu vào, nhận kết quả, kèm số lần gọi model / token) |
| `python run.py check` | Kiểm `eval/benchmark.csv` (6 cột, số câu, `kho` / `tu_choi`, mã `source`, ô trống, dòng mẫu) `eval/metric_spec.yaml` (≥3 metric điền đủ) và `TEAMS.md` (đúng format để BTC quét). Chỉ cảnh báo, không sửa file |
| `python run.py eval --try` | **Thử nối model:** chạy 3 câu đầu (`--try 5` = 5 câu) → `eval/run-try.csv`. Thấy "Nối model được" là xong. Không tính là một lượt |
| `python run.py eval` | Chạy cả bộ qua `codebase/agent.py` → `eval/run-1.csv` (lần sau `run-2.csv`…) + `traces/run-1.jsonl`. Mỗi dòng có run ID, model, số lần gọi model / công cụ, token. Model còn giả → chỉ ghi `run-mock.csv`; mọi câu lỗi → `run-error.csv`; Ctrl+C → `run-stopped.csv` — đều **không** được đánh số |
| `python run.py eval --fake` | Thử riêng bộ chạy, không gọi agent → `eval/run-fake.csv` |
| `python run.py score eval/run-1.csv` | Sau khi điền cột `pass` (1 / 0): in % đạt tổng và theo `type`. Còn ô trống → "CHƯA CHẤM XONG", không in % |
| `python run.py simulate --try` | Thử mô phỏng chi phí 10 phiên (làm trước CP3) → `cost/simulate-try.csv` |
| `python run.py simulate` | Mô phỏng chi phí khi dùng thật theo `cost/personas.yaml` (≥50 phiên) → `cost/simulate-N.csv` + `cost/simulate-N-summary.md` |
| `python run.py simulate --rate-from eval/run-2.csv` | Như trên, lấy tỉ lệ đạt từ đúng lượt chỉ định. Không ghi thì khung lấy lượt `run-N` mới nhất đã chấm, cùng model, và ghi rõ đã lấy lượt nào trong bản tóm tắt |
| `python codebase/web.py` | **Giao diện web** gom lõi + F1 + F2 + F3 (mục "Giao diện web" ở trên) |
| `python codebase/f1_lo_trinh.py Day13` | F1: chạy lõi cho mọi CP của 1 lab → trang lộ trình + sơ đồ `data/f1/Day13.html` (nên bật `CACHE=1`). Mẫu đã chạy: [data/f1/Day13.html](data/f1/Day13.html) |
| `python codebase/f2_preclass.py` | F2 nguồn data preclass BTC: top khái niệm lớp kẹt nhất mỗi Day (số người sai lần đầu ở bài ôn, số gộp) |
| `python codebase/f2_heatmap.py --lab Day13` | F2: bảng "khái niệm / CP nào lớp kẹt nhất" từ log ẩn danh (`HEATMAP_LOG=1` mới ghi log; < 5 lượt → "chưa đủ dữ liệu") |
| `python codebase/feynman.py "Lab Day13, CP1. ..."` | F3: phiên Feynman trên terminal (người mới hỏi, học viên giải thích lại, chấm 3 mức) |
| `python -m pytest tests/` | Test lõi + F1 + F2 + F3 + web (lõi chạy AI giả, không tốn token). pytest không có trong `requirements.txt`, cài riêng |

Gói miễn phí báo hết lượt: thêm `--wait 4` sau `eval` hoặc `simulate` (nghỉ 4 giây giữa hai lượt gọi). Sửa CSV bằng Excel: *File → Save As → CSV UTF-8*; Google Sheets: *Tệp → Tải xuống → CSV*.

**Lượt có lỗi kỹ thuật** (cột `error` có chữ): không sửa tay file đó, chạy lại thành lượt mới và ghi vào bảng các lượt ở `eval/README.md`. Không xoá file lượt nào.

Nhóm dùng stack khác (Node, Streamlit, notebook…): sửa hàm `run_app()` trong `run.py` để `python run.py` vẫn chạy được bản chạy thử, và giữ `answer()` trong `codebase/agent.py` để `eval`, `simulate` chạy được.

## Bản chạy thử — viết ở đâu

| File | Viết gì | Bước guide |
|---|---|---|
| `codebase/agent.py` | `answer(text)` — luồng chính, đúng hình dạng ở `spec.md` §4. Khung có sẵn một workflow 2 bước *ví dụ* | 3.2 |
| `codebase/tools.py` | Công cụ của bài toán, mỗi công cụ một hàm có `@tool` | 2.2, 3.2 |
| `codebase/ai.py` | `call_model(system, user)` — chỗ duy nhất gọi model. Chưa điền `.env` thì chạy **chế độ giả** | 3.3 |

- **Trước CP2:** để chế độ giả, công cụ trả dữ liệu giả — `python run.py` đi hết luồng là đủ.
- **Trước CP3:** nối model thật theo [docs/connect-model.md](docs/connect-model.md), `eval --try` thấy token > 0 rồi mới `eval`.
- Bộ chạy gửi **nguyên ô `input`** của câu thử vào `answer(text)`. Dữ liệu nền (bài học, thông báo, lịch…) để trong `data/`, đọc qua công cụ.

## Phần nào thật, phần nào giả

| Thành phần | Thật / Giả | Ghi chú |
|---|---|---|
| Lời gọi AI ở quyết định trung tâm (bước 5: ghép khái niệm ↔ file / hàm) | **Giả** tới CP2 · **Thật** từ CP3 | CP2 chạy chế độ giả (ghép dự phòng theo tên hàm). CP3 nối `codebase/ai.py`, model: `gpt-5-mini` (OpenAI, `MODEL_PROVIDER=openai`); `run-1` chạy `openai/gpt-5-mini` qua OpenRouter |
| Đọc repo lab, CP, file khung (`tools.py`) | **Thật** | Đọc repo lab thật của khoá trong `LABS_DIR`. Chỉ đưa model các hàm mà `# TODO CPn` chỉ tới (PR #21) |
| Gói kiến thức slide (`data/knowledge/`) | **Thật, nhóm tự viết** | Bản tóm tắt nhóm tự viết theo mã `DayNN-s<trang>`, không phải slide gốc. Mới có Day13 (3 trang) → lab khác ra `khong_co_can_cu` |
| Kiểm hàm / mã slide có thật, ép nhãn file khung (bước 6) | **Thật** | Kiểm bằng code, không qua model |
| F1 lộ trình + sơ đồ (`f1_lo_trinh.py`) | **Thật, không gọi AI** | Dựng từ output lõi + đọc code lab bằng `ast` (hàm gọi hàm, file import file) |
| F2 heatmap từ app (`f2_heatmap.py`) | **Thật, chưa có dữ liệu** | Đếm từ log ẩn danh (bật khi chạy web); mới đếm lượt hỏi, chưa đếm người → < 5 lượt hiện "chưa đủ dữ liệu", không giả số |
| F2 heatmap từ preclass (`f2_preclass.py`) | **Thật, data BTC** | Số gộp từ `data-btc/preclass/answers.csv` (không commit); vd Day06 41/93 lượt sai lần đầu ở bài ôn |
| F3 Feynman (`feynman.py`) | **Thật** | Mức 1 gọi model chấm, chỉ đối chiếu đoạn slide; mức 2–3 chấm bằng code. Kịch bản mức 3 mới có Day13 |
| Giao diện web (`web.py`, `web/index.html`) | **Thật, chạy local** | Không deploy (lý do ở mục "Giao diện web") |

## Dùng AI vào việc gì

2–3 dòng (bắt buộc): nhóm dùng công cụ AI nào để làm gì, người kiểm lại phần nào. Chi tiết: [docs/ai-usage.md](docs/ai-usage.md). Coding agent đọc [AGENTS.md](AGENTS.md).

- **Claude Code (Claude Opus):** Khuê dùng để viết lõi `codebase/`, F1, giao diện web (`codebase/web.py`, `web/index.html`) + test, `spec.md` §0–§2, §4, canvas, script đào data preclass, review PR. Người kiểm: ____
- **Claude Code (Claude Sonnet):** Khánh dùng để viết câu thử B06–B18 và `eval/grade_metrics.py`. Người kiểm: ____
- **Claude Code (Claude Opus):** Phong dùng để viết F3 `codebase/feynman.py` + test, `data/DATA_CARD.md`, tóm tắt slide Day13, điền slide trang 3–8. Người kiểm: Phong đối chiếu số trên slide với `eval/run-*.csv`, trace và PDF slide gốc; Khuê duyệt và merge PR #8, #17, #29
- Đức Anh: ____

## File mẫu — điền ở bước nào

| File | Điền ở bước guide | Mốc |
|---|---|---|
| `TEAMS.md` | 1.0 | CP1 · **đúng format**, BTC quét khi chấm |
| `canvas.md` | 1.4 | CP1, cập nhật CP2 |
| `evidence/hypothesis.md` | 1.1 | trước khi tìm bằng chứng |
| `evidence/data-mining.md` · `evidence/interviews/TEMPLATE.md` → `P1.md`… · `evidence/survey/TEMPLATE.md` | 1.2 | bắt đầu sau Zoom, xong CP3 |
| `evidence/summary.md` | 1.2 | CP3 |
| `spec.md` | §0–§2: 1.1–1.3 · §3–§5: 2.1–2.3 · §7: 2.4 · §8: 4.2 · §10: suốt | §7 chốt CP2 · §0–§7 CP3 · đủ CP4 |
| `data/DATA_CARD.md` | 2.4 | bản đầu CP2 |
| `eval/benchmark.csv` · `eval/metric_spec.yaml` | 2.4 | ≥10 câu + metric chốt CP2 · 20–30 câu CP3 |
| `codebase/` | 3.2, 3.3 | khung CP2 · AI thật CP3 |
| `eval/report.md` · `eval/README.md` | 4.1 (README mục 1–4 từ 2.4) | CP4 |
| `cost/personas.yaml` · `cost/cost-estimate.md` | 4.2 | thử 10 phiên CP3 · đủ CP4 |
| `validation/log.md` *(bonus)* | 4.3 | CP4 |
| `slides/outline.md` → `demo-slides.pdf` | 5.1 | CP4 |
| `reflection/TEMPLATE.md` → `reflection/<ten>.md` | 5.3 | 23:59 Thứ Bảy 28/11 |
| `AGENTS.md` · `docs/ai-usage.md` | khi dùng coding agent / AI | suốt |

## Bảy hạng mục bắt buộc — nằm ở file nào

| # | Hạng mục | File |
|---|---|---|
| 1 | Bằng chứng pain | `evidence/` (tổng hợp ở `evidence/summary.md`) |
| 2 | Impact có số | `spec.md` §2 |
| 3 | Thiết kế giải pháp | `spec.md` §4 |
| 4 | Bản chạy thử làm trọn lát cắt | `codebase/` · lệnh ở mục "Lệnh" |
| 5 | Định nghĩa "tốt" + bộ câu thử | `data/DATA_CARD.md` · `eval/` |
| 6 | Mô phỏng chi phí khi dùng thật | `cost/` |
| 7 | Slide + demo + video dự phòng | slide trong repo (PDF, PPTX, HTML…) hoặc link slide ở form CP4 · `demo-slides.pdf` · video dự phòng CP4 (quay trên giao diện web, gpt-5-mini thật): https://youtu.be/6WCbfzqKo7Y · video CP3 (30 giây, bản chạy thử gọi AI thật): https://youtu.be/9zUn2nzibEI |
| + | *Bonus:* người dùng thử | `validation/log.md` |
