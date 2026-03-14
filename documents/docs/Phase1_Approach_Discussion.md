# Thảo luận: Phase 1 - AITOPIA

> Ghi lại cuộc thảo luận về cách giải quyết 2 bài toán nhỏ trong Phase 1.

---

## Bối cảnh

Phase 1 cần giải quyết 2 bài toán:

1. **Tìm PIC** (Person In Charge)
2. **Xác định** xem Issue giống thế này trước đây đã gặp và giải quyết chưa

---

## Bài toán 1: Tìm PIC

### Đề xuất dự kiến

- Đã có mapping: **Module → PIC** (mỗi Module tương ứng 1 PIC)
- Bài toán quy về: **Issue này thuộc Module nào?**
- Có sẵn danh sách mô tả các Module (còn hơi sơ sài)
- **Giải pháp (ban đầu)**: LLM đọc toàn bộ thông tin các Module + thông tin Issue hiện tại → đưa ra Module tương ứng → suy ra PIC

### Lo ngại: Mở rộng nhiều Module

Khi hệ thống mở rộng ra **rất nhiều Module**, việc đưa hết mô tả Module vào prompt có thể **không ổn**:

- **Context limit**: Số token vượt giới hạn context của LLM
- **Chi phí & độ trễ**: Mỗi lần gọi đều tốn token cho toàn bộ Module
- **Chất lượng**: Quá nhiều lựa chọn trong một prompt có thể làm LLM phân tán, dễ nhầm lẫn

→ Cần phương án **không phụ thuộc số lượng Module** trong mỗi lần gọi LLM.

### Đề xuất: Luồng hai bước (Retrieve rồi mới LLM)

**Bước 1 – Thu hẹp ứng viên (không dùng LLM, hoặc dùng embedding):**

- Lưu mỗi Module dưới dạng một “document”: mô tả + từ khóa + (nếu có) ví dụ Issue điển hình.
- **Embed** Issue hiện tại và **embed** từng Module (hoặc dùng keyword matching nếu có từ khóa chuẩn).
- Chọn **top-k Module** (VD: k = 5–10) gần với Issue nhất.

**Bước 2 – LLM chỉ quyết định trong k ứng viên:**

- Prompt chỉ gồm: **thông tin Issue** + **k mô tả Module** (đã thu hẹp).
- LLM chọn 1 Module (hoặc xếp hạng + độ tin cậy) trong k ứng viên đó.

**Lợi ích:**

- Kích thước prompt **cố định** theo k, không tăng khi thêm Module.
- Có thể tăng số Module tùy ý; chỉ cần cập nhật index/embedding khi thêm/sửa Module.
- Có thể tái dùng cùng cơ chế embedding với bài toán 2 (RAG Issue) nếu dùng chung model.

**Lưu ý:**

- k đủ lớn để không bỏ sót Module đúng (thường 5–10 là đủ nếu embedding tốt).
- Nếu Module đúng không nằm trong top-k → có thể tăng k, hoặc cải thiện mô tả/từ khóa/embedding cho Module đó.

### Nhận xét & góp ý

**Ưu điểm:**
- Đơn giản, dễ triển khai
- Tận dụng được mapping sẵn có
- LLM phù hợp với bài toán phân loại dựa trên mô tả ngữ nghĩa

**Góp ý (vẫn áp dụng khi dùng luồng hai bước):**

1. **Cải thiện mô tả Module**: Mô tả sơ sài có thể làm LLM nhầm lẫn. Nên bổ sung:
   - Ví dụ Issue điển hình thuộc Module đó
   - Từ khóa / pattern thường gặp (VD: fingerprint, Samsung Wallet, FIDO...)
   - Các trường PLM có thể dùng làm gợi ý (Occurr. Type, Appearance Classification, Resolved Layer...)

2. **Prompt design** (bước 2): 
   - Cho LLM output dạng structured (VD: JSON với `module`, `confidence`, `reasoning`)
   - Thêm option "không chắc chắn" để fallback sang semi-automated

