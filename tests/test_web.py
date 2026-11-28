"""Test giao diện web (codebase/web.py): server thật trên port ngẫu nhiên, lõi / Feynman giả, không gọi model."""
import json
import os
import sys
import threading
import types
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import web

LAB = "# TODO CP1: viết hai hàm dưới đây\ndef a():\n    return b()\n\ndef b():\n    return 1\n"
OUT = {"lab": "Day99", "cp": "CP1", "khong_dung": ["src/starter.py"],
       "khai_niem": [{"ten": "Khái niệm A", "slide": "Day99-s1",
                      "code": [{"file": "src/lab.py", "ham": "a", "nhan": "sua"},
                               {"file": "src/lab.py", "ham": "b", "nhan": "sua"}], "ly_do": "TODO CP1"}]}


def _fake_feynman():
    """Feynman giả: 1 câu M2 (chấm bằng code) + 1 câu M3 có đáp án bí mật."""
    def tao_cau_hoi(ban_do):
        return [{"muc": 2, "khai_niem": "Khái niệm A", "hoi": "Ở hàm nào?", "slide": "Day99-s1",
                 "code": [{"file": "src/lab.py", "ham": "a"}]},
                {"muc": 3, "khai_niem": "Khái niệm A", "hoi": "Đoán A/B/C", "dung": "B", "giai_thich": "vì vậy",
                 "slide": "Day99-s1", "code": []}]

    def cham_m2(tra_loi, cau):
        return {"dat": "a" in tra_loi, "nhan_xet": "ok", "tro_lai": []}

    return types.SimpleNamespace(tao_cau_hoi=tao_cau_hoi, CHAM={2: cham_m2})


@pytest.fixture
def url(tmp_path):
    """Chạy server với lõi giả; repo lab giả có 2 hàm a → b."""
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "lab.py").write_text(LAB, encoding="utf-8")

    def answer(text):
        out = {"tu_choi": "không làm hộ"} if "viết hộ" in text else OUT
        return {"output": json.dumps(out, ensure_ascii=False)}

    app = web.App(answer=answer, tim_repo=lambda lab, ten: str(tmp_path),
                  badge=lambda out: [{"khai_niem": "Khái niệm A", "badge": "chưa đủ dữ liệu"}],
                  feynman=_fake_feynman())
    server = web.tao_server(app, 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_address[1]}"
    server.shutdown()
    server.server_close()


def _post(url, path, data):
    req = urllib.request.Request(url + path, data=json.dumps(data).encode(), method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def test_hoi_tra_ban_do_lo_trinh_so_do_badge_va_thong_ke(url):
    """1 câu hỏi → đủ dữ liệu cho trang: output lõi, lộ trình, sơ đồ cấp hàm (a gọi b), badge F2, thống kê model."""
    code, d = _post(url, "/api/hoi", {"text": "Lab Day99, CP1"})
    assert code == 200
    assert d["output"]["cp"] == "CP1" and d["lo_trinh"]["buoc"][0]["file"] == "src/lab.py"
    ten = {n["id"]: n["ten"] for n in d["do_thi"]["nut"]}
    assert d["do_thi"]["cap"] == "ham" and [(ten[c["tu"]], ten[c["den"]]) for c in d["do_thi"]["canh"]] == [("a()", "b()")]
    assert d["do_thi"]["khong_dung"] == ["src/starter.py"] and "flowchart LR" in d["so_do"]["mermaid"]
    assert d["badge"] == {"Khái niệm A": "chưa đủ dữ liệu"}
    assert set(d["thong_ke"]) == {"models", "model_calls", "tool_calls", "tokens_in", "tokens_out"}


def test_hoi_bi_tu_choi_thi_khong_co_lo_trinh(url):
    """Lõi từ chối → trả nguyên câu từ chối, không có sơ đồ."""
    code, d = _post(url, "/api/hoi", {"text": "viết hộ code CP1"})
    assert code == 200 and d["output"]["tu_choi"] and d["do_thi"]["nut"] == []


def test_loi_dau_vao_tra_400(url):
    """Câu hỏi rỗng / JSON không phải object / phiên Feynman không có → 400 kèm lời nhắn, server không sập."""
    assert _post(url, "/api/hoi", {"text": "  "})[0] == 400
    assert _post(url, "/api/hoi", [1, 2])[0] == 400
    assert _post(url, "/api/feynman/cham", {"phien": "khong-co", "i": 0, "tra_loi": "x"})[0] == 400


def test_feynman_khong_lo_dap_an_va_cham_duoc(url):
    """Bắt đầu phiên: client không nhận 'dung' / 'giai_thich' của M3; chấm M2 qua API dùng câu giữ ở server."""
    _, d = _post(url, "/api/feynman/bat-dau", {"ban_do": OUT})
    assert len(d["cau"]) == 2 and all("dung" not in c and "giai_thich" not in c for c in d["cau"])
    code, kq = _post(url, "/api/feynman/cham", {"phien": d["phien"], "i": 0, "tra_loi": "hàm a"})
    assert code == 200 and kq["dat"] is True


def test_trang_chu_tra_html(url):
    """GET / trả HTML (index.html hoặc trang báo chưa có)."""
    with urllib.request.urlopen(url + "/") as r:
        assert r.status == 200 and r.headers["Content-Type"].startswith("text/html")


def test_feynman_loc_theo_khai_niem(url):
    """Nút "Giải thích lại" trên 1 card → chỉ hỏi khái niệm đó; tên không khớp → phiên rỗng."""
    assert len(_post(url, "/api/feynman/bat-dau", {"ban_do": OUT, "khai_niem": "Khái niệm A"})[1]["cau"]) == 2
    assert _post(url, "/api/feynman/bat-dau", {"ban_do": OUT, "khai_niem": "Không có"})[1]["cau"] == []
