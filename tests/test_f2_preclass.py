"""Test F2 nguồn preclass (codebase/f2_preclass.py): đếm người, không đếm dòng; ô nhỏ chưa đủ dữ liệu; không lộ mã học viên."""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

import f2_preclass as f2p

COT = "id,hv,nguon,lesson_id,kc_code,lan_thu,was_correct\n"


def _csv(tmp_path, dong):
    p = tmp_path / "answers.csv"
    p.write_text(COT + "".join(dong), encoding="utf-8")
    return str(p)


def _dong(hv, kc, dung, nguon="pre_post_post", lan="1", day="program-day06:data-eng"):
    return f"A,{hv},{nguon},{day},{kc},{lan},{dung}\n"


def test_dem_nguoi_sai_lan_dau_o_bai_on(tmp_path):
    """6 người làm khái niệm x: 4 sai lần đầu → 4/6; lần thử 2 và dòng không phải bài ôn bị bỏ;
    1 người sai 2 lần vẫn tính 1 người."""
    dong = [_dong(f"L{i}", "x", "False") for i in range(4)] + [_dong("L4", "x", "True"), _dong("L5", "x", "True"),
            _dong("L0", "x", "False"), _dong("L4", "x", "False", lan="2"), _dong("L5", "x", "False", nguon="thuc_hanh")]
    d = f2p.thong_ke_preclass(_csv(tmp_path, dong))["theo_day"][0]
    assert d["day"] == "Day06" and d["bai"] == "data-eng" and (d["sai"], d["tong"]) == (4, 6)
    assert d["khai_niem"] == [{"kc": "x", "sai": 4, "tong": 6, "du": True}]
    assert (d["luot_sai"], d["luot"], d["du"]) == (4, 6, True)


def test_day_it_nguoi_thi_chua_du(tmp_path):
    """Day chỉ 2 người làm → du False (UI để xám, không tô màu theo tỉ lệ)."""
    d = f2p.thong_ke_preclass(_csv(tmp_path, [_dong("L0", "x", "False"), _dong("L1", "x", "False")]))["theo_day"][0]
    assert d["du"] is False and (d["luot_sai"], d["luot"]) == (2, 2)


def test_o_it_nguoi_chua_du_du_lieu_va_xep_sau(tmp_path):
    """Khái niệm y chỉ 2 người (dù sai cả 2) → du False, xếp sau khái niệm đủ dữ liệu."""
    dong = [_dong(f"L{i}", "x", "True" if i else "False") for i in range(5)] + [_dong("L0", "y", "False"),
                                                                                  _dong("L1", "y", "False")]
    kn = f2p.thong_ke_preclass(_csv(tmp_path, dong))["theo_day"][0]["khai_niem"]
    assert [(k["kc"], k["du"]) for k in kn] == [("x", True), ("y", False)]


def test_khong_lo_ma_hoc_vien_va_thieu_file_thi_rong(tmp_path):
    """Kết quả không chứa mã học viên; không có file → co_du_lieu False."""
    tk = f2p.thong_ke_preclass(_csv(tmp_path, [_dong("L0571", "x", "False")]))
    assert "L0571" not in json.dumps(tk)
    rong = f2p.thong_ke_preclass(str(tmp_path / "khong-co.csv"))
    assert rong["co_du_lieu"] is False and rong["theo_day"] == []
