"""Feature 2 (nguồn thứ hai): lớp kẹt ở đâu, đếm từ data preclass BTC cấp (không phải log của app).

Đọc `data-btc/preclass/answers.csv` (gitignored, không commit), chỉ trả số gộp theo Day × khái niệm
(`kc_code`): bao nhiêu **người** làm sai ngay lần đầu ở bài ôn cuối ngày (`nguon = pre_post_post`,
`lan_thu = 1`). Không trả mã học viên hay dòng data nào. Ô dưới MIN_NGUOI người → "chưa đủ dữ liệu".

    python codebase/f2_preclass.py     → in bảng top khái niệm lớp kẹt nhất mỗi Day
"""
import csv
import os
import re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CSV = os.path.join(ROOT, "data-btc", "preclass", "answers.csv")
MIN_NGUOI = 5


def thong_ke_preclass(path: str | None = None, min_nguoi: int = MIN_NGUOI) -> dict:
    """Đếm số người sai lần đầu ở bài ôn theo Day × khái niệm, chỉ số gộp.

    Args:
        path: Đường dẫn answers.csv (mặc định biến môi trường PRECLASS_CSV, rồi data-btc/preclass/answers.csv).
        min_nguoi: Ô có ít người làm hơn số này thì đánh dấu chưa đủ dữ liệu (du = False).

    Returns:
        {"co_du_lieu": bool, "nguon": str, "min_nguoi": int, "theo_day": [...]}; mỗi Day:
        {"day": "Day06", "bai": "data-engineering-for-agents", "sai": 9, "tong": 14,
         "khai_niem": [{"kc": "raw_clean_serve_layers", "sai": 5, "tong": 7, "du": True}, ...]}.
        Day: sai = số người sai ≥1 khái niệm ở lần đầu, tong = số người làm bài ôn hôm đó;
        luot_sai / luot = cộng (người × khái niệm) sai / đã làm (dùng tô màu, không bão hoà như "sai ≥1");
        du = tong ≥ min_nguoi.
        Khái niệm xếp ô đủ dữ liệu trước, rồi tỉ lệ sai giảm dần. Không có file → co_du_lieu False, theo_day [].
    """
    path = path or os.environ.get("PRECLASS_CSV") or DEFAULT_CSV
    ket_qua = {"co_du_lieu": False, "nguon": "data preclass BTC (answers.csv, số gộp)", "min_nguoi": min_nguoi,
               "theo_day": []}
    if not os.path.isfile(path):
        return ket_qua
    o = defaultdict(lambda: [set(), set()])      # (day, kc) → [người làm, người sai]
    ngay = defaultdict(lambda: [set(), set()])   # day → [người làm, người sai ≥1]
    bai = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("nguon") != "pre_post_post" or str(r.get("lan_thu")) != "1" or not r.get("hv"):
                continue
            m = re.search(r"day(\d+)(?::([\w-]+))?", r.get("lesson_id") or "", re.IGNORECASE)
            if not m or not r.get("kc_code"):
                continue
            day = f"Day{int(m.group(1)):02d}"
            bai.setdefault(day, m.group(2) or "")
            sai = str(r.get("was_correct")).strip().lower() == "false"
            for d in (o[(day, r["kc_code"])], ngay[day]):
                d[0].add(r["hv"])
                if sai:
                    d[1].add(r["hv"])
    for day in sorted(ngay):
        kn = [{"kc": kc, "sai": len(v[1]), "tong": len(v[0]), "du": len(v[0]) >= min_nguoi}
              for (d, kc), v in o.items() if d == day]
        kn.sort(key=lambda k: (not k["du"], -k["sai"] / k["tong"], k["kc"]))
        ket_qua["theo_day"].append({"day": day, "bai": bai[day], "sai": len(ngay[day][1]),
                                    "tong": len(ngay[day][0]), "luot_sai": sum(k["sai"] for k in kn),
                                    "luot": sum(k["tong"] for k in kn), "du": len(ngay[day][0]) >= min_nguoi,
                                    "khai_niem": kn})
    ket_qua["co_du_lieu"] = bool(ket_qua["theo_day"])
    return ket_qua


def main() -> int:
    """In top 3 khái niệm lớp kẹt nhất mỗi Day (chỉ ô đủ dữ liệu)."""
    import sys

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    tk = thong_ke_preclass()
    if not tk["co_du_lieu"]:
        print("Chưa có data preclass (data-btc/preclass/answers.csv).")
        return 0
    for d in tk["theo_day"]:
        top = [k for k in d["khai_niem"] if k["du"]][:3]
        print(f"{d['day']} {d['bai']}: {d['sai']}/{d['tong']} người sai ≥1 khái niệm ở lần đầu")
        for k in top:
            print(f"    {k['sai']}/{k['tong']}  {k['kc']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
