import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "codebase"))

from f2_heatmap import badge_cho_output, bao_cao_markdown, thong_ke_heatmap


def _ghi_log(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def test_duoi_5_luot_tra_ve_chua_du_du_lieu(tmp_path):
    log_file = tmp_path / "cau_hoi.jsonl"
    _ghi_log(
        log_file,
        [
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["health check"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["readiness"]},
        ],
    )
    res = thong_ke_heatmap(lab="Day14", log_path=str(log_file))
    assert res["du_du_lieu"] is False
    assert res["thong_bao"] == "chưa đủ dữ liệu"
    assert res["tong_luot"] == 4
    assert res["top_ket"] == []
    assert "chưa đủ dữ liệu" in bao_cao_markdown(lab="Day14", log_path=str(log_file))


def test_tu_5_luot_tro_len_hien_badge_luot_hoi_va_giai_thich_mau_so(tmp_path):
    log_file = tmp_path / "cau_hoi.jsonl"
    _ghi_log(
        log_file,
        [
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting", "rate limiting"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting", "health check"]},
            {"lab": "Day14", "cp": "CP5", "khai_niem": ["health check"]},
            {"lab": "Day14", "cp": "CP2", "khai_niem": ["readiness"]},
            {"lab": "Day13", "cp": "CP1", "khai_niem": ["chi phí"]},
        ],
    )
    res = thong_ke_heatmap(lab="Day14", log_path=str(log_file))
    assert res["du_du_lieu"] is True
    assert res["loai_mau_so"] == "luot_hoi"
    assert res["tong_luot"] == 5
    assert res["top_ket"][0]["khai_niem"] == "rate limiting"
    assert res["top_ket"][0]["so_luot"] == 3
    assert res["top_ket"][0]["badge"] == "🔥 3/5 lượt hỏi"

    md = bao_cao_markdown(lab="Day14", log_path=str(log_file))
    assert "🔥 3/5 lượt hỏi" in md
    assert "Mẫu số N = **5** lượt hỏi" in md
    assert "1 câu hỏi có thể trúng nhiều khái niệm" in md
    assert "Day13" not in md


def test_co_id_an_danh_dem_theo_nguoi_va_hien_ban_hoi(tmp_path):
    log_file = tmp_path / "cau_hoi.jsonl"
    _ghi_log(
        log_file,
        [
            {"id": "u1", "lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
            {"id": "u1", "lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
            {"id": "u2", "lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting", "health check"]},
            {"id": "u3", "lab": "Day14", "cp": "CP5", "khai_niem": ["health check"]},
            {"id": "u4", "lab": "Day14", "cp": "CP5", "khai_niem": ["readiness"]},
            {"id": "u5", "lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]},
        ],
    )
    res = thong_ke_heatmap(lab="Day14", log_path=str(log_file))
    assert res["du_du_lieu"] is True
    assert res["loai_mau_so"] == "nguoi"
    assert res["tong_luot"] == 5
    assert res["top_ket"][0]["khai_niem"] == "rate limiting"
    assert res["top_ket"][0]["so_luot"] == 3
    assert res["top_ket"][0]["badge"] == "🔥 3/5 bạn hỏi ở đây"

    md = bao_cao_markdown(lab="Day14", log_path=str(log_file))
    assert "Mẫu số N = **5** người dùng ẩn danh" in md


def test_badge_cho_output_tu_contract_chuan(tmp_path):
    log_file = tmp_path / "cau_hoi.jsonl"
    _ghi_log(
        log_file,
        [{"lab": "Day14", "cp": "CP5", "khai_niem": ["rate limiting"]} for _ in range(5)],
    )
    output_json = json.dumps(
        {
            "lab": "Day14",
            "cp": "CP5",
            "khai_niem": [{"ten": "rate limiting", "slide": "Day14-s1", "code": [], "ly_do": "test"}],
            "khong_dung": [],
            "can_hoi_lai": None,
            "ghi_chu": "",
        },
        ensure_ascii=False,
    )
    badges = badge_cho_output(output_json, log_path=str(log_file))
    assert badges == [
        {
            "khai_niem": "rate limiting",
            "so_luot": 5,
            "tong_luot": 5,
            "badge": "🔥 5/5 lượt hỏi",
        }
    ]
    assert badge_cho_output({"tu_choi": "không phải lab"}, log_path=str(log_file)) == []
