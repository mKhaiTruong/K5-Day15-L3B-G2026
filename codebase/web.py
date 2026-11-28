"""Giao diện web chạy local: gom lõi + F1 (lộ trình, sơ đồ) + F2 (badge) + F3 (Feynman) vào 1 trang.

Chạy:  python codebase/web.py            → mở http://127.0.0.1:8000 trên trình duyệt
       python codebase/web.py --port 8080 --no-open

Chỉ thư viện chuẩn (http.server). Chỉ nghe 127.0.0.1, không mở ra mạng ngoài.
Không sửa lõi: gọi agent.answer() và các hàm public của f1_lo_trinh / f2_heatmap / feynman.

API (JSON):
    POST /api/hoi             {"text"}                 → bản đồ lõi + lộ trình + sơ đồ + badge + thống kê model
    POST /api/feynman/bat-dau {"ban_do", "khai_niem"?} → {"phien", "cau": [...]} (không lộ đáp án M3)
    POST /api/feynman/cham    {"phien", "i", "tra_loi"} → {"dat", "nhan_xet", "cau_hoi_tiep", "tro_lai"}
    GET  /                    → codebase/web/index.html
"""
import json
import os
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import f1_lo_trinh as f1
import tracing

HERE = os.path.dirname(os.path.abspath(__file__))
INDEX = os.path.join(HERE, "web", "index.html")
MAX_BODY = 64 * 1024
CAU_CONG_KHAI = ("muc", "khai_niem", "hoi", "bo_qua", "slide", "code")  # không gửi "dung", "slide_text"


class App:
    """Lớp dịch vụ (facade) gom lõi + 3 feature; HTTP handler chỉ chuyển JSON vào / ra.

    Các phụ thuộc truyền vào được (dependency injection) để test chạy với lõi giả, không gọi model.
    Một khoá (lock) cho mọi lượt gọi lõi / model, vì tracing ghi vào biến toàn cục.

    Args:
        answer: agent.answer (mặc định nạp thật).
        tim_repo: tools.tim_repo, để F1 đọc code vẽ sơ đồ.
        badge: f2_heatmap.badge_cho_output.
        feynman: module feynman (cần tao_cau_hoi, CHAM).
    """

    def __init__(self, answer=None, tim_repo=None, badge=None, feynman=None):
        if answer is None:
            from agent import answer
        if tim_repo is None:
            from tools import tim_repo
        if badge is None:
            from f2_heatmap import badge_cho_output as badge
        if feynman is None:
            import feynman
        self.answer, self.tim_repo, self.badge, self.feynman = answer, tim_repo, badge, feynman
        self.lock = threading.Lock()
        self.phien = {}  # phien_id → list câu hỏi Feynman (giữ ở server, chỉ trong bộ nhớ)

    def hoi(self, text: str) -> dict:
        """Chạy lõi cho 1 câu hỏi rồi dựng mọi thứ trang cần.

        Returns:
            {"output": dict của lõi, "lo_trinh": lo_trinh(), "do_thi": dữ liệu sơ đồ cho UI tự vẽ,
             "so_do": {"mermaid", "cap", "chu_thich"}, "badge": {tên khái niệm: badge F2},
             "thong_ke": {"models", "model_calls", "tool_calls", "tokens_in", "tokens_out"}}.
        """
        with self.lock:
            tracing.begin("web")
            try:
                output = json.loads(self.answer(text)["output"])
            finally:
                thong_ke, _ = tracing.end()
        lt = f1.lo_trinh(output)
        repo = self.tim_repo(output.get("lab") or "", "") if lt["buoc"] else ""
        return {
            "output": output,
            "lo_trinh": lt,
            "do_thi": _do_thi(repo, lt) if repo else {"cap": "", "nut": [], "canh": []},
            "so_do": f1.so_do(repo, lt) if repo else {"mermaid": "", "cap": "", "chu_thich": ""},
            "badge": {b["khai_niem"]: b["badge"] for b in self.badge(output)},
            "thong_ke": {k: thong_ke[k] for k in ("models", "model_calls", "tool_calls", "tokens_in", "tokens_out")},
        }

    def feynman_bat_dau(self, ban_do: dict, khai_niem: str = "") -> dict:
        """Tạo phiên Feynman từ bản đồ của lõi; câu hỏi giữ ở server, client chỉ nhận phần công khai.

        Args:
            ban_do: output của lõi.
            khai_niem: Tên 1 khái niệm (nút "Giải thích lại" trên card) → chỉ hỏi khái niệm đó; rỗng = hỏi hết.
        """
        cau = [c for c in self.feynman.tao_cau_hoi(ban_do) if not khai_niem or c["khai_niem"] == khai_niem]
        pid = uuid.uuid4().hex
        self.phien[pid] = cau
        return {"phien": pid, "cau": [{k: c[k] for k in CAU_CONG_KHAI if k in c} for c in cau]}

    def feynman_cham(self, pid: str, i: int, tra_loi: str) -> dict:
        """Chấm 1 câu trả lời (M1 gọi model, M2 / M3 chấm bằng code).

        Raises:
            KeyError: phiên hoặc số thứ tự câu không có.
        """
        cau = self.phien[pid][i]
        if cau.get("bo_qua"):
            return {"dat": None, "nhan_xet": cau["bo_qua"], "cau_hoi_tiep": "", "tro_lai": []}
        with self.lock:
            tracing.begin("web-feynman")
            try:
                kq = self.feynman.CHAM[cau["muc"]](tra_loi, cau)
            finally:
                tracing.end()
        return {"dat": kq["dat"], "nhan_xet": kq["nhan_xet"], "cau_hoi_tiep": kq.get("cau_hoi_tiep", ""),
                "tro_lai": kq.get("tro_lai", [])}


