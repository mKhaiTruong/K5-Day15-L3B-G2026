"""Feature 2: Heatmap câu hỏi ẩn danh ("🔥 x/N bạn hỏi ở đây" + khái niệm/CP lớp kẹt nhất).

Chỉ đọc log từ data/heatmap/cau_hoi.jsonl và JSON output của lõi (answer(text)["output"]).
Không sửa codebase/agent.py, tools.py, ai.py; không lưu hay hiển thị thông tin cá nhân.
"""

from __future__ import annotations

import json
import os
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_LOG_PATH = os.path.join(ROOT, "data", "heatmap", "cau_hoi.jsonl")
MIN_SAMPLES = 5


def doc_log(log_path: str | None = None) -> list[dict]:
    """Đọc các dòng log ẩn danh từ cau_hoi.jsonl; trả về [] nếu chưa có file."""
    path = log_path or DEFAULT_LOG_PATH
    if not os.path.isfile(path):
        return []
    rows: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(item, dict):
                rows.append(item)
    return rows


def thong_ke_heatmap(
    lab: str | None = None,
    log_path: str | None = None,
    min_samples: int = MIN_SAMPLES,
) -> dict:
    """Tổng hợp tần suất (lab, cp, khai_niem); dưới min_samples trả về 'chưa đủ dữ liệu'."""
    rows = doc_log(log_path)
    if lab:
        target = lab.strip().lower()
        rows = [r for r in rows if str(r.get("lab") or "").strip().lower() == target]

    tong_luot = len(rows)
    if tong_luot < min_samples:
        return {
            "du_du_lieu": False,
            "thong_bao": "chưa đủ dữ liệu",
            "tong_luot": tong_luot,
            "top_ket": [],
        }

    counts: Counter[tuple[str, str, str]] = Counter()
    for r in rows:
        r_lab = str(r.get("lab") or "").strip()
        r_cp = str(r.get("cp") or "").strip()
        concepts = r.get("khai_niem") or []
        if not isinstance(concepts, list):
            continue
        seen_in_row = {str(c).strip() for c in concepts if str(c).strip()}
        for ten in seen_in_row:
            counts[(r_lab, r_cp, ten)] += 1

    top_ket = [
        {
            "lab": k_lab,
            "cp": k_cp,
            "khai_niem": k_ten,
            "so_luot": so_luot,
            "tong_luot": tong_luot,
            "badge": f"🔥 {so_luot}/{tong_luot} bạn hỏi ở đây",
        }
        for (k_lab, k_cp, k_ten), so_luot in counts.most_common()
    ]
    return {
        "du_du_lieu": True,
        "thong_bao": None,
        "tong_luot": tong_luot,
        "top_ket": top_ket,
    }


def _parse_output(output_json: str | dict) -> dict:
    if isinstance(output_json, dict):
        return output_json
    if isinstance(output_json, str):
        try:
            data = json.loads(output_json)
            return data if isinstance(data, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def badge_cho_output(
    output_json: str | dict,
    log_path: str | None = None,
    min_samples: int = MIN_SAMPLES,
) -> list[dict]:
    """Gắn badge '🔥 x/N bạn hỏi ở đây' (hoặc 'chưa đủ dữ liệu') cho từng khái niệm trong output lõi."""
    data = _parse_output(output_json)
    if "tu_choi" in data or not data.get("khai_niem"):
        return []

    lab = str(data.get("lab") or "").strip()
    cp = str(data.get("cp") or "").strip()
    stats = thong_ke_heatmap(lab=lab or None, log_path=log_path, min_samples=min_samples)

    lookup = {
        (item["cp"], item["khai_niem"]): item
        for item in stats["top_ket"]
    }

    badges: list[dict] = []
    for k in data["khai_niem"]:
        if not isinstance(k, dict):
            continue
        ten = str(k.get("ten") or "").strip()
        if not ten:
            continue
        if not stats["du_du_lieu"]:
            badges.append({"khai_niem": ten, "badge": "chưa đủ dữ liệu"})
            continue
        hit = lookup.get((cp, ten))
        so_luot = hit["so_luot"] if hit else 0
        tong = stats["tong_luot"]
        badges.append(
            {
                "khai_niem": ten,
                "so_luot": so_luot,
                "tong_luot": tong,
                "badge": f"🔥 {so_luot}/{tong} bạn hỏi ở đây",
            }
        )
    return badges


def bao_cao_markdown(
    lab: str | None = None,
    log_path: str | None = None,
    min_samples: int = MIN_SAMPLES,
) -> str:
    """Xuất bảng 'Khái niệm / CP nào lớp kẹt nhất' dạng Markdown ẩn danh."""
    stats = thong_ke_heatmap(lab=lab, log_path=log_path, min_samples=min_samples)
    tieu_de = f"## Heatmap khái niệm lớp kẹt nhất ({lab})" if lab else "## Heatmap khái niệm lớp kẹt nhất"
    if not stats["du_du_lieu"]:
        return f"{tieu_de}\n\nchưa đủ dữ liệu ({stats['tong_luot']}/{min_samples} lượt hỏi)."

    lines = [
        tieu_de,
        "",
        f"Tổng lượt hỏi ẩn danh: **{stats['tong_luot']}**",
        "",
        "| Lab | CP | Khái niệm | Mức độ |",
        "|---|---|---|---|",
    ]
    for item in stats["top_ket"]:
        cp_label = item["cp"] or "—"
        lines.append(f"| {item['lab']} | {cp_label} | {item['khai_niem']} | {item['badge']} |")
    return "\n".join(lines)
