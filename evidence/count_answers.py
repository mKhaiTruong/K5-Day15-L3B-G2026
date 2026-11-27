import csv, sys, statistics as st
from collections import Counter, defaultdict
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
print("total rows", len(rows), "learners", len({r["hv"] for r in rows}))
print("by nguon", Counter(r["nguon"] for r in rows))
by = defaultdict(list)
for r in rows: by[r["nguon"]].append(r)

g = by["giai_thich"]
print("\n== giai_thich:", len(g), "rows,", len({r['hv'] for r in g}), "learners")
print("trang_thai_cham", Counter(r["trang_thai_cham"] for r in g))
dc = [r for r in g if r["trang_thai_cham"] == "da_cham"]
for k in ["rubric_bam_bai", "rubric_y_moi", "rubric_dung_ngu_canh"]:
    print(k, sorted(Counter(r[k] for r in dc).items()))
L = [int(r["do_dai_noi_dung"] or 0) for r in g]
print("len median", st.median(L), "<=20 chars", sum(x <= 20 for x in L), "/", len(L), " ==0:", sum(x == 0 for x in L))
g1 = [r for r in g if r["lan_thu"] == "1"]
print("giai_thich lan_thu=1:", len(g1))

# link explanation to the answer it explains: same hv, ref explain:<qid> -> answer ref <qid>
ans = {}
for r in rows:
    if r["nguon"] not in ("giai_thich", "chat") and r["was_correct"] in ("True", "False") and r["lan_thu"] == "1":
        ans[(r["hv"], r["ref"])] = r["was_correct"]
pair = Counter()
for r in dc:
    q = r["ref"].split("explain:", 1)[-1]
    c = ans.get((r["hv"], q))
    if c is None: continue
    weak = r["rubric_y_moi"] in ("0",) or r["rubric_dung_ngu_canh"] in ("0",)
    pair[(c, "weak" if weak else "ok")] += 1
print("answer correct x explanation (weak = y_moi 0 or dung_ngu_canh 0):", dict(pair))

t = by["thuc_hanh"]
print("\n== thuc_hanh:", len(t), "rows,", len({r['hv'] for r in t}), "learners; correct", Counter(r["was_correct"] for r in t))
th_hv = {r["hv"] for r in t}; gt_hv = {r["hv"] for r in g}
print("thuc_hanh learners who ever wrote giai_thich:", len(th_hv & gt_hv), "/", len(th_hv))

c = by["chat"]; cc = [r for r in c if r["trang_thai_cham"] == "da_cham"]
print("\n== chat graded:", len(cc), "rubric_y_moi", sorted(Counter(r["rubric_y_moi"] for r in cc).items()))
