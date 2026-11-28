"""Feature 3 — phiên Feynman: agent đóng vai người mới hỏi, học viên giải thích lại.

Chỉ đọc output của lõi (answer(text)["output"], format ở đầu eval/metric_spec.yaml). Không gọi hàm bên trong
lõi, không sửa agent.py / tools.py / ai.py. Gọi model qua ai.call_model.

Mỗi khái niệm trong bản đồ của lõi được hỏi theo 3 mức:
    M1 giải thích bằng lời thường  → AI chấm, CHỈ đối chiếu đoạn slide (mã slide lấy từ output lõi)
    M2 chỉ ra file:hàm             → code chấm: câu trả lời có nhắc hàm của khái niệm trong output lõi không
    M3 đoán khi đổi điều kiện     → code chấm: chọn A/B/C; đáp án là kịch bản đã chạy sẵn trong
                                      data/knowledge/<DayNN>/kich_ban.json (số trên slide), KHÔNG chạy code lab
Chưa đạt → trỏ lại đúng mã slide + file:hàm. Khái niệm không có slide (khong_co_can_cu) thì bỏ M1, nói rõ lý do.
Tự nguyện: kết quả chỉ in cho học viên, không ghi file, không gửi đi đâu.

Chạy:
    python codebase/feynman.py "Lab Day13, CP1. Công thức chi phí trong bài giảng được viết thành những hàm nào?"
    python codebase/feynman.py --ban-do output.json      (dùng output lõi đã lưu thành file JSON)
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ai import call_model

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KHONG_CO = "khong_co_can_cu"
TU_TOI_THIEU = 4  # câu giải thích ngắn hơn số từ này thì không đạt, không tốn lượt gọi model
BO_QUA = {"bo qua", "bỏ qua", "skip"}

SYSTEM_M1 = """Bạn là người mới học, đang nghe một học viên giải thích lại một khái niệm (phương pháp Feynman).
Chấm câu giải thích CHỈ dựa trên đoạn slide được đưa vào. Không dùng kiến thức ngoài, không tự thêm ý.
Đoạn slide có thể nói về nhiều khái niệm: CHỈ chấm các ý của đúng khái niệm được hỏi, bỏ qua ý của khái niệm khác.
Học viên được yêu cầu nói bằng lời thường: KHÔNG đòi công thức, ký hiệu hay số chính xác; giải thích đúng bản chất
hoặc một ví dụ đúng là đủ. Đạt khi nói đúng bản chất của khái niệm đó bằng lời của mình và không sai ý nào.
Chỉ lặp lại tên khái niệm hoặc thuật ngữ mà không nói bản chất thì KHÔNG đạt.
Trả về đúng một JSON, không thêm chữ nào khác:
{"dat": true hoặc false, "y_dung": [chuỗi], "y_thieu": [chuỗi], "cau_hoi_tiep": chuỗi}
y_thieu: ý về bản chất của đúng khái niệm được hỏi mà học viên chưa nói hoặc nói sai (không liệt kê công thức).
cau_hoi_tiep: một câu hỏi ngắn của người mới, gợi học viên nghĩ tới ý còn thiếu, không nói ra đáp án ("" nếu đạt)."""


def _knowledge_dir() -> str:
    return os.environ.get("KNOWLEDGE_DIR") or os.path.join(ROOT, "data", "knowledge")


def _read(path: str) -> str:
    try:
        with open(path, encoding="utf-8-sig") as f:
            return f.read()
    except OSError:
        return ""


def doc_doan_slide(lab: str, ma: str) -> str:
    """Nội dung đoạn `## <ma>` trong data/knowledge/<lab>/slides.md; rỗng nếu không có."""
    if not lab or not ma or ma == KHONG_CO:
        return ""
    text = _read(os.path.join(_knowledge_dir(), lab, "slides.md"))
    m = re.search(rf"^##\s*{re.escape(ma)}\s*$(.*?)(?=^##\s|\Z)", text, re.MULTILINE | re.DOTALL | re.IGNORECASE)
    return m.group(1).strip() if m else ""


def doc_kich_ban(lab: str) -> list:
    """Kịch bản M3 đã chạy sẵn của lab (data/knowledge/<lab>/kich_ban.json); rỗng nếu chưa có."""
    try:
        data = json.loads(_read(os.path.join(_knowledge_dir(), lab, "kich_ban.json")) or "[]")
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def tao_cau_hoi(ban_do: dict) -> list:
    """Bản đồ của lõi → danh sách câu hỏi theo khái niệm, mức M1 → M2 → M3. Bỏ khái niệm không có hàm."""
    if not isinstance(ban_do, dict) or ban_do.get("tu_choi") or not ban_do.get("khai_niem"):
        return []
    lab = ban_do.get("lab") or ""
    kich_ban = doc_kich_ban(lab)
    da_hoi = set()
    cau = []
    for k in ban_do["khai_niem"]:
        ten = str(k.get("ten") or "").strip()
        code = [c for c in k.get("code") or [] if c.get("ham") and c.get("nhan") in ("sua", "doc")]
        if not ten or not code:
            continue
        ma = k.get("slide") or KHONG_CO
        chung = {"khai_niem": ten, "slide": ma, "code": code}
        slide = doc_doan_slide(lab, ma)
        if slide:
            cau.append({**chung, "muc": 1, "slide_text": slide,
                        "hoi": f'Mình mới học, chưa biết gì. "{ten}" là gì vậy? '
                               "Bạn giải thích bằng lời thường, đừng dùng thuật ngữ nhé."})
        else:
            cau.append({**chung, "muc": 1, "bo_qua": "Không có đoạn slide để đối chiếu nên không chấm phần giải thích."})
        cau.append({**chung, "muc": 2, "hoi": f'"{ten}" nằm ở file nào, hàm nào trong lab? Vì sao lại là hàm đó?'})
        for kb in kich_ban:
            if ma != KHONG_CO and kb.get("slide") == ma and kb.get("id") not in da_hoi:
                da_hoi.add(kb.get("id"))
                lua_chon = "\n".join(f"  {chu}. {nd}" for chu, nd in sorted(kb["lua_chon"].items()))
                cau.append({**chung, "muc": 3, "hoi": f"Đoán trước nhé: {kb['hoi']}\n{lua_chon}\n(Trả lời A, B hoặc C)",
                            "dung": kb["dung"], "giai_thich": kb["giai_thich"]})
    return cau


def _tro_lai(cau: dict) -> list:
    """Chỗ cần xem lại: mã slide (nếu có) + file:hàm của khái niệm, lấy từ output lõi."""
    out = [f"slide {cau['slide']}"] if cau.get("slide") and cau["slide"] != KHONG_CO else []
    return out + [f"{c['file']}:{c['ham']}" for c in cau.get("code", [])]


def _parse_json(text: str):
    m = re.search(r"\{.*\}", text or "", re.DOTALL)
    if not m:
        return None
    try:
        data = json.loads(m.group(0))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def cham_m1(tra_loi: str, cau: dict) -> dict:
    """M1: AI chấm câu giải thích, chỉ đối chiếu đoạn slide. dat = None khi không chấm được."""
    if len(tra_loi.split()) < TU_TOI_THIEU:
        return {"dat": False, "nhan_xet": "Câu trả lời quá ngắn, mình chưa hiểu được. Bạn nói kỹ hơn nhé.",
                "cau_hoi_tiep": "", "tro_lai": _tro_lai(cau)}
    user = "Khái niệm: {}\n\nĐoạn slide (nguồn duy nhất):\n{}\n\nCâu giải thích của học viên:\n{}".format(
        cau["khai_niem"], cau["slide_text"], tra_loi)
    data = _parse_json(call_model(SYSTEM_M1, user)["text"])
    if data is None or not isinstance(data.get("dat"), bool):
        return {"dat": None, "nhan_xet": "Chưa chấm được câu này (AI không trả kết quả đúng dạng).",
                "cau_hoi_tiep": "", "tro_lai": _tro_lai(cau)}
    thieu = [str(y) for y in data.get("y_thieu") or []]
    if data["dat"]:
        return {"dat": True, "nhan_xet": "Mình hiểu rồi, cảm ơn bạn!", "cau_hoi_tiep": "", "tro_lai": []}
    return {"dat": False, "nhan_xet": "Còn thiếu: " + "; ".join(thieu) if thieu else "Chưa đúng ý slide.",
            "cau_hoi_tiep": str(data.get("cau_hoi_tiep") or ""), "tro_lai": _tro_lai(cau)}


def cham_m2(tra_loi: str, cau: dict) -> dict:
    """M2: code chấm — câu trả lời phải nhắc ít nhất 1 hàm của khái niệm trong output lõi."""
    trung = [f"{c['file']}:{c['ham']}" for c in cau["code"]
             if re.search(rf"\b{re.escape(c['ham'])}\b", tra_loi, re.IGNORECASE)]
    if trung:
        return {"dat": True, "nhan_xet": "Đúng chỗ: " + ", ".join(trung), "tro_lai": []}
    return {"dat": False, "nhan_xet": "Chưa nhắc đúng hàm của khái niệm này.", "tro_lai": _tro_lai(cau)}


def cham_m3(tra_loi: str, cau: dict) -> dict:
    """M3: code chấm lựa chọn A/B/C với đáp án đã chạy sẵn. dat = None khi chưa chọn."""
    m = re.match(r"\s*([abcABC])\b", tra_loi) or re.search(r"\b([ABC])\b", tra_loi)
    if not m:
        return {"dat": None, "nhan_xet": "Bạn chưa chọn A, B hoặc C.", "tro_lai": []}
    if m.group(1).upper() == cau["dung"]:
        return {"dat": True, "nhan_xet": "Đoán đúng! " + cau["giai_thich"], "tro_lai": []}
    return {"dat": False, "nhan_xet": f"Chưa đúng, đáp án là {cau['dung']}. " + cau["giai_thich"],
            "tro_lai": _tro_lai(cau)}


CHAM = {1: cham_m1, 2: cham_m2, 3: cham_m3}
DAU = {True: "✓", False: "✗", None: "–"}


def tong_ket(ket_qua: list) -> str:
    """Một dòng mỗi khái niệm: mức đạt / chưa đạt + chỗ cần xem lại."""
    theo_kn = {}
    for r in ket_qua:
        theo_kn.setdefault(r["khai_niem"], []).append(r)
    dong = ["", "Tổng kết (chỉ hiện ở đây, không lưu):"]
    for ten, rs in theo_kn.items():
        muc = " · ".join(f"M{r['muc']} {DAU[r['dat']]}" for r in rs)
        xem = sorted({x for r in rs if r["dat"] is False for x in r["tro_lai"]})
        dong.append(f"- {ten}: {muc}" + (f"  → xem lại: {', '.join(xem)}" if xem else ""))
    return "\n".join(dong)


def phien(ban_do: dict, hoi=input, in_ra=print) -> list:
    """Chạy một phiên hỏi đáp. Enter trống = dừng, "bỏ qua" = bỏ câu. Trả kết quả (chỉ trong bộ nhớ)."""
    cau_hoi = tao_cau_hoi(ban_do)
    if not cau_hoi:
        in_ra("Bản đồ chưa có khái niệm nào gắn với hàm, chưa có gì để hỏi.")
        return []
    in_ra("Phiên Feynman (tự nguyện): mình là người mới, bạn giải thích cho mình nhé. "
          "Kết quả chỉ hiện ở đây, không lưu. Gõ 'bỏ qua' để bỏ câu, Enter trống để dừng.")
    ket_qua = []
    for cau in cau_hoi:
        if cau.get("bo_qua"):
            ket_qua.append({"muc": cau["muc"], "khai_niem": cau["khai_niem"], "dat": None,
                            "nhan_xet": cau["bo_qua"], "tro_lai": []})
            continue
        in_ra(f"\n[M{cau['muc']} · {cau['khai_niem']}] {cau['hoi']}")
        tra_loi = hoi("> ").strip()
        if not tra_loi:
            break
        if tra_loi.lower() in BO_QUA:
            kq = {"dat": None, "nhan_xet": "Đã bỏ qua.", "tro_lai": []}
        else:
            kq = CHAM[cau["muc"]](tra_loi, cau)
            if cau["muc"] == 1 and kq["dat"] is False and kq.get("cau_hoi_tiep"):
                in_ra(f"{kq['nhan_xet']}\nNgười mới hỏi tiếp: {kq['cau_hoi_tiep']}")
                them = hoi("> ").strip()
                if them:
                    kq = cham_m1(tra_loi + " " + them, cau)
        in_ra(kq["nhan_xet"] + (f"\nXem lại: {', '.join(kq['tro_lai'])}" if kq["tro_lai"] else ""))
        ket_qua.append({"muc": cau["muc"], "khai_niem": cau["khai_niem"], "dat": kq["dat"],
                        "nhan_xet": kq["nhan_xet"], "tro_lai": kq["tro_lai"]})
    in_ra(tong_ket(ket_qua))
    return ket_qua


def main(argv: list) -> int:
    for stream in (sys.stdout, sys.stdin):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) == 2 and argv[0] == "--ban-do":
        ban_do = json.loads(_read(argv[1]) or "{}")
    elif argv:
        from agent import answer
        ban_do = json.loads(answer(" ".join(argv))["output"])
    else:
        print(__doc__)
        return 1
    if ban_do.get("tu_choi"):
        print(ban_do["tu_choi"])
        return 0
    if ban_do.get("can_hoi_lai") and not ban_do.get("khai_niem"):
        print(ban_do["can_hoi_lai"])
        return 0
    phien(ban_do)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
