"""Feature 1: lộ trình đọc file theo CP + sơ đồ flow, dựng từ output của lõi (không gọi AI).

Hợp đồng: chỉ đọc output JSON của agent.answer() (format ở đầu eval/metric_spec.yaml),
không gọi vào hàm nội bộ của lõi. Phần sơ đồ đọc dòng import của các file trong lộ trình
bằng ast (không chạy code lab).

    lo_trinh(output)            → ≤5 bước đọc file
    do_thi_import(repo, files)  → mũi tên "file A import file B" giữa các file đó
    ve_mermaid(lt, canh)        → sơ đồ Mermaid (text)
"""
import ast
import os

MAX_BUOC = 5


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
    lines += ["    classDef doc fill:#e8f1fb,stroke:#6a9fd4,color:#1f3b57",
              "    classDef sua fill:#e7f5ea,stroke:#5fae6e,color:#1e4227",
              "    classDef khung fill:#fbeaea,stroke:#d98c8c,color:#5a2323"]
    return "\n".join(lines)


def _esc(text: str) -> str:
    """Thoát ký tự làm vỡ nhãn Mermaid (ngoặc kép, <, >)."""
    return str(text).replace("&", "&amp;").replace('"', "#quot;").replace("<", "&lt;").replace(">", "&gt;")

