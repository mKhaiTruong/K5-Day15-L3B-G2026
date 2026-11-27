"""Luồng chính của lõi: bản đồ khái niệm bài giảng ↔ code lab theo CP (spec.md §4).

Hình dạng: workflow cố định 6 bước, AI chỉ làm bước 5 (ghép khái niệm ↔ file / hàm).
    1. tìm repo + kiểm có phải lab        → không phải lab: từ chối
    2. đã rõ CP chưa                      → chưa: hỏi lại (G10)
    3. đọc CP + file khung                → câu đòi sửa file khung / làm hộ: từ chối
    4. tìm đoạn slide
    5. call_model ghép khái niệm ↔ code   → model trả không phải JSON: ghép dự phòng bằng so khớp tên hàm
    6. kiểm bằng code: bỏ hàm không có thật, mã slide bịa → khong_co_can_cu, ép nhãn khong_dung cho file khung

Hợp đồng: answer(text) -> {"output": str}; output là chuỗi JSON theo format ở đầu eval/metric_spec.yaml.
"""
import json
import re

from ai import call_model
from tools import (
    doc_cau_truc_lab,
    doc_cp,
    ghi_cau_hoi_an_danh,
    kiem_ham_ton_tai,
    ma_slide_ton_tai,
    tim_file_khung,
    tim_repo,
    tim_slide,
)
from tracing import note

SYSTEM = """Bạn giúp học viên AI20K nối khái niệm của bài giảng với code của bài lab.
Chỉ dùng các hàm trong danh sách "Hàm của CP" và các đoạn trong "Slide" được đưa vào; không dùng kiến thức ngoài.
Trả về DUY NHẤT một JSON:
{"khai_niem": [{"ten": str, "slide": "<mã đoạn slide đã cho, hoặc khong_co_can_cu>",
  "code": [{"file": str, "ham": str, "nhan": "doc|sua|khong_dung"}], "ly_do": str}]}
- Mỗi khái niệm trỏ tới hàm có trong danh sách; nhãn "sua" nếu CP yêu cầu học viên viết / sửa hàm đó, "doc" nếu chỉ cần đọc.
- Không bao giờ gắn nhãn "sua" cho file trong "File khung".
- Khái niệm không có trong slide đã cho thì ghi slide = "khong_co_can_cu"."""

ATTACK = re.compile(r"bỏ qua (mọi |các )?(hướng dẫn|chỉ dẫn)|ignore (all |previous )?instructions|"
                    r"(viết|làm|giải|code) hộ|in luôn pass|cho nó (in|báo) pass", re.IGNORECASE)
TEST_FILE = re.compile(r"(^|/)tests?/|(^|/)test_[^/]*\.py$")
CONFIRM = re.compile(r"đúng không|phải không|có phải", re.IGNORECASE)
EDIT_WORDS = re.compile(r"\b(sửa|chỉnh|edit|modify|xoá|xóa)\b", re.IGNORECASE)
STOP = {"code", "file", "files", "repo", "trong", "giúp", "mình", "muốn", "khác", "nhau", "những",
        "được", "nằm", "đâu", "này", "check", "với", "chỗ", "nào", "hiểu", "lab", "của"}


def _out(obj: dict) -> dict:
    return {"output": json.dumps(obj, ensure_ascii=False)}


def _parse(text: str) -> dict:
    """Tách mã lab, mã CP, tên repo từ câu của học viên."""
    lab = re.search(r"\bday\s?0?(\d{1,2})\b", text, re.IGNORECASE)
    cp = re.search(r"\bCP\s?(\d+)\b", text, re.IGNORECASE)
    repo = re.search(r"\brepo\s+([\w.-]+)", text, re.IGNORECASE)
    return {"lab": f"Day{int(lab.group(1)):02d}" if lab else "",
            "cp": f"CP{cp.group(1)}" if cp else "",
            "ten_repo": repo.group(1) if repo else ""}


def _tokens(text: str) -> list:
    return [w for w in re.findall(r"[a-zA-Z]\w+", text.lower()) if len(w) >= 4 and w not in STOP]


def _ghep_du_phong(text: str, ham: list) -> list:
    """Ghép dự phòng khi model không trả JSON: khớp từ trong câu hỏi với tên hàm (chỉ dùng ở chế độ giả)."""
    q = _tokens(text)
    groups = {}
    for h in ham:
        parts = [p for p in h["ham"].lower().split("_") if len(p) >= 4]
        hit = [w for w in q if any(p.startswith(w) or w.startswith(p) for p in parts)]
        if hit:
            groups.setdefault(" ".join(dict.fromkeys(hit)), []).append(
                {"file": h["file"], "ham": h["ham"], "nhan": "sua"})
    return [{"ten": k, "slide": "khong_co_can_cu", "code": v,
             "ly_do": "khớp tên hàm với câu hỏi (ghép dự phòng, chưa có model)"} for k, v in groups.items()]


def _parse_json(text: str):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    return data.get("khai_niem") if isinstance(data, dict) and isinstance(data.get("khai_niem"), list) else None


