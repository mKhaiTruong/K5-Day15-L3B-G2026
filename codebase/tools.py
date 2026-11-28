"""Công cụ của lõi: đọc repo lab + gói kiến thức (slide), khớp spec.md §4.

Mỗi công cụ là một hàm có @tool; docstring ghi: tên · input · output · có tác động ra ngoài không.
Chỉ dùng thư viện chuẩn. Không công cụ nào ghi vào repo lab của học viên.

Dữ liệu đọc:
    LABS_DIR      thư mục chứa các repo lab (mặc định data/labs). Mỗi lab tìm theo tên có "DayNN".
    KNOWLEDGE_DIR gói kiến thức (mặc định data/knowledge): <DayNN>/slides.md, mỗi đoạn bắt đầu
                  bằng dòng "## DayNN-s<trang>" (vd "## Day14-s12"). Không commit nguyên slide.
"""
import ast
import json
import os
import re

from tracing import TOOLS, tool  # noqa: F401

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache"}
KHUNG_PATTERN = re.compile(r"không\s+(được\s+)?sửa|khong\s+sua|do\s+not\s+(edit|modify)|đừng\s+sửa", re.IGNORECASE)
FILE_TOKEN = re.compile(r"[\w./-]+\.(?:py|md|csv|yaml|yml|json|toml|txt|sh)\b")


def _labs_dir() -> str:
    return os.environ.get("LABS_DIR") or os.path.join(ROOT, "data", "labs")


def _knowledge_dir() -> str:
    return os.environ.get("KNOWLEDGE_DIR") or os.path.join(ROOT, "data", "knowledge")


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _walk_files(repo: str, max_depth: int = 4):
    """Yield đường dẫn tương đối (dùng /) của mọi file trong repo, bỏ thư mục rác."""
    base_depth = repo.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, filenames in os.walk(repo):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if dirpath.count(os.sep) - base_depth >= max_depth:
            dirnames[:] = []
        for name in filenames:
            yield os.path.relpath(os.path.join(dirpath, name), repo).replace(os.sep, "/")


def _candidate_dirs(base: str, depth: int = 2) -> list:
    """Liệt kê thư mục con tới độ sâu `depth` dưới base."""
    out = []
    base_depth = base.rstrip(os.sep).count(os.sep)
    for dirpath, dirnames, _ in os.walk(base):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        if dirpath.count(os.sep) - base_depth >= depth - 1:
            out.extend(os.path.join(dirpath, d) for d in dirnames)
            dirnames[:] = []
        else:
            out.extend(os.path.join(dirpath, d) for d in dirnames)
    return out


@tool
def tim_repo(lab: str = "", ten_repo: str = "") -> str:
    """Tìm thư mục repo theo mã lab ("Day14") hoặc tên repo.

    Input: lab (vd "Day14"), ten_repo (tên thư mục). Output: đường dẫn tuyệt đối, "" nếu không thấy.
    Không tác động ra ngoài.
    """
    base = _labs_dir()
    if not os.path.isdir(base):
        return ""
    dirs = _candidate_dirs(base)
    if ten_repo:
        hits = [d for d in dirs if os.path.basename(d).lower() == ten_repo.lower()]
        hits.sort(key=len, reverse=True)  # thư mục lồng (repo/repo) thường là repo thật
        if hits:
            return hits[0]
    if lab:
        num = re.sub(r"\D", "", lab)
        pat = re.compile(rf"day[\s_-]?0?{num}(?!\d)", re.IGNORECASE)
        hits = [d for d in dirs if pat.search(os.path.basename(d))]
        # ưu tiên thư mục trông giống repo lab (có CHECKPOINTS / README)
        hits.sort(key=lambda d: (not os.path.exists(os.path.join(d, "CHECKPOINTS.md")),
                                 not os.path.exists(os.path.join(d, "README.md")), len(d)))
        if hits:
            return hits[0]
    return ""


