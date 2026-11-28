"""Test Feature 3 (codebase/feynman.py): phiên Feynman đọc bản đồ của lõi, chấm 3 mức.

Bản đồ mẫu = đáp án câu B08 trong eval/benchmark.csv (lab Day13, CP1). M1 dùng model giả trong test.
Chạy: python -m pytest tests/test_feynman.py
"""
import json
import os
import re
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "codebase"))

import feynman

BAN_DO_B08 = {
    "lab": "Day13", "cp": "CP1",
    "khai_niem": [
        {"ten": "chi phí mỗi việc thành công", "slide": "Day13-s12", "ly_do": "",
         "code": [{"file": "src/lab13.py", "ham": "mo_hinh", "nhan": "sua"}]},
        {"ten": "chạy lại", "slide": "Day13-s14", "ly_do": "",
         "code": [{"file": "src/lab13.py", "ham": "so_lan_chay_ky_vong", "nhan": "sua"},
                  {"file": "src/lab13.py", "ham": "ti_le_thanh_cong", "nhan": "sua"},
                  {"file": "src/lab13_starter.py", "ham": "mo_hinh", "nhan": "khong_dung"}]},
    ],
    "khong_dung": ["src/lab13_starter.py"], "can_hoi_lai": None, "ghi_chu": None,
}


@pytest.fixture(autouse=True)
def goi_that(monkeypatch):
    """Dùng gói kiến thức Day13 thật trong repo."""
    monkeypatch.setenv("KNOWLEDGE_DIR", os.path.join(ROOT, "data", "knowledge"))


def model_gia(text):
    calls = []

    def call(system, user):
        calls.append(user)
        return {"text": text, "model": "test", "tokens_in": 1, "tokens_out": 1}
    return call, calls


def cau(ban_do, muc, khai_niem):
    return next(c for c in feynman.tao_cau_hoi(ban_do) if c["muc"] == muc and c["khai_niem"] == khai_niem)


def test_kich_ban_that_tro_dung_ma_slide_co_that():
    """Mỗi kịch bản M3 của Day13 trỏ về mã slide có thật và có đáp án nằm trong lựa chọn."""
    kb = feynman.doc_kich_ban("Day13")
    assert len(kb) >= 2
    for k in kb:
        assert feynman.doc_doan_slide("Day13", k["slide"])
        assert k["dung"] in k["lua_chon"]


def test_tao_cau_hoi_du_3_muc_va_bo_file_khong_dung():
    cau_hoi = feynman.tao_cau_hoi(BAN_DO_B08)
    muc = [(c["khai_niem"], c["muc"]) for c in cau_hoi]
    assert muc == [("chi phí mỗi việc thành công", 1), ("chi phí mỗi việc thành công", 2),
                   ("chạy lại", 1), ("chạy lại", 2), ("chạy lại", 3)]
    assert "Tử số" in cau(BAN_DO_B08, 1, "chi phí mỗi việc thành công")["slide_text"]
    assert all(c["nhan"] != "khong_dung" for c in cau(BAN_DO_B08, 2, "chạy lại")["code"])


def test_khong_co_slide_thi_bo_m1_va_khong_co_m3():
    ban_do = {"lab": "Day13", "khai_niem": [{"ten": "x", "slide": "khong_co_can_cu",
                                             "code": [{"file": "a.py", "ham": "f", "nhan": "doc"}]}]}
    cau_hoi = feynman.tao_cau_hoi(ban_do)
    assert [c["muc"] for c in cau_hoi] == [1, 2]
    assert "Không có đoạn slide" in cau_hoi[0]["bo_qua"]


@pytest.mark.parametrize("ban_do", [{"tu_choi": "không phải lab"}, {"lab": "Day13", "khai_niem": []}, None])
def test_tu_choi_hoac_rong_thi_khong_hoi(ban_do):
    assert feynman.tao_cau_hoi(ban_do) == []


def test_m2_nhac_dung_ham_thi_dat():
    kq = feynman.cham_m2("Nằm ở hàm mo_hinh() trong src/lab13.py", cau(BAN_DO_B08, 2, "chi phí mỗi việc thành công"))
    assert kq["dat"] is True


