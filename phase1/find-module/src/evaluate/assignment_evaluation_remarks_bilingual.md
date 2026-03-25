# Nhận xét kết quả phân loại / Evaluation Remarks

## Tiếng Việt

### Tổng quan
Bộ phân loại hiện cho thấy hiệu quả **khá tốt với các issue SKPM**, nhưng hiệu năng tổng thể vẫn còn hạn chế khi đánh giá trên toàn bộ tập dữ liệu có bao gồm các issue ngoài phạm vi 4 module chính.

- **Tổng số issue**: **719**
- **Độ chính xác tổng thể** (5 lớp: OMA, SKMSAgent, SEM, SKPM, Others): **37.97%**
- **Độ chính xác trong phạm vi 4 module chính**: **50.50%**
- **Macro F1**: **44.34%**
- **Weighted F1**: **36.79%**

### Điểm mạnh
- **SKPM** là module có kết quả tốt nhất, với **Precision = 91.67%**, **Recall = 88.00%**, **F1 = 89.80%**.
- Bộ luật hiện tại cũng nhận diện **OMA** ở mức chấp nhận được về độ bao phủ, với **Recall = 64.56%**.
- Khi issue thực sự thuộc 4 module chính, mô hình đạt **50.50% accuracy**, tức là rule-based classifier đã học được một phần tín hiệu miền nghiệp vụ.

### Điểm yếu
- **Others** là lớp yếu nhất: **Recall chỉ 8.41%**, nghĩa là phần lớn issue ngoài phạm vi vẫn bị ép sang một trong 4 module chính thay vì bị từ chối bằng `UNKNOWN`.
- **SEM đang bị over-predict mạnh**: có **327** dự đoán SEM, trong khi ground truth SEM chỉ có **151** issue. Điều này làm precision của SEM giảm còn **23.85%**.
- **SKMSAgent** có **Precision cao (84.51%) nhưng Recall thấp (30.00%)**, cho thấy rule hiện tại khá “chặt”, chỉ bắt được một phần nhỏ issue thật sự thuộc SKMSAgent.
- Các nhầm lẫn lớn nhất là:
  - **Others → SEM: 133**
  - **SKMSAgent → SEM: 87**
  - **SEM → Others: 40**
  - **OMA → SEM: 26**

### Diễn giải ngắn gọn
Hiện tại classifier có xu hướng:
1. **Nhận diện rất tốt SKPM**
2. **Dự đoán SEM quá nhiều**
3. **Thiếu cơ chế reject hiệu quả cho issue ngoài phạm vi**
4. **Chưa tách tốt giữa SKMSAgent và SEM**, đặc biệt khi log chứa nhiều tín hiệu chồng lấp

### Khuyến nghị cải thiện
1. **Tăng độ mạnh của cơ chế `UNKNOWN` / reject**
   - Tăng threshold cho auto-assign
   - Bổ sung rule phạt khi score top-1 không vượt rõ top-2
   - Cân nhắc trả về `UNKNOWN` khi evidence quá loãng hoặc lẫn nhiều module

2. **Giảm bias về SEM**
   - Rà lại keyword SEM quá rộng
   - Giảm bonus cho các rule SEM đang bắt quá nhiều log chung
   - Loại bỏ những từ khóa xuất hiện phổ biến ở issue ngoài phạm vi

3. **Tăng recall cho SKMSAgent**
   - Bổ sung keyword đặc trưng hơn cho app/package/service của agent
   - Thêm priority rule giúp thắng SEM trong các case agent-centric

4. **Tách rõ in-scope và out-of-scope**
   - Nên theo hướng 2 tầng:
     - tầng 1: xác định `Primary Modules` vs `Others`
     - tầng 2: nếu là `Primary Modules` thì mới phân tiếp vào OMA / SKMSAgent / SEM / SKPM

---

## English

### Overview
The current classifier performs **strongly on SKPM issues**, but overall performance is still limited when the evaluation includes out-of-scope issues beyond the four primary modules.

- **Total issues**: **719**
- **Overall accuracy** (5 classes: OMA, SKMSAgent, SEM, SKPM, Others): **37.97%**
- **In-scope accuracy** (only issues whose ground truth belongs to the 4 primary modules): **50.50%**
- **Macro F1**: **44.34%**
- **Weighted F1**: **36.79%**

### Strengths
- **SKPM** is the strongest class, with **91.67% precision**, **88.00% recall**, and **89.80% F1**.
- **OMA** also shows acceptable coverage, with **64.56% recall**.
- On issues that truly belong to the 4 supported modules, the classifier reaches **50.50% accuracy**, which shows that the rule-based design is already capturing meaningful domain signals.

### Weaknesses
- **Others** is the weakest class: **recall is only 8.41%**, meaning that most out-of-scope issues are still forced into one of the four primary modules instead of being rejected as `UNKNOWN`.
- **SEM is heavily over-predicted**: there are **327** SEM predictions, while only **151** issues are actually SEM. This drives SEM precision down to **23.85%**.
- **SKMSAgent** has **high precision (84.51%) but low recall (30.00%)**, indicating that the current rules are too conservative and miss many real SKMSAgent issues.
- The largest confusion patterns are:
  - **Others → SEM: 133**
  - **SKMSAgent → SEM: 87**
  - **SEM → Others: 40**
  - **OMA → SEM: 26**

### Short interpretation
At this stage, the classifier tends to:
1. **Detect SKPM very well**
2. **Over-assign SEM**
3. **Lack a strong reject mechanism for out-of-scope issues**
4. **Struggle to separate SKMSAgent from SEM**, especially when logs contain overlapping evidence

### Recommendations
1. **Strengthen the `UNKNOWN` / reject behavior**
   - Increase the auto-assign threshold
   - Add penalty rules when top-1 does not clearly outperform top-2
   - Return `UNKNOWN` when evidence is sparse or highly mixed

2. **Reduce SEM bias**
   - Review overly broad SEM keywords
   - Reduce SEM rule bonuses that fire on generic logs
   - Remove keywords that frequently appear in out-of-scope issues

3. **Improve SKMSAgent recall**
   - Add more agent-specific app/package/service keywords
   - Introduce priority rules that allow SKMSAgent to win against SEM in agent-centric cases

4. **Separate in-scope vs out-of-scope detection**
   - A 2-stage design would likely work better:
     - stage 1: determine `Primary Modules` vs `Others`
     - stage 2: if `Primary Modules`, classify into OMA / SKMSAgent / SEM / SKPM