@tool
def doc_cau_truc_lab(repo: str) -> dict:
    """Đọc cấu trúc repo và xác định có phải repo lab không.

    Input: đường dẫn repo. Output: {"la_lab": bool, "ly_do": str, "files": [...], "cps": ["CP0", ...]}.
    Repo lab = có README + (CHECKPOINTS.md hoặc README nhắc checkpoint/CPn) + (RUBRIC.md hoặc có test/script chấm).
    Không tác động ra ngoài.
    """
    if not repo or not os.path.isdir(repo):
        return {"la_lab": False, "ly_do": "không tìm thấy repo", "files": [], "cps": []}
    files = list(_walk_files(repo))
    readme = _read(os.path.join(repo, "README.md"))
    checkpoints = _read(os.path.join(repo, "CHECKPOINTS.md"))
    cps = sorted(set(re.findall(r"\bCP\s?(\d+)\b", checkpoints or readme)), key=int)
    has_cp = bool(cps) or "checkpoint" in readme.lower()
    has_rubric = any(f.lower().endswith("rubric.md") for f in files) or any(
        re.search(r"(^|/)tests?/|(^|/)test_[^/]*\.py$|(^|/)check[^/]*\.py$", f) for f in files)
    la_lab = bool(readme) and has_cp and has_rubric
    if not readme:
        ly_do = "không có README"
    elif not has_cp:
        ly_do = "README không có checkpoint / CP"
    elif not has_rubric:
        ly_do = "không có rubric hay test"
    else:
        ly_do = "có README, checkpoint, rubric/test"
    return {"la_lab": la_lab, "ly_do": ly_do, "files": files[:300], "cps": [f"CP{c}" for c in cps]}


@tool
def doc_cp(repo: str, cp: str) -> dict:
    """Đọc mô tả một CP và các file / hàm Python thuộc phần việc của CP đó.

    Input: repo, mã CP ("CP5"; rỗng = lab không chia CP).
    Output: {"mo_ta": str, "ham": [{"file", "ham", "dong"}], "todo": [{"file", "dong", "text"}]};
    mo_ta rỗng nếu không có CP đó. todo = dòng TODO của CP này trong các file đó (để biết hàm nào học viên phải viết).
    Hàm lấy từ file .py được nhắc trong đoạn CP, hoặc nằm trong thư mục được nhắc. Với thư mục, nếu README
    của thư mục ghi "TODO" cạnh tên file thì chỉ lấy các file đó (bỏ app phụ trùng tên ở thư mục con khác).
    Lab không chia CP: mô tả = README, hàm = mọi file .py của repo.
    Không tác động ra ngoài.
    """
    if not cp:
        files = [f for f in _walk_files(repo, 3) if f.endswith(".py")]
        return {"mo_ta": _read(os.path.join(repo, "README.md"))[:3000], "ham": _list_functions(repo, files),
                "todo": _todo_lines(repo, files, "")}
    text = _read(os.path.join(repo, "CHECKPOINTS.md")) or _read(os.path.join(repo, "README.md"))
    num = re.sub(r"\D", "", cp)
    m = re.search(rf"^#+[^\n]*\bCP\s?{num}\b.*?(?=^#+[^\n]*\bCP\s?\d+\b|\Z)", text, re.MULTILINE | re.DOTALL)
    mo_ta = m.group(0).strip() if m else ""
    refs = {a or b for a, b in re.findall(r"`([^`]+)`|\]\(([^)\s]+)\)", mo_ta)}
    py_files = []
    for ref in refs:
        ref = ref.strip().rstrip("/")
        path = os.path.join(repo, ref)
        if ref.lower().endswith("readme.md") and os.path.isfile(path):
            ref = os.path.dirname(ref)
            path = os.path.join(repo, ref)
            if not ref:
                continue
        if os.path.isdir(path):
            py_files += _files_in_scope(repo, ref)
        elif ref.endswith(".py") and os.path.isfile(path):
            py_files.append(ref)
    todo = _todo_lines(repo, py_files, cp)
    return {"mo_ta": mo_ta[:3000], "ham": _loc_ham_theo_todo(repo, _list_functions(repo, py_files), todo, cp),
            "todo": todo}


SO_HAM = re.compile(r"\b(\d+|một|hai|ba|bốn|năm|sáu)\s+hàm", re.IGNORECASE)
SO_CHU = {"một": 1, "hai": 2, "ba": 3, "bốn": 4, "năm": 5, "sáu": 6}


