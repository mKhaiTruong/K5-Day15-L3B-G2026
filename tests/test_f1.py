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
