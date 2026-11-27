import csv, sys
from collections import Counter, defaultdict
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8-sig")))
def d(r): return r["created_at"][:10]
for src in ("thuc_hanh", "giai_thich", "pre_post_post"):
    s = [r for r in rows if r["nguon"] == src]
    print(src, "dates", min(map(d, s)), "->", max(map(d, s)), "kc filled", sum(bool(r["kc_code"]) for r in s), "/", len(s))
th = [r for r in rows if r["nguon"] == "thuc_hanh"]
gt = [r for r in rows if r["nguon"] == "giai_thich"]
start = min(map(d, gt))
th_after = {r["hv"] for r in th if d(r) >= start}
print("thuc_hanh learners active from", start, ":", len(th_after), "| of them wrote giai_thich:", len(th_after & {r['hv'] for r in gt}))
print("thuc_hanh first-try correct:", sum(r["was_correct"]=="True" for r in th if r["lan_thu"]=="1"), "/", sum(r["lan_thu"]=="1" for r in th))
print("labs:", Counter(r["ref"].split(":")[1] for r in th).most_common(8))
# passed lab on KC, then post-quiz same KC first try
lab_kc = defaultdict(set)
for r in th:
    if r["was_correct"] == "True" and r["kc_code"]: lab_kc[r["hv"]].add(r["kc_code"])
post = [r for r in rows if r["nguon"]=="pre_post_post" and r["lan_thu"]=="1" and r["was_correct"] in ("True","False")]
pairs = [(r["hv"], r["kc_code"], r["was_correct"]) for r in post if r["kc_code"] in lab_kc.get(r["hv"], ())]
print("post-quiz answers on KC the learner already passed in lab:", len(pairs), "wrong:", sum(p[2]=="False" for p in pairs),
      "learners:", len({p[0] for p in pairs}), "learners with >=1 wrong:", len({p[0] for p in pairs if p[2]=="False"}))
allpost = Counter(r["was_correct"] for r in post); print("all post first-try:", dict(allpost))
ex = [p for p in pairs if p[2]=="False"][:6]; print("examples:", ex)
# time-ordered: post-quiz strictly after the learner's first passed lab step on that KC
first_pass = {}
for r in th:
    if r["was_correct"] == "True" and r["kc_code"]:
        k = (r["hv"], r["kc_code"]); first_pass[k] = min(first_pass.get(k, r["created_at"]), r["created_at"])
ordered = [r for r in post if (r["hv"], r["kc_code"]) in first_pass and r["created_at"] > first_pass[(r["hv"], r["kc_code"])]]
w = [r for r in ordered if r["was_correct"] == "False"]
print("ORDERED: answers", len(ordered), "wrong", len(w), "| learners", len({r['hv'] for r in ordered}), "with>=1 wrong", len({r['hv'] for r in w}))
print("ORDERED examples:", [(r["id"], r["kc_code"]) for r in w[:6]])
