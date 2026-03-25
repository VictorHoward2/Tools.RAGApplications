# Issue Module Assignment Classifier

## English

### Overview
This project classifies an issue into a target module using a simple, explainable rule-based scoring approach. It scans issue text fields, scores matched keywords by strength and field weight, applies priority bonus rules, then returns the predicted module, PIC, confidence, review status, and explanation details.

### Supported modules
- OMA
- SKMSAgent
- SEM
- SKPM

### How it works
1. Normalize text from `search_text`, `evidence_text`, and `raw_comments`.
2. Count keyword occurrences for each module.
3. Compute score using:
   - keyword level weight: `strong`, `medium`, `weak`
   - field weight: `search_text`, `evidence_text`, `raw_comments`
4. Apply priority bonus rules for highly indicative patterns.
5. Pick the top module, estimate confidence, and decide review status:
   - `manual_review`
   - `review_recommended`
   - `auto_assign`

### Main files
- `classifier.py`: core scoring and classification logic
- `keyword_config.py`: module keywords, weights, thresholds, PIC mapping, priority rules
- `pic_mapper.py`: maps predicted module to PIC
- `assign_demo.py`: runs a simple demo and prints the result
- `export_assignment_json.py`: enriches all issues in a JSON file with prediction output

### Expected input
Each issue should be a JSON object with fields such as:

```json
{
  "id": "ISSUE-001",
  "search_text": "...",
  "evidence_text": "...",
  "raw_comments": ["...", "..."],
  "metadata": {
    "type": "OMA"
  }
}
```

### Output
The classifier returns fields including:
- `predicted_module`
- `predicted_pic`
- `confidence`
- `review_status`
- `top_2_candidates`
- `scores`
- `matched_rules`
- `top_reasons`
- `ground_truth_module`

### Quick usage
Run demo:

```bash
python assign_demo.py
```

Export enriched JSON:

```bash
python export_assignment_json.py
```

Use inside Python:

```python
from classifier import classify_issue

issue = {
    "id": "ISSUE-001",
    "search_text": "OMAPI CTS failed",
    "evidence_text": "secureelementservice error",
    "raw_comments": ["VTS secure element test failed"],
    "metadata": {"type": "OMA"}
}

result = classify_issue(issue)
print(result)
```

### Notes
- This is a heuristic classifier, so it is easy to debug and tune.
- To improve accuracy, update `MODULE_KEYWORDS`, `PRIORITY_RULES`, and thresholds in `keyword_config.py`.
- The current demo/export scripts use local Windows paths, so update them before running in a different environment.

---

## Tiếng Việt

### Tổng quan
Dự án này dùng cách chấm điểm theo từ khóa để phân loại một issue vào module phù hợp. Chương trình quét các trường văn bản của issue, tính điểm theo độ mạnh của từ khóa và trọng số của từng trường, cộng thêm rule ưu tiên, rồi trả về module dự đoán, PIC, confidence, trạng thái review và các lý do giải thích.

### Các module hỗ trợ
- OMA
- SKMSAgent
- SEM
- SKPM

### Cách hoạt động
1. Chuẩn hóa dữ liệu từ `search_text`, `evidence_text` và `raw_comments`.
2. Đếm số lần xuất hiện của từ khóa cho từng module.
3. Tính điểm dựa trên:
   - trọng số mức từ khóa: `strong`, `medium`, `weak`
   - trọng số trường dữ liệu: `search_text`, `evidence_text`, `raw_comments`
4. Áp dụng các rule bonus cho những pattern có độ đặc trưng cao.
5. Chọn module có điểm cao nhất, ước lượng confidence và quyết định trạng thái xử lý:
   - `manual_review`
   - `review_recommended`
   - `auto_assign`

### Các file chính
- `classifier.py`: logic chấm điểm và phân loại chính
- `keyword_config.py`: cấu hình từ khóa, trọng số, ngưỡng, PIC và rule ưu tiên
- `pic_mapper.py`: ánh xạ module sang PIC
- `assign_demo.py`: chạy thử một issue mẫu và in kết quả
- `export_assignment_json.py`: ghi kết quả dự đoán vào toàn bộ file JSON đầu vào

### Dữ liệu đầu vào mong đợi
Mỗi issue nên là một object JSON có dạng:

```json
{
  "id": "ISSUE-001",
  "search_text": "...",
  "evidence_text": "...",
  "raw_comments": ["...", "..."],
  "metadata": {
    "type": "OMA"
  }
}
```

### Kết quả đầu ra
Bộ phân loại trả về các trường như:
- `predicted_module`
- `predicted_pic`
- `confidence`
- `review_status`
- `top_2_candidates`
- `scores`
- `matched_rules`
- `top_reasons`
- `ground_truth_module`

### Cách dùng nhanh
Chạy demo:

```bash
python assign_demo.py
```

Xuất file JSON đã gắn kết quả dự đoán:

```bash
python export_assignment_json.py
```

Dùng trực tiếp trong Python:

```python
from classifier import classify_issue

issue = {
    "id": "ISSUE-001",
    "search_text": "OMAPI CTS failed",
    "evidence_text": "secureelementservice error",
    "raw_comments": ["VTS secure element test failed"],
    "metadata": {"type": "OMA"}
}

result = classify_issue(issue)
print(result)
```

### Ghi chú
- Đây là bộ phân loại heuristic nên dễ debug và dễ tinh chỉnh.
- Muốn tăng độ chính xác, hãy cập nhật `MODULE_KEYWORDS`, `PRIORITY_RULES` và các ngưỡng trong `keyword_config.py`.
- Các script demo/export hiện đang dùng đường dẫn Windows cứng, nên cần sửa lại nếu chạy ở môi trường khác.
