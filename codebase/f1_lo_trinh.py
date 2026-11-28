"""Feature 1: lộ trình đọc file theo CP + sơ đồ flow, dựng từ output của lõi (không gọi AI).

Hợp đồng: chỉ đọc output JSON của agent.answer() (format ở đầu eval/metric_spec.yaml),
không gọi vào hàm nội bộ của lõi. Phần sơ đồ đọc dòng import của các file trong lộ trình
bằng ast (không chạy code lab).

    lo_trinh(output)            → ≤5 bước đọc file
    do_thi_import(repo, files)  → mũi tên "file A import file B" giữa các file đó
    ve_mermaid(lt, canh)        → sơ đồ Mermaid (text)
    ve_html(lab, muc)           → trang HTML kiểu wiki: sidebar CP + sơ đồ + lộ trình (theme gatsby, material wax)
"""
import ast
import html
import os
import urllib.parse

MAX_BUOC = 5
ISSUE_URL = "https://github.com/mKhaiTruong/K5-Day15-L3B-G2026/issues/new"
MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs"


def lo_trinh(output: dict) -> dict:
    """Xếp bản đồ khái niệm của lõi thành lộ trình ≤5 bước đọc file.

    Gom theo file; file có hàm nhãn "sua" thì cả bước là "sua". File "doc" đứng trước
    (đọc bối cảnh), rồi tới file "sua"; cùng nhãn thì giữ thứ tự xuất hiện trong output.
    File khung không thành bước nào, chỉ nằm trong "khong_dung".

    Args:
        output: Dict đã parse từ answer(text)["output"].

    Returns:
        Dict gồm:
            "lab", "cp": như output của lõi.
            "buoc": list bước, vd [{"so": 1, "file": "src/lab13.py", "nhan": "sua",
                    "ham": ["mo_hinh"], "khai_niem": ["Chi phí mỗi việc thành công"],
                    "slide": ["Day13-s12"]}].
            "con_lai": số file bị cắt vì quá MAX_BUOC.
            "khong_dung": list file khung.
            "loi_nhan": câu từ chối / hỏi lại của lõi, None nếu có lộ trình.
    """
    if "tu_choi" in output:
        return _rong(output, output["tu_choi"])

    theo_file = {}
    for k in output.get("khai_niem") or []:
        for c in k.get("code") or []:
            if c.get("nhan") == "khong_dung":
                continue

            b = theo_file.setdefault(
                c["file"], {"file": c["file"], "nhan": "doc",
                            "ham": [], "khai_niem": [], "slide": []})

            if c.get("nhan") == "sua":
                b["nhan"] = "sua"

            _them(b["ham"], c.get("ham"))
            _them(b["khai_niem"], k.get("ten"))
            if k.get("slide") and k["slide"] != "khong_co_can_cu":
                _them(b["slide"], k["slide"])

    if not theo_file:
        return _rong(output, output.get("can_hoi_lai") or "Chưa có lộ trình cho câu này.")

    xep = [b for b in theo_file.values() if b["nhan"] == "doc"] + \
          [b for b in theo_file.values() if b["nhan"] == "sua"]
    buoc = [dict(b, so=i) for i, b in enumerate(xep[:MAX_BUOC], 1)]

    return {"lab": output.get("lab"), "cp": output.get("cp"), "buoc": buoc,
            "con_lai": max(0, len(xep) - MAX_BUOC), "khong_dung": output.get("khong_dung") or [],
            "loi_nhan": None}


def _them(ds: list, x) -> None:
    """Thêm x vào ds nếu có giá trị và chưa có (giữ thứ tự)."""
    if x and x not in ds:
        ds.append(x)


def _rong(output: dict, loi_nhan: str) -> dict:
    """Lộ trình rỗng kèm lời nhắn của lõi (từ chối / hỏi lại)."""
    return {"lab": output.get("lab"), "cp": output.get("cp"), "buoc": [], "con_lai": 0,
            "khong_dung": output.get("khong_dung") or [], "loi_nhan": loi_nhan}


