# AI SPEC — Trợ lý repo lab theo CP · Nhóm G2026 · Phòng C401 · Zone [X]

> Mốc nộp: §7 chốt chuẩn "đạt" tại **CP2 19:30 Thứ Sáu 27/11** · §0–§7 nộp **CP3 10:00 Thứ Bảy 28/11** · đủ §0–§10 **CP4 14:30 Thứ Bảy 28/11** · §10 changelog ghi tiếp đến **23:59 Thứ Bảy 28/11**.
> Đầu mỗi mục ghi bước guide (`02-guide.md` trong repo đề) chỉ cách điền. Mỗi mục ngắn, có số và nguồn; chi tiết để ở file được trỏ tới. Xoá dòng hướng dẫn trong ngoặc vuông khi điền xong.

Track: [x] A · [ ] B · [ ] C · [ ] D · [ ] E — bài toán: nhóm tự mở rộng — học viên hiểu và bắt đầu đúng một CP của repo lab. Lõi phân tích repo + CP, 3 feature: lộ trình file theo CP · heatmap chỗ lớp hay kẹt · phiên Feynman tự giải thích lại
Data BTC cấp đã dùng (nếu có — không commit nguyên file): chưa dùng (bằng chứng chính lấy từ phỏng vấn / khảo sát)

## §0. Hiện tại việc này diễn ra thế nào *(guide 1.1)*
- Luồng hiện tại (trong khoá AI20K, theo trải nghiệm của nhóm — chưa phải bằng chứng):
    1. Nhận link repo lab (README, checkpoint, rubric, test)
    2. Mentor giải thích nhiệm vụ của buổi
    3. Học viên đọc README, mở thử vài file, hoặc paste repo / đề vào ChatGPT / Claude Code để hỏi cần làm gì
    4. Sửa code cho tới khi test xanh, nộp
- Công cụ đang được dùng: ChatGPT, Claude Code / Cursor (hỏi đáp trên repo); DeepWiki (bóc repo thành trang wiki + hỏi đáp); hỏi bạn / mentor. Số người dùng mỗi công cụ: chưa kiểm.

## §1. Người dùng & bằng chứng *(guide 1.1, 1.2)*
- Người dùng chính (một vai cụ thể): học viên AI20K vừa nhận repo lab trong ngày, muốn làm đúng và hiểu bài. Không phục vụ người chỉ muốn vibe code cho qua.
- Việc họ cố làm xong: bắt đầu làm đúng một checkpoint của repo lab ngay trong buổi lab.
- Hôm nay họ giải bằng gì, hỏng ở đâu, vì sao chưa bỏ: đọc README + hỏi ChatGPT / Claude. Hỏng ở chỗ công cụ chung không biết cấu trúc đề lab (CP, rubric, file khung cấm sửa): phải tự paste, tự dặn, lab nào cũng làm lại từ đầu, trả lời giải thích mọi file như nhau. Chưa bỏ vì miễn phí, có sẵn, và chưa có công cụ nào chuyên cho lab *(giả thuyết, chờ phỏng vấn)*.
- Pain: học viên AI20K nhận repo lab nhưng không biết CP này phải đọc file nào, sửa file nào, file nào cấm đụng; hậu quả là mất thời gian mò repo, sửa nhầm file, làm xong mà không nối được code với bài giảng.
- Bằng chứng — số chính + kết luận (chi tiết: `evidence/summary.md`): CP1 mới có giả thuyết (`evidence/hypothesis.md`). Sẽ kiểm bằng phỏng vấn ≥3 học viên ngoài nhóm + khảo sát ≥20 + hỏi 1–2 mentor, trước CP2.

## §2. Impact & quyết định chọn *(guide 1.3)*

| Hướng | Bao nhiêu người gặp | Bao nhiêu lần / tháng | Mỗi lần tốn gì | Impact / tháng | Làm kịp không | Chọn? |
|---|---|---|---|---|---|---|
| Trợ lý repo lab theo CP (lõi + 3 feature) | __ học viên AI20K *(chờ sĩ số)* | ~__ lab / tháng *(tự ước tính, chờ phỏng vấn)* | ~__ phút mò repo / lab *(giả thuyết ≥15)* | __ | Có — lõi nhỏ, test lấy từ lab Day1–15 thật | ✅ |
| Feynman tutor đứng riêng (ôn lại lab sau khi nộp) | __ | thấp — chỉ khi sắp bị hỏi vấn đáp *(tự ước tính)* | __ | __ | Có | ❌ gộp thành feature 3 |
| Gallery format tóm tắt repo | __ | __ | __ | __ | Có | ❌ |

- **Impact / tháng** của hướng chọn = __ người × __ lần × __ phút = __ — nguồn từng thừa số: chờ phỏng vấn / khảo sát *(chưa có số, không tự điền)*
- Hướng ĐÃ LOẠI + vì sao (giữ lại, đừng xoá):
    - Track B (B1 tra cứu hướng dẫn, B2 tương tác thuốc, B3 sàng lọc tại nhà thuốc): B2 rủi ro y khoa cao; B3 khó gặp dược sĩ trong 2 ngày; nhóm không muốn làm y tế
    - Feynman tutor đứng riêng: không ai tự mở app để bị kiểm tra; trộn 2 bài toán (hiểu lab + kiểm tra hiểu). Giữ lại làm feature 3 dùng chung lõi
    - App cho mentor kiểm tra từng học viên: thành công cụ giám sát, trái luật Track A (lỗi cá nhân không công khai)
    - Gallery format tóm tắt repo: trùng DeepWiki / GitDiagram, phần AI mờ, khó viết chuẩn "đạt"
