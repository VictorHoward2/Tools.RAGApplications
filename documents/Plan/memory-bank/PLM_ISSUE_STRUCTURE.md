# Cấu trúc PLM Issue - Tài liệu tham chiếu

> Phân tích từ sample: `sample plm issue/[PLM] P240613-02380-View Problem.html`, `[PLM] P241202-07082-View Problem.html`

Đọc file này để hiểu cặn kẽ cấu trúc một PLM Issue khi trích xuất dữ liệu, xây RAG, hoặc tích hợp với UTOPIA.

---

## 1. Thông tin định danh

| Thành phần | Mô tả | Ví dụ |
|------------|-------|-------|
| **Defect Code** | Mã Issue duy nhất, format PYYMMDD-XXXXX | P240613-02380, P241202-07082 |
| **Defect ID** | ID nội bộ (hidden field) | 01R7PV8TCtPMWL1000 |
| **Title** | Tiêu đề Issue | [慧博][莫彬][Samsung Members][59378814]... Alipay and Taobao cannot use fingerprint payment... |
| **refObjectId** | ID project/model | 00QOQX414tPMWL1000 |
| **refObjectType** | Loại project | ETC, DEV |

---

## 2. Phần Problem (Vấn đề)

| Trường | Nhãn HTML | Nội dung |
|--------|-----------|----------|
| **Problem** | `[Problem]` | Mô tả chi tiết lỗi. Có thể đa ngôn ngữ (tiếng Trung, tiếng Anh). Thường có [Samsung Members Notice] |
| **Reproduction Route** | `[Reproduction Route]` | Thông tin tái hiện: Device Name, Model No., CSC, OS Ver., Build No., Carrier, liên hệ, mô tả người dùng |
| **Expected Result** | `[Expected Result]` | Thường là Bug Resolve Instruction (hướng dẫn xử lý chuẩn) |
| **Attachment** | `[Attachment]` | File đính kèm: ảnh, log (zip), v.v. |

### Cấu trúc chuẩn Reproduction Route

```
[Original Contents] : 
联系方式: [số điện thoại]
用户描述: [mô tả người dùng]

[Device Name] : Galaxy S24 Ultra
[Model No.] : SM-S9280
[CSC] : CHC
[OS Ver.] : 14
[Build No.] : S9280ZCS2AXD3
[Carrier] : [chuỗi carrier]
```

---

## 3. Phần Resolve Charge (PIC - Person In Charge)

Bảng người phụ trách xử lý Issue:

| Cột | Mô tả |
|-----|-------|
| **Type** | Main / Sub |
| **Type** | S/W, H/W, v.v. |
| **Name** | Tên người phụ trách |
| **Position/Position Name** | Chức vụ |
| **Dept.** | Phòng ban |
| **Company** | Công ty |

→ **Quan trọng cho AITOPIA Phase 1**: Đây là nguồn để tìm PIC.

---

## 4. Phần Solution (Giải pháp) - Khi đã Resolve

| Trường | Nhãn HTML | Nội dung |
|--------|-----------|----------|
| **Register** | - | Người đăng ký giải pháp (tên + email) |
| **Reg. Date / Resolved Date** | - | Ngày đăng ký / giải quyết (kèm thời gian) |
| **Cause** | `[Cause]` | **Root Cause** - Nguyên nhân gốc |
| **Countermeasure** | `[Countermeasure]` | Giải pháp / cách khắc phục |
| **Attachment** | `[Attachment]` | File đính kèm liên quan |
| **Resolution S/W Ver.** | - | Phiên bản S/W giải quyết (VD: S9280ZCS2AXD3) |
| **Resolved Layer** | - | Lớp xử lý (VD: Kernel (System)) |
| **Resolve Option** | - | Maintain current status, issue fixed, CS guiding, v.v. |

→ **Quan trọng cho RAG**: Cause + Countermeasure là nguồn knowledge chính.

---

## 5. Phần Confirm Resolved (Xác nhận đóng)