def do_thi_import(repo: str, files: list) -> list:
    """Tìm các cặp "file A import file B" giữa các file .py trong lộ trình.

    Đọc bằng ast, không chạy code. Chỉ giữ cạnh tới file nằm trong `files`
    (import thư viện ngoài bị bỏ). Khớp module theo đuôi đường dẫn, vd
    `from app.auth import x` trong `06-lab/app/main.py` khớp `06-lab/app/auth.py`;
    import tương đối (`from .auth import x`) tính từ thư mục của file.

    Args:
        repo: Đường dẫn thư mục repo lab.
        files: Đường dẫn tương đối (dạng a/b.py) của các file trong lộ trình.

    Returns:
        List cặp (file_import, file_bi_import) không trùng, không có cạnh tự trỏ,
        vd [("06-lab/app/main.py", "06-lab/app/auth.py")].
    """
    py = [f for f in dict.fromkeys(files) if f.endswith(".py")]
    canh = []
    for src in py:
        try:
            with open(os.path.join(repo, src), encoding="utf-8-sig", errors="replace") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError, ValueError):
            continue
        for mod in _modules(tree, os.path.dirname(src)):
            dst = _khop_file(mod, py)
            if dst and dst != src and (src, dst) not in canh:
                canh.append((src, dst))
    return canh