3. **Few-shot** (bước 2): Nếu có vài cặp (Issue, Module) đã gán sẵn, thêm vào prompt để tăng độ chính xác

4. **Fallback**: Khi LLM không chắc → gợi ý top 2–3 Module trong k ứng viên cho Dev chọn

---

## Bài toán 2: Xác định Issue tương tự đã giải quyết chưa

### Thông tin cần trích xuất từ PLM Issue

Tham chiếu cấu trúc đầy đủ: **`memory-bank/PLM_ISSUE_STRUCTURE.md`**. Dưới đây là các trường cần trích xuất cho bài toán này, nhóm theo mục đích sử dụng.

#### 1. Cho embedding / RAG (tìm Issue tương tự)

Dùng để tạo vector tìm kiếm và so sánh ngữ nghĩa. Nên gộp thành **một hoặc vài chuỗi** trước khi embed:

| Nguồn | Trường cần trích | Ghi chú |
|-------|------------------|--------|
| **Định danh** | Defect Code, Title | Title thường tóm tắt nội dung |
| **Problem**  | Problem, Reproduction Route | Mô tả lỗi + cách tái hiện; đa ngôn ngữ |
| **Solution**  | Cause, Countermeasure | Chỉ có khi Issue đã Resolve; là knowledge chính |
| **Comment** | Toàn bộ lịch sử Comment | ETA, phân tích Root Cause, workaround, thảo luận |

→ **Chunk để embed**: có thể 1 chunk = 1 Issue (gộp Problem + Reproduction Route + Cause + Countermeasure + Comment), hoặc tách riêng phần “vấn đề” và phần “giải pháp” nếu cần chunk nhỏ hơn.

#### 2. Cho metadata / bộ điều kiện (lọc, so sánh nhanh)

Dùng để lọc (VD: chỉ lấy Issue đã Resolve), hoặc điều kiện “cùng Model/OS”:

| Nguồn | Trường cần trích | Ghi chú |
|-------|------------------|--------|
| **Định danh** | Defect Code, Defect ID | Để tham chiếu và link |
| **Form/hidden** (§9) | defectVO.status, defectVO.resolveStatus | RESOLVE vs OPEN; cần cho filter “đã giải quyết” |
| **Thiết bị & phân loại** (§6) | Model No., OS Ver., Build No., Occurr. Type, Appearance Classification, Detailed Failure Situation | So sánh nhanh, điều kiện “cùng Model/OS/App” |
| **Solution** (§4) | Resolution S/W Ver., Resolve Option | Bổ sung ngữ cảnh khi đã Resolve |

#### 3. Cho input LLM (khi đánh giá “đã gặp/giải quyết chưa”)

Khi đưa **Issue hiện tại** và **k Issue tương tự** vào LLM, mỗi Issue nên có đủ thông tin sau:

| Nguồn | Trường cần trích | Ghi chú |
|-------|------------------|--------|
| **Định danh** | Defect Code, Title | Để LLM trích dẫn và gợi ý |
| **Problem** (§2) | Problem, Reproduction Route (rút gọn nếu quá dài) | Ngữ cảnh vấn đề |
| **Solution** (§4) | Cause, Countermeasure | **Bắt buộc** nếu Issue đã Resolve; dùng để gợi ý giải pháp |
| **Comment** (§7) | Comment (có thể rút gọn hoặc chỉ các comment có phân tích/giải pháp) | Bằng chứng bổ sung |
| **Metadata** | status (đã Resolve hay chưa), Model No., OS Ver. | Giúp LLM hiểu độ liên quan |

#### 4. Tóm tắt bảng trích xuất

| Nhóm | Mục đích | Các trường chính |
|------|----------|------------------|
| **Embedding** | RAG / tìm tương tự | Title, Problem, Reproduction Route, Cause, Countermeasure, Comment |
| **Metadata** | Lọc, điều kiện | Defect Code, status, resolveStatus, Model No., OS Ver., Build No., Occurr. Type, Appearance Classification, Detailed Failure Situation |
| **Cho LLM** | Đánh giá + gợi ý | Defect Code, Title, Problem, Reproduction Route, Cause, Countermeasure, Comment (tóm tắt), status, Model/OS |