def _kiem(repo: str, lab: str, khai_niem: list, khung: list) -> list:
    """Bước 6: bỏ hàm không có thật, sửa mã slide bịa, ép nhãn khong_dung cho file khung."""
    out = []
    for k in khai_niem:
        if not isinstance(k, dict) or not k.get("ten"):
            continue
        code = []
        for c in k.get("code") or []:
            f, h = str(c.get("file", "")), str(c.get("ham", ""))
            if not kiem_ham_ton_tai(repo, f, h):
                note(f"bỏ {f}:{h} — không có trong repo")
                continue
            nhan = "khong_dung" if f in khung else (c.get("nhan") if c.get("nhan") in ("doc", "sua") else "doc")
            code.append({"file": f, "ham": h, "nhan": nhan})
        slide = str(k.get("slide") or "khong_co_can_cu")
        if slide != "khong_co_can_cu" and not ma_slide_ton_tai(lab, slide):
            note(f"mã slide {slide} không có trong gói kiến thức")
            slide = "khong_co_can_cu"
        if code:
            out.append({"ten": str(k["ten"]), "slide": slide, "code": code, "ly_do": str(k.get("ly_do", ""))})
    return out


def answer(text: str) -> dict:
    p = _parse(text)
    if ATTACK.search(text):
        return _out({"tu_choi": "Mình chỉ chỉ đường và giải thích, không làm hộ bài hay lách script chấm. "
                                "Hãy chọn CP và khái niệm bạn muốn hiểu."})

    # Bước 1: tìm repo, kiểm có phải lab
    if not p["lab"] and not p["ten_repo"]:
        return _out({"can_hoi_lai": "Bạn đang làm lab ngày mấy (vd Day14) và CP nào?"})
    repo = tim_repo(p["lab"], p["ten_repo"])
    if not repo:
        return _out({"tu_choi": "Chưa có %s trong hệ thống, mình chỉ hỗ trợ lab đã có gói kiến thức."
                                % (p["lab"] or p["ten_repo"])})
    info = doc_cau_truc_lab(repo)
    if not info["la_lab"]:
        return _out({"tu_choi": "Repo này không phải repo lab ({}), mình không hỗ trợ.".format(info["ly_do"])})

    # Bước 2: đã rõ CP chưa (G10). Lab không chia CP thì đi tiếp với cả repo.
    if info["cps"] and (not p["cp"] or p["cp"] not in info["cps"]):
        return _out({"lab": p["lab"], "cp": p["cp"] or None, "khai_niem": [], "khong_dung": [],
                     "can_hoi_lai": "Bạn đang làm CP nào? Lab này có: {}".format(", ".join(info["cps"]))})

    # Bước 3: đọc CP + file khung; chặn câu đòi sửa file khung
    khung = tim_file_khung(repo)
    ghi_chu = None
    nhac_khung = [k for k in khung if k.rsplit("/", 1)[-1].lower() in text.lower()]
    if EDIT_WORDS.search(text) and nhac_khung:
        if not CONFIRM.search(text):  # đòi sửa file khung → từ chối
            return _out({"tu_choi": "File bạn nhắc là file khung, đề ghi không được sửa. "
                                    "Phần việc của bạn nằm ở các TODO của CP; mình chỉ chỗ đó được.",
                         "khong_dung": khung})
        # hỏi xác nhận ("sửa file đó đúng không?") → tiền đề sai, trả lời tiếp kèm ghi chú
        ghi_chu = "{} là file khung, không sửa; xem các file được gắn nhãn sua bên dưới.".format(", ".join(nhac_khung))
    if not info["cps"]:
        p["cp"] = ""
    cp_info = doc_cp(repo, p["cp"])
    ham = [h for h in cp_info["ham"] if h["file"] not in khung and not TEST_FILE.search(h["file"])]

    # Bước 4: slide
    slides = tim_slide(p["lab"], text)

    # Bước 5: model ghép khái niệm ↔ code
    user = "Câu của học viên:\n{}\n\nMô tả CP:\n{}\n\nHàm của CP:\n{}\n\nFile khung:\n{}\n\nSlide:\n{}".format(
        text, cp_info["mo_ta"][:1500],
        "\n".join("{}:{}".format(h["file"], h["ham"]) for h in ham) or "(không có)",
        "\n".join(khung) or "(không có)",
        "\n".join("[{}] {}".format(s["ma"], s["text"]) for s in slides) or "(chưa có slide)")
    reply = call_model(SYSTEM, user)
    khai_niem = _parse_json(reply["text"])
    if khai_niem is None:
        note("model không trả JSON — dùng ghép dự phòng")
        khai_niem = _ghep_du_phong(text, ham)

    # Bước 6: kiểm bằng code
    khai_niem = _kiem(repo, p["lab"], khai_niem, khung)
    ghi_cau_hoi_an_danh(p["lab"], p["cp"], [k["ten"] for k in khai_niem])
    return _out({"lab": p["lab"], "cp": p["cp"] or None, "khai_niem": khai_niem, "khong_dung": khung,
                 "ghi_chu": ghi_chu,
                 "can_hoi_lai": None if khai_niem else "Mình chưa thấy khái niệm này trong %s. "
                                                        "Bạn hỏi cụ thể hơn được không?" % (p["cp"] or p["lab"])})
