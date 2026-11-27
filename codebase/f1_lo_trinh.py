"""Feature 1: lộ trình đọc file theo CP, dựng từ output của lõi (không gọi AI, không đọc repo).

Hợp đồng: chỉ đọc output JSON của agent.answer() (format ở đầu eval/metric_spec.yaml),
không gọi vào hàm nội bộ của lõi.
"""

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