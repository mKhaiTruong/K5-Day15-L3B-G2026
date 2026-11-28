"""Feature 2: Heatmap câu hỏi ẩn danh ("🔥 x/N lượt hỏi" hoặc "🔥 x/N bạn hỏi ở đây" + bảng lớp kẹt nhất).

Chỉ đọc log từ data/heatmap/cau_hoi.jsonl và JSON output của lõi (answer(text)["output"]).
Không sửa codebase/agent.py, tools.py, ai.py; không lưu hay hiển thị thông tin cá nhân.
"""

from __future__ import annotations

import json
import os
from collections import Counter, defaultdict

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


def _lay_id_an_danh(row: dict) -> str | None:
    for key in ("id", "anon_id", "session_id", "user_id"):
        val = row.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return None


def thong_ke_heatmap(
    lab: str | None = None,
    log_path: str | None = None,
    min_samples: int = MIN_SAMPLES,
) -> dict:
    """Tổng hợp tần suất (lab, cp, khai_niem); dưới min_samples trả về 'chưa đủ dữ liệu'.

    Nếu mọi dòng log đều có id ẩn danh: mẫu số N = số người duy nhất, badge '🔥 x/N bạn hỏi ở đây'.
    Nếu không có id ẩn danh (mặc định của tools.py): mẫu số N = tổng số câu hỏi, badge '🔥 x/N lượt hỏi'.
    """
    rows = doc_log(log_path)
    if lab:
        target = lab.strip().lower()
        rows = [r for r in rows if str(r.get("lab") or "").strip().lower() == target]

    co_id = bool(rows) and all(_lay_id_an_danh(r) is not None for r in rows)
    if co_id:
        mau_so = len({_lay_id_an_danh(r) for r in rows})
        don_vi = "bạn hỏi ở đây"
        loai_mau_so = "nguoi"
    else:
        mau_so = len(rows)
        don_vi = "lượt hỏi"
        loai_mau_so = "luot_hoi"

    if mau_so < min_samples:
        return {
            "du_du_lieu": False,
            "thong_bao": "chưa đủ dữ liệu",
            "loai_mau_so": loai_mau_so,
            "don_vi": don_vi,
            "tong_luot": mau_so,
            "top_ket": [],
        }

    if co_id:
        id_sets: dict[tuple[str, str, str], set[str]] = defaultdict(set)
        for r in rows:
            uid = _lay_id_an_danh(r)
            assert uid is not None
            r_lab = str(r.get("lab") or "").strip()
            r_cp = str(r.get("cp") or "").strip()
            concepts = r.get("khai_niem") or []
            if not isinstance(concepts, list):
                continue
            for c in concepts:
                ten = str(c).strip()
                if ten:
                    id_sets[(r_lab, r_cp, ten)].add(uid)
        sorted_items = sorted(
            ((k, len(uids)) for k, uids in id_sets.items()),
            key=lambda kv: (-kv[1], kv[0]),
        )
    else:
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
        sorted_items = counts.most_common()

    top_ket = [
        {
            "lab": k_lab,
            "cp": k_cp,
            "khai_niem": k_ten,
            "so_luot": so_luot,
            "tong_luot": mau_so,
            "badge": f"🔥 {so_luot}/{mau_so} {don_vi}",
        }
        for (k_lab, k_cp, k_ten), so_luot in sorted_items
    ]
    return {
        "du_du_lieu": True,
        "thong_bao": None,
        "loai_mau_so": loai_mau_so,
        "don_vi": don_vi,
        "tong_luot": mau_so,
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
    """Gắn badge '🔥 x/N lượt hỏi' hoặc '🔥 x/N bạn hỏi ở đây' (hoặc 'chưa đủ dữ liệu') cho từng khái niệm."""
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
                "badge": f"🔥 {so_luot}/{tong} {stats['don_vi']}",
            }
        )
    return badges


def bao_cao_markdown(
    lab: str | None = None,
    log_path: str | None = None,
    min_samples: int = MIN_SAMPLES,
) -> str:
    """Xuất bảng 'Khái niệm / CP nào lớp kẹt nhất' dạng Markdown ẩn danh, ghi rõ mẫu số N."""
    stats = thong_ke_heatmap(lab=lab, log_path=log_path, min_samples=min_samples)
    tieu_de = f"## Heatmap khái niệm lớp kẹt nhất ({lab})" if lab else "## Heatmap khái niệm lớp kẹt nhất"
    if not stats["du_du_lieu"]:
        don_vi_ngan = "người" if stats["loai_mau_so"] == "nguoi" else "lượt hỏi"
        return f"{tieu_de}\n\nchưa đủ dữ liệu ({stats['tong_luot']}/{min_samples} {don_vi_ngan})."

    if stats["loai_mau_so"] == "nguoi":
        giai_thich_mau = (
            f"Mẫu số N = **{stats['tong_luot']}** người dùng ẩn danh "
            "(1 người có thể hỏi nhiều khái niệm nên tổng số theo khái niệm có thể > N)."
        )
    else:
        giai_thich_mau = (
            f"Mẫu số N = **{stats['tong_luot']}** lượt hỏi "
            "(1 câu hỏi có thể trúng nhiều khái niệm nên tổng lượt theo khái niệm có thể > N)."
        )

    lines = [
        tieu_de,
        "",
        giai_thich_mau,
        "",
        "| Lab | CP | Khái niệm | Mức độ |",
        "|---|---|---|---|",
    ]
    for item in stats["top_ket"]:
        cp_label = item["cp"] or "—"
        lines.append(f"| {item['lab']} | {cp_label} | {item['khai_niem']} | {item['badge']} |")
    return "\n".join(lines)


def main() -> int:
    """Chạy xem nhanh báo cáo heatmap trên terminal: python codebase/f2_heatmap.py [--lab Day14]."""
    import argparse
    import sys

    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Heatmap khái niệm lớp kẹt nhất (ẩn danh)")
    parser.add_argument("--lab", default=None, help="Lọc theo mã lab, vd Day14")
    parser.add_argument("--log", default=None, help="Đường dẫn tới cau_hoi.jsonl")
    args = parser.parse_args()
    print(bao_cao_markdown(lab=args.lab, log_path=args.log))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
