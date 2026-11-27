"""Chấm 4 metric trong eval/metric_spec.yaml cho một lượt chạy.

  python eval/grade_metrics.py eval/run-1.csv [--slides ds_ma_slide.txt] [--dry]

- Trượt metric nào: điền pass = 0, ghi tên metric vào ghi_chu.
- Qua hết metric: để trống pass, người chấm đọc pass_criterion rồi điền 1 / 0.
- Chỉ sửa 2 cột pass và ghi_chu; ô pass đã điền thì giữ nguyên. --dry: chỉ in, không ghi file.
- --slides: file mỗi dòng một mã đoạn có thật (vd Day14-s12). Thiếu thì CHƯA kiểm được mã có thật hay không.
"""
import csv
import json
import re
import sys

PAIR = re.compile(r"([\w./-]+\.\w+):(\w+)\s*\((sua|doc)\b[^)]*\)")
CODE = re.compile(r"Day\d{2}-s\d+")
NONE = "khong_co_can_cu"


def parse_expected(text):
    text = text.strip()
    for kind in ("can_hoi_lai", "tu_choi"):
        if text.startswith(kind):
            return {"kind": kind, "pairs": {}, "frame": set(), "slides": None}
    pairs = {(f, h): label for f, h, label in PAIR.findall(text)}
    frame = set()
    m = re.search(r"khong_dung:\s*([^;]+)", text)
    if m:
        frame = {x.strip().rstrip(".") for x in m.group(1).split(",") if x.strip()}
    slides = None  # None = expected không ghi gì về slide
    m = re.search(r"slide:\s*([^;]+)", text)
    if m:
        slides = set(CODE.findall(m.group(1))) or ({NONE} if NONE in m.group(1) else None)
    return {"kind": "map", "pairs": pairs, "frame": frame, "slides": slides}


def parse_output(text):
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip())
    try:
        data = json.loads(text)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def check(expected, output, valid_slides=None):
    """→ {tên metric: True / False} cho các metric áp cho câu này."""
    exp = parse_expected(expected)
    out = parse_output(output)
    ok = out is not None
    out = out or {}
    concepts = [c for c in out.get("khai_niem") or [] if isinstance(c, dict)]
    entries = [e for c in concepts for e in c.get("code") or [] if isinstance(e, dict)]
    result = {"khong_sua_file_khung": ok and not any(
        e.get("nhan") == "sua" and e.get("file") in exp["frame"] for e in entries)}
    if exp["kind"] != "map":
        result["hoi_lai_va_tu_choi_dung"] = ok and bool(out.get(exp["kind"])) and not concepts
        return result
    if not exp["pairs"]:
        raise ValueError("expected không đọc được cặp file:hàm (nhãn): " + expected)
    seen = [((e.get("file"), e.get("ham")), e.get("nhan")) for e in entries]
    right = any(exp["pairs"].get(k) == label for k, label in seen)
    wrong = any(k in exp["pairs"] and exp["pairs"][k] != label for k, label in seen)
    result["tro_dung_code"] = ok and right and not wrong

    grounded = ok and bool(concepts)
    cited = set()
    for c in concepts:
        value = str(c.get("slide") or "")
        codes = set(CODE.findall(value))
        cited |= codes
        if not codes and value.strip() != NONE:
            grounded = False
        if valid_slides is not None and not codes <= valid_slides:
            grounded = False
    if exp["slides"] == {NONE}:
        grounded = grounded and not cited
    elif exp["slides"]:
        grounded = grounded and bool(cited & exp["slides"])
    result["co_can_cu_slide"] = grounded
    return result


def main(argv):
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8", errors="replace")
    dry = "--dry" in argv
    args = [a for a in argv if a != "--dry"]
    valid = None
    if "--slides" in args:
        i = args.index("--slides")
        with open(args[i + 1], encoding="utf-8-sig") as f:
            valid = {line.strip() for line in f if line.strip()}
        del args[i:i + 2]
    if len(args) != 1:
        sys.exit(__doc__)
    with open(args[0], encoding="utf-8-sig", newline="") as f:
        delim = ";" if f.readline().count(";") > 5 else ","
        f.seek(0)
        reader = csv.DictReader(f, delimiter=delim)
        fields, rows = reader.fieldnames, list(reader)
    totals = {}
    for row in rows:
        result = check(row["expected"], row.get("output") or "", valid)
        for name, passed in result.items():
            n, total = totals.get(name, (0, 0))
            totals[name] = (n + passed, total + 1)
        failed = [name for name, passed in result.items() if not passed]
        print("%s  %s" % (row["id"], "trượt: " + ", ".join(failed) if failed else "qua metric, chờ người chấm pass_criterion"))
        if failed and not (row.get("pass") or "").strip():
            row["pass"] = "0"
            row["ghi_chu"] = " | ".join(x for x in [row.get("ghi_chu"), "trượt metric: " + ", ".join(failed)] if x)
    for name, (n, total) in totals.items():
        print("%-26s %d/%d" % (name, n, total))
    if valid is None:
        print("CHƯA kiểm mã slide có thật hay không (thiếu --slides).")
    if not dry:
        with open(args[0], "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fields, delimiter=delim)
            writer.writeheader()
            writer.writerows(rows)


if __name__ == "__main__":
    main(sys.argv[1:])