**Lưu ý**: Comment (§7) chứa nhiều bằng chứng quan trọng (Root Cause, workaround) → bắt buộc trích xuất cho cả embedding và input LLM.

---

### Đề xuất dự kiến

- Thu thập một số lượng cụ thể các Issue từ tất cả các Module
- Dùng **RAG** để tìm **k Issue** giống với Issue hiện tại
- Thiết kế **bộ điều kiện**: nếu độ giống cao hoặc thỏa mãn điều kiện nào đó → kết luận 2 Issue tương tự
- Đưa vào LLM: Issue hiện tại + k Issue tương tự + bộ lọc → LLM đánh giá → kết luận đã gặp/giải quyết chưa

### Nhận xét & góp ý

**Ưu điểm:**
- RAG phù hợp: tìm nhanh trong corpus lớn, không cần so sánh từng cặp
- Kết hợp rule (bộ điều kiện) + LLM: cân bằng giữa tốc độ và độ chính xác
- LLM làm lớp cuối để đánh giá ngữ nghĩa, tránh false positive từ similarity thuần túy

**Góp ý:**

1. **Chọn k hợp lý**: 
   - k quá nhỏ (3–5): có thể bỏ sót Issue tương tự
   - k quá lớn (20+): tốn token, LLM khó tập trung
   - Gợi ý: k = 5–10, có thể lấy thêm nếu score gần ngưỡng

2. **Chunking cho RAG**:
   - Mỗi Issue nên embed dựa trên: **Problem + Reproduction Route + (nếu có) Cause + Countermeasure + Comment**
   - Có thể tách: 1 chunk = 1 Issue (full) hoặc tách Problem / Solution thành chunk riêng tùy kích thước

3. **Bộ điều kiện**:
   - Đề xuất cấu trúc rõ ràng, VD:
     - `similarity_score >= 0.85` → tương tự mạnh
     - `similarity_score >= 0.75` **và** `cùng Model/OS/App` → tương tự
     - `có Cause + Countermeasure` trong Issue tìm được → ưu tiên (đã giải quyết)
   - Lưu ý: Issue "tương tự" nhưng chưa Resolve thì chưa giúp được gì → nên ưu tiên Issue đã có Solution

4. **Input cho LLM**:
   - Chỉ đưa k Issue **đã Resolve** (có Cause, Countermeasure) vào prompt
   - Hoặc đánh dấu rõ: Issue nào đã giải quyết, Issue nào chưa
   - Output: `có_tương_tự: bool`, `issue_tham_chiếu: [defect_code]`, `độ_tin_cậy`, `gợi_ý_giải_pháp` (trích từ Countermeasure)

5. **Đa ngôn ngữ**:
   - Issue có thể tiếng Trung, tiếng Anh → embedding model cần hỗ trợ multilingual (VD: multilingual-e5, paraphrase-multilingual)

6. **Cập nhật knowledge base**:
   - Định kỳ thêm Issue mới đã Resolve vào RAG để tăng độ phủ

---

## Tóm tắt luồng đề xuất

```
[Issue mới]
    │
    ├─► Bài toán 1 (hai bước):
    │       Embed(Issue) + Index(Module) → top-k Module
    │       → LLM(Issue + k Module) → Module → PIC
    │
    └─► Bài toán 2: RAG(Issue) → k Issue tương tự
                              → Bộ điều kiện (filter)
                              → LLM(Issue + k results + conditions) → Đã gặp/giải quyết chưa? + Gợi ý
```

---

## Các điểm cần làm rõ thêm (nếu có)

- Số lượng Issue dự kiến thu thập cho RAG (mỗi Module / tổng)?
- Định dạng mô tả Module hiện tại (để thiết kế prompt)?
- Bộ điều kiện cụ thể bạn đang nghĩ tới?
- Có dữ liệu labeled (Issue → Module, Issue A ~ Issue B) để đánh giá không?