def _loc_ham_theo_todo(repo: str, ham: list, todo: list, cp: str) -> list:
    """Giữ hàm mà TODO của đúng CP chỉ tới, để 1 file chứa nhiều CP không đưa model hàm của CP khác.

    Hàm được giữ khi: chứa dòng TODO của CP · được TODO nhắc tên · hoặc là N hàm ngay sau một dòng TODO
    ở cấp module ("viết ba hàm dưới đây" → 3 hàm; không ghi số → 1 hàm). Chỉ xét dòng comment `# TODO` ghi đúng CP;
    không có TODO nào như vậy, hoặc lọc ra rỗng → trả nguyên danh sách (giữ cách cũ).

    Args:
        repo: Đường dẫn repo lab.
        ham: Kết quả _list_functions: [{"file", "ham", "dong"}].
        todo: Kết quả _todo_lines của CP.
        cp: Mã CP, vd "CP1".

    Returns:
        Danh sách con của `ham`, giữ thứ tự cũ.
    """
    num = re.sub(r"\D", "", cp)
    if not num:
        return ham
    this_cp = re.compile(rf"\bCP\s?{num}(?!\d)", re.IGNORECASE)
    # chỉ dòng comment: docstring kiểu "đánh dấu TODO CP1…CP4" không chỉ tới hàm nào
    todo = [t for t in todo if t["text"].startswith("#") and this_cp.search(t["text"])]
    if not todo:
        return ham
    giu = set()
    for rel in {t["file"] for t in todo}:
        try:
            tree = ast.parse(_read(os.path.join(repo, rel)))
        except SyntaxError:
            continue
        defs = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        for t in (t for t in todo if t["file"] == rel):
            ben_trong = [d for d in defs if d.lineno <= t["dong"] <= (d.end_lineno or d.lineno)]
            giu |= {(rel, d.name) for d in ben_trong}
            giu |= {(rel, d.name) for d in defs if re.search(rf"\b{re.escape(d.name)}\b", t["text"])}
            if not ben_trong:  # TODO ở cấp module → lấy N hàm ngay sau nó
                m = SO_HAM.search(t["text"])
                n = (int(m.group(1)) if m.group(1).isdigit() else SO_CHU[m.group(1).lower()]) if m else 1
                giu |= {(rel, d.name) for d in [d for d in defs if d.lineno > t["dong"]][:n]}
    loc = [h for h in ham if (h["file"], h["ham"]) in giu or h["file"] not in {t["file"] for t in todo}]
    return loc or ham


def _files_in_scope(repo: str, folder: str) -> list:
    """File .py thuộc phần việc trong `folder`: ưu tiên file README của folder ghi TODO, không có thì lấy hết."""
    all_py = [folder + "/" + f for f in _walk_files(os.path.join(repo, folder), 3) if f.endswith(".py")]
    readme = _read(os.path.join(repo, folder, "README.md"))
    todo_names = {os.path.basename(t) for line in readme.splitlines() if "TODO" in line
                  for t in FILE_TOKEN.findall(line) if t.endswith(".py")}
    picked = []
    for name in todo_names:
        same = sorted((f for f in all_py if os.path.basename(f) == name), key=lambda f: f.count("/"))
        if same:
            picked.append(same[0])  # trùng tên thì lấy file nông nhất (app chính, không phải app phụ)
    return picked or all_py


def _list_functions(repo: str, py_files: list) -> list:
    """Liệt kê hàm public cấp module trong các file .py (đọc bằng ast)."""
    ham = []
    for rel in sorted(set(py_files)):
        try:
            tree = ast.parse(_read(os.path.join(repo, rel)))
        except SyntaxError:
            continue
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
                ham.append({"file": rel, "ham": node.name, "dong": node.lineno})
    return ham[:200]


def _todo_lines(repo: str, py_files: list, cp: str) -> list:
    """Lấy các dòng TODO của CP trong file .py (vd "# TODO CP1: viết ba hàm dưới đây").

    Lấy dòng ghi đúng CP đó, hoặc TODO không ghi CP nào. cp rỗng = lấy mọi TODO.
    """
    num = re.sub(r"\D", "", cp)
    other_cp = re.compile(r"\bCP\s?\d+", re.IGNORECASE)
    this_cp = re.compile(rf"\bCP\s?{num}(?!\d)", re.IGNORECASE) if num else None
    out = []
    for rel in sorted(set(py_files)):
        for i, line in enumerate(_read(os.path.join(repo, rel)).splitlines(), 1):
            if "TODO" not in line:
                continue
            if this_cp and other_cp.search(line) and not this_cp.search(line):
                continue
            out.append({"file": rel, "dong": i, "text": line.strip()[:200]})
    return out[:40]


