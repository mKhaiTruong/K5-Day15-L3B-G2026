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


def _trang():
    out = {"lab": "Day13", "cp": "CP1", "khong_dung": ["src/lab13_starter.py"], "khai_niem": [
        _kn("Chi phí mỗi việc thành công", "Day13-s12", ("src/lab13.py", "mo_hinh", "sua"))]}
    lt1 = f1.lo_trinh(out)
    lt3 = f1.lo_trinh({"lab": "Day13", "cp": "CP3", "khai_niem": [], "can_hoi_lai": "Bạn hỏi cụ thể hơn?"})
    return f1.ve_html("Day13", [{"cp": "CP1", "lt": lt1, "mermaid": f1.ve_mermaid(lt1, [])},
                                {"cp": "CP3", "lt": lt3, "mermaid": ""}])


def test_html_co_sidebar_cp_va_so_do():
    """Sidebar có link tới từng CP: CP có lộ trình gắn ✅, CP rỗng ghi 'chưa nối được'; CP có bước thì có Mermaid."""
    h = _trang()
    assert '<a href="#cp-cp1" aria-current="true">✅ CP1</a>' in h
    assert 'href="#cp-cp3">CP3 <span class="rong">· chưa nối được</span>' in h
    assert '<pre class="mermaid">flowchart LR' in h and f1.MERMAID_CDN in h


def test_html_buoc_khung_va_cho_f2_f3():
    """Mỗi bước có nhãn + file + mã slide; có ô ⛔ file khung; F2 / F3 ghi 'chưa nối', không giả dữ liệu."""
    h = _trang()
    assert '<span class="nhan sua">✏️ Sửa</span><code>src/lab13.py</code>' in h
    assert '<span class="slide">Day13-s12</span>' in h
    assert "⛔ Đừng đụng" in h and "<code>src/lab13_starter.py</code>" in h
    assert "chưa nối (feature 2)" in h and "chưa nối (feature 3)" in h
    assert '<p class="loi-nhan">Bạn hỏi cụ thể hơn?</p>' in h


def test_html_thoat_ky_tu_va_link_bao_sai():
    """Tên file chứa <script> bị thoát (không chèn được HTML); link báo sai điền sẵn lab / CP / file."""
    lt = f1.lo_trinh({"khai_niem": [_kn("k", "khong_co_can_cu", ("<script>x</script>.py", "h", "sua"))]})
    h = f1.ve_html("Day99", [{"cp": "CP1", "lt": lt, "mermaid": f1.ve_mermaid(lt, [])}])
    assert "<script>x</script>" not in h and "&lt;script&gt;x&lt;/script&gt;.py" in h
    assert "không có căn cứ slide" in h
    link = f1._link_bao_sai(f1.ISSUE_URL, "Day13", "CP1", {"file": "src/lab13.py", "nhan": "sua",
                                                           "ham": ["mo_hinh"], "slide": []})
    assert link.startswith(f1.ISSUE_URL + "?title=")
    assert "Day13" in link and "src%2Flab13.py" in link and "khong_co_can_cu" in link


LAB_GOI_HAM = (
    "# TODO CP1: viết ba hàm dưới đây\n"
    "def so_lan(p):\n    return 1 / p\n\n"
    "def ti_le(p):\n    return p\n\n"
    "def he_so(p):\n    return so_lan(p) / ti_le(p)\n\n"
    "def _lam_tron(x):\n    return round(x, 2)\n\n"
    "def mo_hinh(p):\n    return _lam_tron(he_so(p)) + obj.khong_tinh()\n"
)


def _lt_goi_ham(tmp_path, ham=("mo_hinh", "he_so", "so_lan", "ti_le")):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "lab.py").write_text(LAB_GOI_HAM, encoding="utf-8")
    return f1.lo_trinh({"khai_niem": [_kn("k", "Day13-s14", *[("src/lab.py", h, "sua") for h in ham])],
                        "khong_dung": ["src/starter.py"]})


def test_do_thi_goi_ham_noi_ham_goi_ham_va_them_ham_phu(tmp_path):
    """Cạnh = hàm trái gọi hàm phải (đọc ast); hàm phụ được gọi tới thêm vào với nhãn 'phu';
    gọi qua thuộc tính (obj.khong_tinh()) không thành ô."""
    dt = f1.do_thi_goi_ham(str(tmp_path), _lt_goi_ham(tmp_path)["buoc"])
    ten = {n["id"]: n["ham"] for n in dt["nut"]}
    canh = {(ten[a], ten[b]) for a, b in dt["canh"]}
    assert canh == {("mo_hinh", "he_so"), ("mo_hinh", "_lam_tron"), ("he_so", "so_lan"), ("he_so", "ti_le")}
    assert {n["ham"]: n["nhan"] for n in dt["nut"]}["_lam_tron"] == "phu"
    assert "khong_tinh" not in ten.values()


def test_do_thi_goi_ham_toi_da_9_o(tmp_path):
    """Giới hạn số ô: toi_da=2 → chỉ 2 ô, cạnh chỉ nối giữa các ô còn lại."""
    dt = f1.do_thi_goi_ham(str(tmp_path), _lt_goi_ham(tmp_path)["buoc"], toi_da=2)
    assert len(dt["nut"]) == 2 and all(a != b for a, b in dt["canh"])


def test_so_do_it_file_ve_cap_ham_nhieu_file_ve_cap_file(tmp_path):
    """Lộ trình ≤2 file → sơ đồ cấp hàm có khung file + ô hàm; >2 file → giữ sơ đồ cấp file."""
    sd = f1.so_do(str(tmp_path), _lt_goi_ham(tmp_path))
    assert sd["cap"] == "ham" and 'subgraph F1["src/lab.py"]' in sd["mermaid"] and "✏️ mo_hinh()" in sd["mermaid"]
    assert "⛔ Đừng đụng" in sd["mermaid"]
    lt3 = f1.lo_trinh({"khai_niem": [_kn("k", "khong_co_can_cu", ("a.py", "x", "doc"), ("b.py", "y", "doc"),
                                         ("c.py", "z", "sua"))]})
    assert f1.so_do(str(tmp_path), lt3)["cap"] == "file"


def test_chay_lab_lay_cp_tu_output_loi_va_ghi_ro_cp_rong(tmp_path):
    """Danh sách CP lấy từ can_hoi_lai của lõi; CP không nối được ghi CP_RONG thay cho câu hỏi lại."""
    import json

    _lt_goi_ham(tmp_path)

    def answer(text):
        if "CP" not in text.split(".")[0] and "CP1" not in text and "CP2" not in text:
            out = {"can_hoi_lai": "Bạn đang làm CP nào? Lab này có: CP1, CP2"}
        elif "CP1" in text:
            out = {"lab": "Day99", "cp": "CP1", "khong_dung": [],
                   "khai_niem": [_kn("k", "Day99-s1", ("src/lab.py", "mo_hinh", "sua"))]}
        else:
            out = {"lab": "Day99", "cp": "CP2", "khai_niem": [], "can_hoi_lai": "Bạn hỏi cụ thể hơn?"}
        return {"output": json.dumps(out, ensure_ascii=False)}

    muc = f1.chay_lab("Day99", answer=answer, tim_repo=lambda lab, ten: str(tmp_path))
    assert [m["cp"] for m in muc] == ["CP1", "CP2"]
    assert muc[0]["chu_thich"].startswith("Mỗi khung là 1 file") and "mo_hinh()" in muc[0]["mermaid"]
    assert muc[1]["lt"]["loi_nhan"] == f1.CP_RONG and muc[1]["mermaid"] == ""