- Số lần / tháng của từng kiểu người dùng (dùng cho persona ở §8): chờ phỏng vấn

## §3. Giải pháp tương tự *(guide 2.1)*
- [sản phẩm / tính năng gần giống]: một điều đáng học · một điều đáng né · mình khác gì

## §4. Thiết kế *(guide 2.2, 3.2)*
- **Lát cắt MỘT CÂU** (1 người dùng · 1 việc · 1 quyết định AI · 1 kết quả):
- Không làm (≥3 điều):
- **Sơ đồ** (ảnh / Mermaid / draw.io): [chèn ở đây]
- **Hình dạng:** [ ] workflow cố định · [ ] một agent · [ ] nhiều agent — 2 dòng lý do, và vì sao **không** chọn hình dạng phức tạp hơn:
- **AI dựa vào đâu** — mỗi công cụ (khớp `codebase/tools.py`):

  | Công cụ | Input | Output | Tác động ra ngoài? |
  |---|---|---|---|
  |  |  |  |  |

- **Mức tự động:** [ ] AI gợi ý, người quyết · [ ] AI tự làm khi chắc, chuyển người khi không · [ ] AI tự làm — lý do (sai thì ai chịu gì, sửa đắt hay rẻ):
- **Chỗ chặn rủi ro** (rủi ro lớn nhất của lát cắt bị chặn ở đâu, bằng gì):
- **Chỗ người duyệt** (việc AI không được tự làm):
- **Nguyên tắc thiết kế** (≥3, bắt buộc G10):

  | Nguyên tắc | Chỗ cụ thể trên sơ đồ / trong bản chạy thử |
  |---|---|
  | G10 — thu hẹp phạm vi khi không chắc |  |
  |  |  |
  |  |  |

- Phần nào còn giả (công cụ trả dữ liệu giả, model chế độ giả…) — ghi rõ, không giả làm thật:

## §5. Chỗ khó — 4 lớp + ≥6 kịch bản + 2 tấn công *(guide 2.3)*

| Kịch bản | Lớp (1–4) | Hành vi mong muốn (nói gì, hiện gì, cho làm gì tiếp) | Câu thử |
|---|---|---|---|
|  |  |  |  |
| *(tấn công)* |  |  |  |
| *(tấn công)* |  |  |  |

(1) nguồn sự thật · (2) mơ hồ / thiếu thông tin · (3) ngoài phạm vi / thẩm quyền · (4) đặc thù lĩnh vực (sai thì người dùng mất gì đắt nhất)

## §6. Bốn đường đi của trải nghiệm
- Mọi thứ suôn sẻ: · Không chắc (lớp 2): · Không có căn cứ (lớp 1): · Người dùng sửa:
- Bị đòi ngoài phạm vi (lớp 3): · Trường hợp đặc thù lĩnh vực (lớp 4):

## §7. Đánh giá & chuẩn "đạt" *(guide 2.4, 4.1)*
- Data card: `data/DATA_CARD.md` · bộ câu thử: `eval/benchmark.csv` — __ câu (thuong __ · kho __ · tu_choi __) · metric: `eval/metric_spec.yaml` (__ metric)
- **Chuẩn "đạt"** (chốt **trước 19:30 Thứ Sáu 27/11**, giữ nguyên đến 23:59 Thứ Bảy 28/11): "Đạt khi ≥ __% câu qua, và __"
- Kết quả: lượt 1 __/__ (__%) · lượt 2 __/__ (__%) — run ID: __ / __ → chi tiết `eval/report.md`, hồ sơ `eval/README.md`

## §8. Chi phí khi dùng thật *(guide 4.2)*
- Persona + giá: `cost/personas.yaml` · lượt mô phỏng: `cost/simulate-__.csv` (__ phiên)
- Chi phí / task thành công: __ (model __) · __ (model __)
- Chi phí / tháng ở quy mô thật: thấp __ · cơ sở __ · cao __ → chi tiết `cost/cost-estimate.md`
- So với impact / người / tháng (§2): đáng làm không, vì sao:

## §9. Rủi ro & an toàn
- Dữ liệu: đã ẩn danh gì, không thu gì, không đưa gì vào model gói miễn phí:
- AI **không được** làm gì kể cả khi người dùng yêu cầu:
- Ai có thể bị hại nếu AI sai, và nhóm chặn thế nào:

## §10. Phân công & changelog
- Phân công có tên (theo chặng, chia cặp — guide "Cách chia việc"): __
- Dùng AI vào việc gì (2–3 dòng; chi tiết `docs/ai-usage.md`):
- Nhật ký thay đổi — **mọi thay đổi sau CP2 19:30 Thứ Sáu 27/11 phải có dòng ở đây**:

**CP2 → CP4** (vd thu hẹp lát cắt, hỏi thêm người dùng, lần cải tiến trước lượt 2)

| Thời điểm | Đổi gì | Vì sao (trỏ về câu thử / lỗi / bằng chứng nào) |
|---|---|---|
|  |  |  |

**Sau CP4 (đến 23:59 Thứ Bảy 28/11)** (sửa theo góp ý — không sửa chuẩn "đạt", câu thử, số bằng chứng, kết quả các lượt đã chạy)

| Thời điểm | Đổi gì | Vì sao |
|---|---|---|
|  |  |  |