@tool
def tim_file_khung(repo: str) -> list:
    """Liệt kê file khung không được sửa, đọc từ các dòng ghi "không sửa" trong file .md của repo.

    Bỏ qua file .md trong thư mục ẩn (.study/, .claude/, .github/…): đó là ghi chú của học viên / công cụ,
    không phải luật của đề, mà repo học viên đã làm thường có (vd ".study/plans/...: không sửa file lab").
    Input: repo. Output: danh sách đường dẫn tương đối (dùng /). Không tác động ra ngoài.
    """
    out = set()
    for rel in _walk_files(repo):
        if not rel.lower().endswith(".md"):
            continue
        if any(part.startswith(".") for part in rel.split("/")[:-1]):
            continue
        folder = os.path.dirname(rel)
        for line in _read(os.path.join(repo, rel)).splitlines():
            # chỉ lấy file nằm cùng mệnh đề với "không sửa" (tách theo ". " và ";"),
            # để "File được sửa: `a.py`. Không sửa file CSV." không coi a.py là file khung
            clauses = [c for c in re.split(r"\.\s+|;", line) if KHUNG_PATTERN.search(c)]
            for token in (t for c in clauses for t in FILE_TOKEN.findall(c)):
                token = token.lstrip("./")
                for cand in ((folder + "/" + token) if folder else token, token):
                    if os.path.isfile(os.path.join(repo, cand)):
                        out.add(cand)
                        break
    return sorted(out)


@tool
def tim_slide(lab: str, khai_niem: str) -> list:
    """Tìm đoạn slide trong gói kiến thức của lab có nhắc tới khái niệm.

    Input: lab ("Day14"), khái niệm (chuỗi). Output: [{"ma": "Day14-s12", "text": ...}], rỗng nếu chưa có slide.
    Không tác động ra ngoài.
    """
    text = _read(os.path.join(_knowledge_dir(), lab, "slides.md"))
    if not text:
        return []
    words = [w for w in re.findall(r"\w+", khai_niem.lower()) if len(w) > 2]
    out = []
    pattern = rf"^##\s*({re.escape(lab)}-s\d+)\s*$(.*?)(?=^##\s|\Z)"
    for m in re.finditer(pattern, text, re.MULTILINE | re.DOTALL | re.IGNORECASE):
        body = m.group(2).strip()
        if words and any(w in body.lower() for w in words):
            out.append({"ma": m.group(1), "text": body[:600]})
    return out[:5]


@tool
def ma_slide_ton_tai(lab: str, ma: str) -> bool:
    """Kiểm tra mã đoạn slide có thật trong gói kiến thức không.

    Input: lab, mã đoạn ("Day14-s12"). Output: True / False. Không tác động ra ngoài.
    """
    text = _read(os.path.join(_knowledge_dir(), lab, "slides.md"))
    return bool(ma) and re.search(rf"^##\s*{re.escape(ma)}\s*$", text, re.MULTILINE | re.IGNORECASE) is not None


@tool
def kiem_ham_ton_tai(repo: str, file: str, ham: str) -> bool:
    """Kiểm tra hàm có thật trong file của repo không (đọc bằng ast, không chạy code).

    Input: repo, file (tương đối), tên hàm. Output: True / False. Không tác động ra ngoài.
    """
    path = os.path.join(repo, file)
    if not os.path.isfile(path):
        return False
    if not file.endswith(".py"):
        return not ham
    try:
        tree = ast.parse(_read(path))
    except SyntaxError:
        return False
    return any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.name == ham
               for n in ast.walk(tree))


@tool
def ghi_cau_hoi_an_danh(lab: str, cp: str, khai_niem: list) -> str:
    """Ghi một dòng thống kê ẩn danh cho heatmap (không lưu mã học viên hay nguyên câu hỏi).

    Input: lab, cp, danh sách tên khái niệm. Output: "da_ghi" hoặc "bo_qua" (khi HEATMAP_LOG khác 1).
    Tác động ra ngoài: CÓ, ghi thêm 1 dòng vào data/heatmap/cau_hoi.jsonl. Mặc định tắt.
    """
    if os.environ.get("HEATMAP_LOG") != "1":
        return "bo_qua"
    folder = os.path.join(ROOT, "data", "heatmap")
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, "cau_hoi.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"lab": lab, "cp": cp, "khai_niem": khai_niem}, ensure_ascii=False) + "\n")
    return "da_ghi"