| Thành phần | Mô tả |
|------------|-------|
| **Checked by** | Người xác nhận |
| **Resolved Confirm Date** | Ngày xác nhận |
| **Verification Completion Target Date** | Ngày mục tiêu hoàn thành kiểm tra |
| **Resolution Confirmation S/W Ver.** | Phiên bản S/W xác nhận |
| **Close Option** | VD: Decided_Design/Concept |

---

## 6. Thông tin thiết bị & phân loại

| Trường | Ví dụ |
|--------|-------|
| **Model No.** | SM-S9280_CHN_CHC, SM-F9360 |
| **OS Ver.** | Android 14, Android 13 |
| **AP Vendor** | Qualcomm |
| **AP Series** | SM8650 |
| **Nation(Location)** | China Mainland |
| **Occurr. Type** | Samsung Members VOC |
| **Defect type** | - |
| **Appearance Classification** | FUNCTION |
| **Detailed Failure Situation** | Wrong Popup |
| **Symptom Type** | High/Mid/Low-level |

---

## 7. Phần Comment - QUAN TRỌNG (Bằng chứng)

**Phần Comment có thể chứa nhiều thông tin quan trọng (bằng chứng)** mà không có ở các trường chính thức:

| Loại thông tin | Mô tả |
|----------------|-------|
| **ETA, tiến độ** | Thời gian dự kiến hoàn thành, cập nhật tiến độ |
| **Phân tích Root Cause** | Dev có thể comment phân tích trước khi điền vào [Cause] chính thức |
| **Gợi ý giải pháp, workaround** | Cách xử lý tạm thời, hướng dẫn cho user |
| **Thảo luận nội bộ** | Trao đổi giữa Dev, Tester, PL |
| **Yêu cầu thêm log/info** | Khi cần user cung cấp thêm thông tin |

→ **Bắt buộc trích xuất và đưa vào RAG/knowledge base** khi xây dựng hệ thống AITOPIA.

---

## 8. Các phần mở rộng (có thể thu gọn)

| Phần | Mô tả |
|------|-------|
| **Log Analysis** | Phân tích log (iframe) |
| **SCM (CL / Commit ID) Info.** | Thông tin CL, Commit ID, S/W Version |
| **Problem Link Info.** | Issue liên quan (duplicate, same reason, v.v.) |
| **Chipset Vendor Tracking Info.** | Tracking vendor (AP, AP/CP) |
| **Comment(ETA, Status, Progress)** | Bảng tracking: Tracking No., Fix Code No., Comment, Last update by |

---

## 9. Form & Hidden fields quan trọng

```
defectVO.id              - ID Issue
defectVO.defectCode      - Mã Issue (P240613-02380)
defectVO.refObjectId     - ID project/model
defectVO.refObjectType   - Loại (ETC, DEV...)
defectVO.status          - Trạng thái (RESOLVE, OPEN...)
defectVO.resolveStatus   - Trạng thái resolve chi tiết
defectVO.gerAttachInfoId - ID nhóm file đính kèm
defectVO.getAttachInfoCount - Số lượng file đính kèm
```

---

## 10. Gợi ý trích xuất cho AITOPIA

### Cho RAG / Tìm Issue tương tự
- Problem, Reproduction Route
- Model No., OS Ver., Build No.
- Occurr. Type, Appearance Classification, Detailed Failure Situation
- **Comment** (toàn bộ lịch sử)

### Cho tìm PIC
- Bảng Resolve Charge: Main/Sub, Type (S/W-H/W), Name, Dept.

### Cho Root Cause
- [Cause] trong Solution
- **Comment** (có thể chứa phân tích sớm hơn)

### Cho giải pháp
- [Countermeasure] trong Solution
- **Comment** (workaround, gợi ý)

---

## 11. Nguồn sample

- `sample plm issue/[PLM] P240613-02380-View Problem.html`
- `sample plm issue/[PLM] P241202-07082-View Problem.html`