def _modules(tree: ast.AST, thu_muc: str) -> list:
    """Đổi các lệnh import thành đường dẫn ứng viên dạng "a/b" (chưa có đuôi .py).

    `from x import y` sinh cả "x" lẫn "x/y" (y có thể là module con).
    Import tương đối (level ≥ 1) ghép vào `thu_muc` của file, lùi lên (level - 1) cấp.
    """
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            out += [a.name.replace(".", "/") for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            base = (node.module or "").replace(".", "/")
            if node.level:
                goc = thu_muc
                for _ in range(node.level - 1):
                    goc = os.path.dirname(goc)
                base = "/".join(p for p in (goc.replace(os.sep, "/"), base) if p)
            if base:
                out.append(base)
            out += ["/".join(p for p in (base, a.name) if p) for a in node.names if a.name != "*"]
    return out


def _khop_file(mod: str, py: list):
    """Tìm file trong `py` ứng với module "a/b": a/b.py hoặc a/b/__init__.py, khớp theo đuôi."""
    for duoi in (mod + ".py", mod + "/__init__.py"):
        for f in py:
            if f == duoi or f.endswith("/" + duoi):
                return f
    return None


def ve_mermaid(lt: dict, canh: list) -> str:
    """Vẽ lộ trình thành sơ đồ Mermaid: ô theo bước, mũi tên đứt = thứ tự đọc, mũi tên liền = import.

    Ô ✏️ sửa / 📖 đọc tô 2 màu dịu khác nhau; file khung gom vào 1 ô ⛔ riêng, không nối mũi tên.

    Args:
        lt: Kết quả của lo_trinh().
        canh: Kết quả của do_thi_import() trên các file của lộ trình.

    Returns:
        Chuỗi Mermaid bắt đầu bằng "flowchart LR", hoặc "" nếu lộ trình rỗng.
    """
    if not lt.get("buoc"):
        return ""
    lines = ["flowchart LR"]
    ids = {}
    for b in lt["buoc"]:
        nid = f"B{b['so']}"
        ids[b["file"]] = nid
        icon = "✏️ sửa" if b["nhan"] == "sua" else "📖 đọc"
        nhan = f"{b['so']} · {icon}<br/>{_esc(b['file'])}"
        if b["ham"]:
            nhan += "<br/><small>" + _esc(", ".join(b["ham"][:4])) + ("…" if len(b["ham"]) > 4 else "") + "</small>"
        if b["slide"]:
            nhan += "<br/><small>" + _esc(" · ".join(b["slide"])) + "</small>"
        lines.append(f'    {nid}["{nhan}"]:::{b["nhan"]}')
    for a, b in zip(lt["buoc"], lt["buoc"][1:]):
        lines.append(f"    {ids[a['file']]} -.-> {ids[b['file']]}")
    for src, dst in canh:
        if src in ids and dst in ids:
            lines.append(f"    {ids[src]} -->|import| {ids[dst]}")
    if lt.get("khong_dung"):
        ds = "<br/>".join(_esc(f) for f in lt["khong_dung"][:6])
        more = f"<br/>… +{len(lt['khong_dung']) - 6}" if len(lt["khong_dung"]) > 6 else ""
        lines.append(f'    K["⛔ Đừng đụng<br/>{ds}{more}"]:::khung')
    lines += ["    classDef doc fill:#D1DFE4,stroke:#28303D,stroke-width:2px,color:#28303D",   # gatsby: xanh lạnh
              "    classDef sua fill:#EEEADD,stroke:#28303D,stroke-width:3px,color:#28303D",   # gatsby: kem ấm
              "    classDef khung fill:#E4D1D1,stroke:#A0474A,stroke-width:2px,color:#28303D"]  # gatsby: đỏ nhạt
    return "\n".join(lines)


MAX_NUT = 9  # >9 ô thì sơ đồ nên tách đôi (nguyên tắc mật độ ~4/10)
CAP_HAM_TOI_DA_FILE = 2  # lộ trình ≤2 file → vẽ cấp hàm; nhiều hơn → cấp file (import)


def do_thi_goi_ham(repo: str, buoc: list, toi_da: int = MAX_NUT) -> dict:
    """Tìm hàm nào gọi hàm nào giữa các hàm trong lộ trình (đọc bằng ast, không chạy code lab).

    Ô chính = hàm lõi đã trỏ tới (nhãn của bước: sua / doc). Nếu còn chỗ (≤ toi_da ô), thêm hàm
    cùng file mà các hàm chính gọi tới, nhãn "phu" (để thấy hàm phải viết dựa vào đâu).
    Chỉ tính lời gọi trực tiếp theo tên `ham(...)`; gọi qua thuộc tính (`obj.ham()`) bỏ qua.

    Args:
        repo: Đường dẫn repo lab.
        buoc: lo_trinh(...)["buoc"].
        toi_da: Số ô tối đa.

    Returns:
        {"nut": [{"id": "n1", "file", "ham", "nhan"}], "canh": [("n1", "n2"), ...]}; cạnh = ô trái gọi ô phải.
        Vd Day13 CP1: mo_hinh → he_so_chi_phi_moi_viec_thanh_cong → so_lan_chay_ky_vong.
    """
    defs = {}  # (file, ten) -> ast node
    for b in buoc:
        if not b["file"].endswith(".py") or any(f == b["file"] for f, _ in defs):
            continue
        try:
            with open(os.path.join(repo, b["file"]), encoding="utf-8-sig", errors="replace") as fh:
                tree = ast.parse(fh.read())
        except (OSError, SyntaxError, ValueError):
            continue
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs[(b["file"], n.name)] = n
    chinh = [(b["file"], h, b["nhan"]) for b in buoc for h in b["ham"] if (b["file"], h) in defs]
    ten_chinh = {}  # tên → (file, tên), chỉ khi tên là duy nhất trong lộ trình (để nối khác file)
    for f, h, _ in chinh:
        ten_chinh[h] = None if h in ten_chinh else (f, h)

    def goi(f: str, h: str) -> list:
        ra = []
        for c in ast.walk(defs[(f, h)]):
            if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id != h:
                dich = (f, c.func.id) if (f, c.func.id) in defs else ten_chinh.get(c.func.id)
                if dich and dich not in ra:
                    ra.append(dich)
        return ra

    nut = {(f, h): nhan for f, h, nhan in chinh[:toi_da]}
    for f, h, _ in chinh[:toi_da]:
        for d in goi(f, h):
            if d not in nut and len(nut) < toi_da:
                nut[d] = "phu"
    ids = {k: f"n{i}" for i, k in enumerate(nut, 1)}
    canh = [(ids[k], ids[d]) for k in nut for d in goi(*k) if d in ids]
    return {"nut": [{"id": ids[k], "file": k[0], "ham": k[1], "nhan": v} for k, v in nut.items()],
            "canh": canh}


MAU_GATSBY = {"doc": "#D1DFE4", "sua": "#EEEADD", "phu": "#FFFFFF", "khung": "#E4D1D1",
              "net": "#28303D", "loi": "#A0474A"}


def ve_mermaid_ham(do_thi: dict, khong_dung: list = (), mau: dict = MAU_GATSBY) -> str:
    """Vẽ sơ đồ cấp hàm: mỗi file 1 khung, mỗi hàm 1 ô, mũi tên = gọi hàm.

    Chỉ ô ✏️ sửa được tô màu nhấn (1–2 điểm nhấn mỗi sơ đồ); 📖 đọc tô nhạt; hàm phụ để trắng.

    Args:
        do_thi: Kết quả do_thi_goi_ham().
        khong_dung: File khung, gom vào 1 ô ⛔ riêng.
        mau: Bảng màu {"doc", "sua", "phu", "khung", "net", "loi"} (mặc định theme gatsby).

    Returns:
        Chuỗi Mermaid "flowchart LR", hoặc "" nếu không có ô nào.
    """
    if not do_thi.get("nut"):
        return ""
    lines = ["flowchart LR"]
    icon = {"sua": "✏️ ", "doc": "📖 ", "phu": ""}
    for i, f in enumerate(dict.fromkeys(n["file"] for n in do_thi["nut"]), 1):
        lines.append(f'    subgraph F{i}["{_esc(f)}"]')
        lines += [f'        {n["id"]}["{icon[n["nhan"]]}{_esc(n["ham"])}()"]:::{n["nhan"]}'
                  for n in do_thi["nut"] if n["file"] == f]
        lines.append("    end")
    lines += [f"    {a} --> {b}" for a, b in do_thi["canh"]]
    if khong_dung:
        ds = "<br/>".join(_esc(f) for f in list(khong_dung)[:6])
        more = f"<br/>… +{len(khong_dung) - 6}" if len(khong_dung) > 6 else ""
        lines.append(f'    K["⛔ Đừng đụng<br/>{ds}{more}"]:::khung')
    net = mau["net"]
    lines += [f"    classDef sua fill:{mau['sua']},stroke:{net},stroke-width:3px,color:{net}",
              f"    classDef doc fill:{mau['doc']},stroke:{net},stroke-width:1px,color:{net}",
              f"    classDef phu fill:{mau['phu']},stroke:{net},stroke-width:1px,stroke-dasharray:4 3,color:{net}",
              f"    classDef khung fill:{mau['khung']},stroke:{mau['loi']},stroke-width:2px,color:{net}"]
    return "\n".join(lines)


def so_do(repo: str, lt: dict) -> dict:
    """Chọn cấp sơ đồ cho 1 lộ trình: ≤2 file → cấp hàm (gọi hàm), nhiều hơn → cấp file (import).

    Returns:
        {"mermaid": str, "cap": "ham" | "file", "chu_thich": str}; mermaid rỗng nếu lộ trình rỗng.
    """
    files = [b["file"] for b in lt.get("buoc", [])]
    if files and len(files) <= CAP_HAM_TOI_DA_FILE:
        dt = do_thi_goi_ham(repo, lt["buoc"])
        if dt["nut"]:
            return {"mermaid": ve_mermaid_ham(dt, lt.get("khong_dung") or []), "cap": "ham",
                    "chu_thich": "Mỗi khung là 1 file, mỗi ô là 1 hàm. Mũi tên: hàm này gọi hàm kia. "
                                 "Ô viền đứt: hàm phụ được gọi tới, không nằm trong lộ trình."}
    return {"mermaid": ve_mermaid(lt, do_thi_import(repo, files)), "cap": "file",
            "chu_thich": "Mũi tên đứt: thứ tự đọc. Mũi tên liền: file này import file kia."}


def _esc(text: str) -> str:
    """Thoát ký tự làm vỡ nhãn Mermaid (ngoặc kép, <, >)."""
    return str(text).replace("&", "&amp;").replace('"', "#quot;").replace("<", "&lt;").replace(">", "&gt;")


CSS = """
:root {
  --bg: #D1E4DD; --surface: #FFFFFF; --primary: #28303D; --text: #39414D; --muted: #4F5866;
  --soft: #D1DFE4; --accent: #EEEADD; --khung: #E4D1D1; --error: #A0474A;
  --font: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen-Sans, Ubuntu, Cantarell, "Helvetica Neue", sans-serif;
  --fs-body: 20px; --fs-sm: 18px; --fs-xs: 16px; --fs-h2: 36px; --fs-h3: 24px;
  --space: 20px; --space-x: 25px; --space-y: 30px;
}
@media (min-width: 652px) { :root { --fs-h2: 48px; } }
* { box-sizing: border-box; border-radius: 0; }
body { margin: 0; background: var(--bg); color: var(--text); font: 400 var(--fs-body)/1.7 var(--font); }
h2 { font-size: var(--fs-h2); line-height: 1.3; font-weight: 400; color: var(--primary); margin: 0 0 var(--space); }
h3 { font-size: var(--fs-h3); line-height: 1.3; font-weight: 400; color: var(--primary); margin: 0 0 10px; }
p { margin: 0 0 var(--space); max-width: 610px; }
a { color: var(--primary); text-decoration-thickness: 1px; text-underline-offset: 3px; }
a:focus-visible, button:focus-visible { outline: 3px solid var(--primary); outline-offset: 3px; }
code { font-family: ui-monospace, Consolas, monospace; font-size: var(--fs-sm); color: var(--primary); }
.masthead { padding: var(--space-y) var(--space-x) var(--space); margin: 0 var(--space-x);
  border-bottom: 3px solid var(--primary); box-shadow: 0 5px 0 -4px var(--primary); }
.site { font-size: 24px; text-transform: uppercase; color: var(--primary); margin: 0; max-width: none; }
.sub { font-size: var(--fs-sm); color: var(--muted); margin: 5px 0 0; }
.layout { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: calc(var(--space) * 2);
  max-width: 1240px; margin: 0 auto; padding: var(--space-y) var(--space-x) calc(var(--space-y) * 2); }
nav { position: sticky; top: var(--space); align-self: start; }
nav ol { list-style: none; margin: 0; padding: 0; border-top: 3px solid var(--primary); }
nav li { border-bottom: 1px solid var(--primary); }
nav a { display: block; padding: 13px 10px; text-decoration: none; font-size: var(--fs-sm); }
nav a[aria-current="true"] { background: var(--surface); font-weight: 600; }
nav .rong { color: var(--muted); font-size: var(--fs-xs); }
.cp { margin-bottom: calc(var(--space-y) * 2); scroll-margin-top: var(--space); }
.loi-nhan { background: var(--surface); border: 3px solid var(--primary); padding: var(--space); max-width: 610px; }
.flow-wrap { position: relative; isolation: isolate; margin: var(--space-y) 16px var(--space-y) 0; }
.flow-wrap::before { content: ""; position: absolute; inset: 16px -16px -16px 16px; z-index: -1;
  border: 1px solid var(--primary);
  background: repeating-linear-gradient(-45deg, var(--primary) 0 1px, var(--soft) 1px 7px); }
.flow { background: var(--surface); border: 3px solid var(--primary); padding: var(--space); overflow-x: auto; margin: 0; }
.flow-wrap .crop { position: absolute; width: 24px; height: 24px; pointer-events: none; }
.crop.tl { top: -12px; left: -12px; border-top: 1px solid var(--primary); border-left: 1px solid var(--primary); }
.crop.br { bottom: -12px; right: -12px; border-bottom: 1px solid var(--primary); border-right: 1px solid var(--primary); }
pre.mermaid { font-size: var(--fs-xs); white-space: pre-wrap; margin: 0; }
.chu-thich { font-size: var(--fs-xs); color: var(--muted); margin-top: 26px; }
ol.steps { list-style: none; counter-reset: b; margin: 0; padding: 0; }
ol.steps > li { counter-increment: b; display: grid; grid-template-columns: 56px minmax(0, 1fr);
  gap: 0 var(--space); padding: var(--space) 0; border-top: 1px solid var(--primary); }
ol.steps > li::before { content: counter(b); font-size: 32px; line-height: 1.1; color: var(--primary); }
.nhan { display: inline-block; font-size: var(--fs-xs); font-weight: 500; padding: 2px 10px;
  border: 2px solid var(--primary); margin-right: 10px; color: var(--primary); }
.nhan.sua { background: var(--accent); } .nhan.doc { background: var(--soft); }
.meta { font-size: var(--fs-sm); margin: 6px 0 0; max-width: none; }
.slide { display: inline-block; font-size: var(--fs-xs); background: var(--surface); border: 1px solid var(--primary);
  padding: 0 8px; margin: 4px 6px 0 0; }
.bao-sai { font-size: var(--fs-xs); }
.khung { background: var(--khung); border: 3px solid var(--error); padding: var(--space); margin-top: var(--space-y); }
.khung ul { margin: 0; padding-left: 22px; font-size: var(--fs-sm); }
.cho-trong { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space); margin-top: var(--space-y); }
.cho-trong div { background: var(--accent); border: 1px dashed var(--primary); padding: 15px var(--space); font-size: var(--fs-sm); }
@media (max-width: 821px) {
  .layout { grid-template-columns: 1fr; }
  nav { position: static; }
  .cho-trong { grid-template-columns: 1fr; }
  .flow-wrap::before { inset: 10px -10px -10px 10px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
"""


def ve_html(lab: str, muc: list, issue_url: str = ISSUE_URL) -> str:
    """Dựng trang HTML kiểu wiki cho 1 lab: sidebar các CP, mỗi CP có sơ đồ flow + lộ trình đánh số.

    Theme gatsby (giấy bạc hà) + material wax (góc vuông, kẻ đôi, mảng lót lệch). Sơ đồ vẽ bằng
    Mermaid tải từ CDN; mất mạng thì vẫn thấy sơ đồ dạng text. Chỗ cho F2 (heatmap) và F3 (Feynman)
    hiện "chưa nối", không giả dữ liệu.

    Args:
        lab: Mã lab, vd "Day13".
        muc: Mỗi CP một dict {"cp": "CP1", "lt": kết quả lo_trinh(), "mermaid": kết quả ve_mermaid()}.
        issue_url: Link tạo issue GitHub cho nút "Báo chỗ sai".

    Returns:
        Chuỗi HTML hoàn chỉnh (1 file, CSS nhúng sẵn).
    """
    e = html.escape
    nav, body = [], []
    for i, m in enumerate(muc):
        cp, lt = m["cp"], m["lt"]
        sid = "cp-" + "".join(ch for ch in cp.lower() if ch.isalnum())
        nhan_cp = f"✅ {e(cp)}" if lt.get("buoc") else f'{e(cp)} <span class="rong">· chưa nối được</span>'
        cur = ' aria-current="true"' if i == 0 else ""
        nav.append(f'<li><a href="#{sid}"{cur}>{nhan_cp}</a></li>')
        body.append(_ve_cp(lab, cp, sid, lt, m.get("mermaid", ""), issue_url,
                           m.get("chu_thich") or "Mũi tên đứt: thứ tự đọc. Mũi tên liền: file này import file kia."))
    return f"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(lab)} · bản đồ bài giảng ↔ code</title>
<style>{CSS}</style>
</head>
<body>
<header class="masthead">
  <p class="site">{e(lab)} · bản đồ bài giảng ↔ code</p>
  <p class="sub">Mỗi CP: khái niệm trong slide nằm ở file nào, đọc theo thứ tự nào, file nào không được đụng.</p>
</header>
<div class="layout">
  <nav aria-label="Các checkpoint"><ol>{"".join(nav)}</ol></nav>
  <main>{"".join(body)}</main>
</div>
<script type="module">
  try {{
    const {{ default: mermaid }} = await import("{MERMAID_CDN}");
    mermaid.initialize({{ startOnLoad: false, theme: "base", securityLevel: "strict",
      themeVariables: {{ fontFamily: "Segoe UI, Roboto, sans-serif", fontSize: "16px",
        lineColor: "#28303D", primaryTextColor: "#28303D" }} }});
    await mermaid.run({{ querySelector: "pre.mermaid" }});
  }} catch (err) {{
    document.querySelectorAll(".chu-thich").forEach(n => n.textContent = "Không tải được thư viện vẽ sơ đồ (cần mạng), đang hiện sơ đồ dạng chữ.");
  }}
  const links = document.querySelectorAll("nav a");
  links.forEach(a => a.addEventListener("click", () => {{
    links.forEach(x => x.removeAttribute("aria-current")); a.setAttribute("aria-current", "true");
  }}));
</script>
</body>
</html>
"""


def _ve_cp(lab: str, cp: str, sid: str, lt: dict, mermaid: str, issue_url: str, chu_thich: str = "") -> str:
    """Một section CP: sơ đồ (điểm nhấn) → các bước đánh số → ô file khung → chỗ cho F2 / F3."""
    e = html.escape
    out = [f'<section class="cp" id="{sid}"><h2>{e(cp)}</h2>']
    if not lt.get("buoc"):
        out.append(f'<p class="loi-nhan">{e(lt.get("loi_nhan") or "Chưa có lộ trình cho CP này.")}</p>')
    else:
        out.append('<div class="flow-wrap"><span class="crop tl"></span><span class="crop br"></span>'
                   f'<figure class="flow"><pre class="mermaid">{e(mermaid)}</pre></figure></div>'
                   f'<p class="chu-thich">{e(chu_thich)}</p>')
        out.append('<ol class="steps">')
        for b in lt["buoc"]:
            nhan = "✏️ Sửa" if b["nhan"] == "sua" else "📖 Đọc"
            ham = ", ".join(e(h) for h in b["ham"])
            slides = "".join(f'<span class="slide">{e(s)}</span>' for s in b["slide"]) or \
                '<span class="slide">không có căn cứ slide</span>'
            out.append(
                f'<li><div><h3><span class="nhan {b["nhan"]}">{nhan}</span><code>{e(b["file"])}</code></h3>'
                f'<p class="meta">Hàm: <code>{ham}</code></p>'
                f'<p class="meta">Khái niệm: {e("; ".join(b["khai_niem"]))}</p>'
                f'<p class="meta">{slides}</p>'
                f'<p class="meta bao-sai"><a href="{e(_link_bao_sai(issue_url, lab, cp, b))}" target="_blank" '
                f'rel="noopener">Báo chỗ sai</a> (mở issue công khai trên GitHub)</p></div></li>')
        out.append("</ol>")
        if lt.get("con_lai"):
            out.append(f'<p class="meta">Còn {lt["con_lai"]} file nữa không hiện, để lộ trình gọn trong 5 bước.</p>')
    if lt.get("khong_dung"):
        ds = "".join(f"<li><code>{e(f)}</code></li>" for f in lt["khong_dung"])
        out.append(f'<div class="khung"><h3>⛔ Đừng đụng</h3><p class="meta">File khung của đề, '
                   f'sửa là hỏng test hoặc bị trừ điểm.</p><ul>{ds}</ul></div>')
    out.append('<div class="cho-trong"><div>🔥 Bao nhiêu bạn kẹt ở CP này: chưa nối (feature 2)</div>'
               '<div>💬 Giải thích lại cho mình nghe: chưa nối (feature 3)</div></div></section>')
    return "".join(out)


def _link_bao_sai(issue_url: str, lab: str, cp: str, b: dict) -> str:
    """Link tạo issue GitHub điền sẵn lab, CP, file, hàm, mã slide của 1 bước."""
    title = f"[F1 báo sai] {lab} {cp}: {b['file']}"
    body = (f"Lab: {lab}\nCP: {cp}\nFile: {b['file']} ({b['nhan']})\nHàm: {', '.join(b['ham'])}\n"
            f"Slide: {', '.join(b['slide']) or 'khong_co_can_cu'}\n\nSai ở đâu (nhãn / hàm / slide), đúng ra là gì:\n")
    return issue_url + "?" + urllib.parse.urlencode({"title": title, "body": body})


CP_RONG = ("Chưa nối được khái niệm nào của CP này với hàm Python. "
           "CP có thể làm trên file khác (.md, .docx…) hoặc chưa có slide tương ứng — xem đề của CP.")
CAU_HOI_CP = "Lab {lab}, {cp}. Khái niệm trong bài giảng của CP này nằm ở file nào, hàm nào?"


def chay_lab(lab: str, answer=None, tim_repo=None) -> list:
    """Chạy lõi cho mọi CP của 1 lab, trả các mục để đưa vào ve_html().

    Danh sách CP lấy từ chính output của lõi: hỏi "Lab DayNN" không kèm CP → lõi trả
    can_hoi_lai "Lab này có: CP1, CP2…". Lab không chia CP → 1 mục cho cả repo.

    Args:
        lab: Mã lab, vd "Day13".
        answer: Hàm answer(text) của lõi (mặc định agent.answer; test truyền hàm giả).
        tim_repo: Công cụ tim_repo của lõi, để đọc code vẽ sơ đồ (mặc định tools.tim_repo).

    Returns:
        List {"cp", "lt", "mermaid", "chu_thich"}, theo thứ tự CP.
    """
    import json
    import re

    if answer is None or tim_repo is None:
        from agent import answer as _answer
        from tools import tim_repo as _tim_repo
        answer, tim_repo = answer or _answer, tim_repo or _tim_repo
    repo = tim_repo(lab, "")
    dau = json.loads(answer(f"Lab {lab}. Lab này có những CP nào?")["output"])
    if "tu_choi" in dau:
        return [{"cp": lab, "lt": lo_trinh(dau), "mermaid": "", "chu_thich": ""}]
    cps = list(dict.fromkeys(re.findall(r"\bCP\d+\b", dau.get("can_hoi_lai") or "")))
    muc = []
    for cp in cps or [""]:
        out = dau if not cps else json.loads(answer(CAU_HOI_CP.format(lab=lab, cp=cp))["output"])
        lt = lo_trinh(out)
        if not lt["buoc"] and "tu_choi" not in out:
            lt["loi_nhan"] = CP_RONG
        muc.append({"cp": cp or lab, "lt": lt, **(so_do(repo, lt) if repo and lt["buoc"] else
                                                  {"mermaid": "", "chu_thich": ""})})
    return muc


def main(argv: list) -> int:
    """CLI: python codebase/f1_lo_trinh.py Day13 [--out data/f1/Day13.html]. Nên bật CACHE=1 cho đỡ tốn token."""
    import sys

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if not argv or argv[0].startswith("-"):
        print(main.__doc__)
        return 1
    lab = argv[0]
    out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "f1", f"{lab}.html")
    muc = chay_lab(lab)
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(ve_html(lab, muc))
    co = sum(1 for m in muc if m["lt"]["buoc"])
    print(f"Đã ghi {out} · {co}/{len(muc)} CP có lộ trình")
    return 0


if __name__ == "__main__":
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(main(sys.argv[1:]))