def test_m2_sai_ham_thi_tro_lai_slide_va_ham():
    kq = feynman.cham_m2("Chắc ở lab13_starter.py", cau(BAN_DO_B08, 2, "chi phí mỗi việc thành công"))
    assert kq["dat"] is False
    assert kq["tro_lai"] == ["slide Day13-s12", "src/lab13.py:mo_hinh"]


@pytest.mark.parametrize("tra_loi, dat", [("C", True), ("c, vì 1 ÷ p", True), ("Mình chọn A", False),
                                          ("chắc là tăng", None)])
def test_m3_cham_lua_chon(tra_loi, dat):
    kq = feynman.cham_m3(tra_loi, cau(BAN_DO_B08, 3, "chạy lại"))
    assert kq["dat"] is dat
    if dat is False:
        assert "1,25" in kq["nhan_xet"] and "slide Day13-s14" in kq["tro_lai"]


def test_m1_chi_gui_doan_slide_cho_model_va_doc_ket_qua(monkeypatch):
    call, calls = model_gia('{"dat": false, "y_dung": ["chia số việc"], "y_thieu": ["lần hỏng vẫn tính vào tử số"],'
                            ' "cau_hoi_tiep": "Lần chạy hỏng thì sao?"}')
    monkeypatch.setattr(feynman, "call_model", call)
    c = cau(BAN_DO_B08, 1, "chi phí mỗi việc thành công")
    kq = feynman.cham_m1("Là tổng tiền chia cho số việc làm xong", c)
    assert kq["dat"] is False and "lần hỏng" in kq["nhan_xet"]
    assert kq["cau_hoi_tiep"] == "Lần chạy hỏng thì sao?"
    assert c["slide_text"] in calls[0]


def test_m1_qua_ngan_thi_khong_goi_model(monkeypatch):
    call, calls = model_gia('{"dat": true}')
    monkeypatch.setattr(feynman, "call_model", call)
    kq = feynman.cham_m1("chi phí", cau(BAN_DO_B08, 1, "chi phí mỗi việc thành công"))
    assert kq["dat"] is False and calls == []


def test_m1_model_khong_tra_json_thi_chua_cham(monkeypatch):
    monkeypatch.setattr(feynman, "call_model", model_gia("[câu trả lời giả — chưa nối model]")[0])
    kq = feynman.cham_m1("Là tổng chi phí chia cho số việc thành công", cau(BAN_DO_B08, 1, "chạy lại"))
    assert kq["dat"] is None


def test_phien_tron_ven_va_khong_ghi_file(monkeypatch, tmp_path):
    monkeypatch.setattr(feynman, "call_model", model_gia('{"dat": true, "y_dung": [], "y_thieu": [],'
                                                         ' "cau_hoi_tiep": ""}')[0])
    monkeypatch.chdir(tmp_path)
    tra_loi = iter(["Tổng mọi lần chạy kể cả lần hỏng chia cho số việc thành công",
                    "hàm mo_hinh", "bỏ qua", "so_lan_chay_ky_vong", "A"])
    in_ra = []
    ket_qua = feynman.phien(BAN_DO_B08, hoi=lambda _: next(tra_loi), in_ra=in_ra.append)
    assert [(r["muc"], r["dat"]) for r in ket_qua] == [(1, True), (2, True), (1, None), (2, True), (3, False)]
    tong = in_ra[-1]
    assert re.search(r"chạy lại: M1 – · M2 ✓ · M3 ✗ .*slide Day13-s14", tong)
    assert list(tmp_path.iterdir()) == []


def test_main_doc_ban_do_tu_file(monkeypatch, tmp_path, capsys):
    p = tmp_path / "out.json"
    p.write_text(json.dumps({"tu_choi": "Repo này không phải repo lab"}, ensure_ascii=False), encoding="utf-8")
    assert feynman.main(["--ban-do", str(p)]) == 0
    assert "không phải repo lab" in capsys.readouterr().out