def _do_thi(repo: str, lt: dict) -> dict:
    """Dữ liệu sơ đồ cho UI tự vẽ SVG (không phụ thuộc Mermaid / mạng).

    Returns:
        {"cap": "ham" | "file", "nut": [{"id", "nhan", "ten", "nhom"}], "canh": [{"tu", "den", "loai"}],
         "khong_dung": [...]}; cap hàm: nhóm = file, loại cạnh "goi"; cap file: loại "thu_tu" / "import".
    """
    sd = f1.so_do(repo, lt)
    if sd["cap"] == "ham":
        dt = f1.do_thi_goi_ham(repo, lt["buoc"])
        nut = [{"id": n["id"], "nhan": n["nhan"], "ten": n["ham"] + "()", "nhom": n["file"]} for n in dt["nut"]]
        canh = [{"tu": a, "den": b, "loai": "goi"} for a, b in dt["canh"]]
    else:
        ids = {b["file"]: f"B{b['so']}" for b in lt["buoc"]}
        nut = [{"id": ids[b["file"]], "nhan": b["nhan"], "ten": b["file"], "nhom": ""} for b in lt["buoc"]]
        canh = [{"tu": ids[a["file"]], "den": ids[b["file"]], "loai": "thu_tu"}
                for a, b in zip(lt["buoc"], lt["buoc"][1:])]
        canh += [{"tu": ids[a], "den": ids[b], "loai": "import"}
                 for a, b in f1.do_thi_import(repo, list(ids)) if a in ids and b in ids]
    return {"cap": sd["cap"], "nut": nut, "canh": canh, "khong_dung": lt.get("khong_dung") or []}


def tao_handler(app: App):
    """Tạo lớp HTTP handler gắn với 1 App (adapter mỏng: đọc JSON → gọi App → trả JSON)."""

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # tắt log mỗi request cho terminal gọn
            pass

        def _gui(self, code: int, body: bytes, kieu: str):
            self.send_response(code)
            self.send_header("Content-Type", kieu)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, data: dict):
            self._gui(code, json.dumps(data, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self):
            if self.path.split("?")[0] in ("/", "/index.html"):
                try:
                    with open(INDEX, "rb") as fh:
                        return self._gui(200, fh.read(), "text/html; charset=utf-8")
                except OSError:
                    return self._gui(200, "<p>Chưa có codebase/web/index.html.</p>".encode(), "text/html; charset=utf-8")
            self._json(404, {"loi": "không có trang này"})

        def do_POST(self):
            n = int(self.headers.get("Content-Length") or 0)
            if n > MAX_BODY:
                return self._json(413, {"loi": "dữ liệu gửi lên quá lớn"})
            try:
                data = json.loads(self.rfile.read(n) or b"{}")
                if not isinstance(data, dict):
                    raise TypeError
            except (ValueError, TypeError):
                return self._json(400, {"loi": "cần JSON dạng object"})
            try:
                if self.path == "/api/hoi":
                    text = str(data.get("text") or "").strip()
                    if not text:
                        return self._json(400, {"loi": "chưa có câu hỏi"})
                    return self._json(200, app.hoi(text[:2000]))
                if self.path == "/api/feynman/bat-dau":
                    return self._json(200, app.feynman_bat_dau(data.get("ban_do") or {}, str(data.get("khai_niem") or "")))
                if self.path == "/api/feynman/cham":
                    return self._json(200, app.feynman_cham(str(data.get("phien")), int(data.get("i", -1)),
                                                            str(data.get("tra_loi") or "")))
            except (KeyError, IndexError, TypeError, ValueError):
                return self._json(400, {"loi": "phiên hoặc câu hỏi không hợp lệ, bắt đầu lại phiên nhé"})
            except Exception as e:  # noqa: BLE001 — lỗi gọi model / mạng: báo cho UI, server vẫn chạy
                return self._json(500, {"loi": f"{type(e).__name__}: {e}"})
            self._json(404, {"loi": "không có API này"})

    return Handler


def tao_server(app: App, port: int = 8000) -> ThreadingHTTPServer:
    """Tạo server chỉ nghe 127.0.0.1 (port=0 → hệ điều hành tự chọn port, dùng trong test)."""
    return ThreadingHTTPServer(("127.0.0.1", port), tao_handler(app))


def main(argv: list) -> int:
    """CLI: python codebase/web.py [--port 8000] [--no-open]."""
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    port = int(argv[argv.index("--port") + 1]) if "--port" in argv else 8000
    server = tao_server(App(), port)
    url = f"http://127.0.0.1:{server.server_address[1]}"
    print(f"Bản đồ bài giảng ↔ code đang chạy ở {url}  (Ctrl+C để dừng)")
    if "--no-open" not in argv:
        import webbrowser
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
