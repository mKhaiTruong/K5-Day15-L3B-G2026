"""Test feature 1 (codebase/f1_lo_trinh.py): dựng lộ trình từ output của lõi, không gọi AI.

Chạy: python -m pytest tests/test_f1.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import f1_lo_trinh as f1


def _kn(ten, slide, *code):
    """Một khái niệm trong output của lõi; code = các bộ (file, hàm, nhãn)."""
    return {"ten": ten, "slide": slide, "ly_do": "",
            "code": [{"file": f, "ham": h, "nhan": n} for f, h, n in code]}


def test_doc_truoc_sua_va_gom_theo_file():
    """File doc đứng trước file sua; 2 khái niệm cùng file gộp thành 1 bước, giữ đủ hàm + slide."""
    out = {"lab": "Day13", "cp": "CP1", "khong_dung": ["src/lab13_starter.py"], "khai_niem": [
        _kn("Chi phí mỗi việc thành công", "Day13-s12", ("src/lab13.py", "mo_hinh", "sua")),
        _kn("Chạy lại", "Day13-s14", ("src/lab13.py", "ti_le_thanh_cong", "sua"), ("src/README.md", "x", "doc")),
    ]}
    lt = f1.lo_trinh(out)
    assert [(b["so"], b["file"], b["nhan"]) for b in lt["buoc"]] == [
        (1, "src/README.md", "doc"), (2, "src/lab13.py", "sua")]
    sua = lt["buoc"][1]
    assert sua["ham"] == ["mo_hinh", "ti_le_thanh_cong"]
    assert sua["slide"] == ["Day13-s12", "Day13-s14"]
    assert lt["khong_dung"] == ["src/lab13_starter.py"] and lt["loi_nhan"] is None


def test_file_co_mot_ham_sua_thi_ca_buoc_la_sua():
    """Cùng file, 1 hàm doc + 1 hàm sua → bước đó là sua (học viên phải mở để viết)."""
    out = {"khai_niem": [_kn("a", "khong_co_can_cu", ("app.py", "doc_ham", "doc"), ("app.py", "sua_ham", "sua"))]}
    assert f1.lo_trinh(out)["buoc"][0]["nhan"] == "sua"


def test_cat_o_5_buoc_va_dem_con_lai():
    """7 file → giữ 5 bước, con_lai = 2."""
    out = {"khai_niem": [_kn("k", "khong_co_can_cu", *[(f"f{i}.py", "h", "sua") for i in range(7)])]}
    lt = f1.lo_trinh(out)
    assert len(lt["buoc"]) == f1.MAX_BUOC == 5 and lt["con_lai"] == 2
    assert [b["file"] for b in lt["buoc"]] == ["f0.py", "f1.py", "f2.py", "f3.py", "f4.py"]


def test_file_khung_khong_thanh_buoc():
    """Code có nhãn khong_dung (file khung) không bao giờ lọt vào lộ trình."""
    out = {"khong_dung": ["grader.py"], "khai_niem": [
        _kn("k", "khong_co_can_cu", ("grader.py", "grade", "khong_dung"), ("app.py", "run", "sua"))]}
    assert [b["file"] for b in f1.lo_trinh(out)["buoc"]] == ["app.py"]


def test_slide_khong_co_can_cu_khong_hien():
    """slide = khong_co_can_cu → danh sách slide của bước để trống, không ghi chữ khong_co_can_cu."""
    out = {"khai_niem": [_kn("k", "khong_co_can_cu", ("app.py", "run", "sua"))]}
    assert f1.lo_trinh(out)["buoc"][0]["slide"] == []


def test_tu_choi_thi_lo_trinh_rong_kem_loi_nhan():
    lt = f1.lo_trinh({"tu_choi": "Repo này không phải repo lab."})
    assert lt["buoc"] == [] and lt["loi_nhan"] == "Repo này không phải repo lab."


def test_hoi_lai_thi_lo_trinh_rong_kem_cau_hoi():
    out = {"lab": "Day13", "cp": "CP3", "khai_niem": [], "khong_dung": ["a.csv"],
           "can_hoi_lai": "Bạn hỏi cụ thể hơn được không?"}
    lt = f1.lo_trinh(out)
    assert lt["buoc"] == [] and lt["loi_nhan"] == "Bạn hỏi cụ thể hơn được không?"
    assert lt["khong_dung"] == ["a.csv"]


def _w(root, rel, text):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_import_tuyet_doi_khop_theo_duoi_duong_dan(tmp_path):
    """`from app.auth import x` trong 06-lab/app/main.py → khớp 06-lab/app/auth.py (app là gói con)."""
    _w(tmp_path, "06-lab/app/main.py", "from app.auth import verify\nimport os\n")
    _w(tmp_path, "06-lab/app/auth.py", "def verify():\n    pass\n")
    canh = f1.do_thi_import(str(tmp_path), ["06-lab/app/main.py", "06-lab/app/auth.py"])
    assert canh == [("06-lab/app/main.py", "06-lab/app/auth.py")]


def test_import_tuong_doi_va_from_goi_import_module(tmp_path):
    """`from .cost_guard import x` và `from app import auth` (auth là module con) đều thành cạnh."""
    _w(tmp_path, "app/main.py", "from .cost_guard import check\nfrom app import auth\n")
    _w(tmp_path, "app/cost_guard.py", "")
    _w(tmp_path, "app/auth.py", "")
    canh = f1.do_thi_import(str(tmp_path), ["app/main.py", "app/cost_guard.py", "app/auth.py"])
    assert set(canh) == {("app/main.py", "app/cost_guard.py"), ("app/main.py", "app/auth.py")}


def test_import_ngoai_lo_trinh_file_loi_va_tu_tro_bi_bo(tmp_path):
    """Thư viện ngoài, file không nằm trong lộ trình, file lỗi cú pháp, file không phải .py → không có cạnh."""
    _w(tmp_path, "src/lab13.py", "import pandas\nfrom src import lab13\nfrom src.helper import x\n")
    _w(tmp_path, "src/helper.py", "")
    _w(tmp_path, "src/broken.py", "def (:\n")
    canh = f1.do_thi_import(str(tmp_path), ["src/lab13.py", "src/broken.py", "README.md", "khong_co.py"])
    assert canh == []


def test_mermaid_co_o_buoc_mui_ten_va_o_khung():
    """Sơ đồ có 1 ô / bước tô màu theo nhãn, mũi tên đứt nối thứ tự đọc, mũi tên import, ô ⛔ file khung."""
    out = {"khong_dung": ["grader.py"], "khai_niem": [
        _kn("Xác thực", "Day14-s3", ("app/main.py", "ask", "doc")),
        _kn("API key", "khong_co_can_cu", ("app/auth.py", "verify_api_key", "sua"))]}
    lt = f1.lo_trinh(out)
    m = f1.ve_mermaid(lt, [("app/main.py", "app/auth.py")])
    assert m.startswith("flowchart LR")
    assert 'B1["1 · 📖 đọc<br/>app/main.py' in m and ":::doc" in m
    assert 'B2["2 · ✏️ sửa<br/>app/auth.py' in m and ":::sua" in m
    assert "B1 -.-> B2" in m and "B1 -->|import| B2" in m
    assert "⛔ Đừng đụng<br/>grader.py" in m and ":::khung" in m
    assert "Day14-s3" in m


def test_mermaid_thoat_ngoac_kep_va_lo_trinh_rong():
    """Tên có dấu ngoặc kép không làm vỡ nhãn; lộ trình rỗng → chuỗi rỗng."""
    lt = f1.lo_trinh({"khai_niem": [_kn("k", "khong_co_can_cu", ('a"b.py', "h", "sua"))]})
    assert 'a#quot;b.py' in f1.ve_mermaid(lt, [])
    assert f1.ve_mermaid(f1.lo_trinh({"tu_choi": "x"}), []) == ""
