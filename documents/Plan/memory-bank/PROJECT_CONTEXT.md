# AITOPIA - Project Context

> Memory bank: Đọc file này để nhanh chóng nắm bối cảnh dự án.

## Tổng quan

**AITOPIA** là hệ thống AI giúp Dev xử lý Issue PLM hiệu quả hơn bằng cách:
- Tự động tìm **PIC** (Person In Charge)
- Xác định **Root Cause**
- Xử lý Issue lặp lại (comment giải pháp đã biết)

## 3 Hệ thống liên quan

| Hệ thống | Vai trò |
|----------|---------|
| **PLM** | Quản lý Issue. Tester raise Issue → assign Dev → Dev xử lý hoặc re-assign |
| **UTOPIA** | Tự động hóa: lấy log, comment, re-assign. Cho phép chạy Python script tùy chỉnh |
| **Agent Builder** | Nền tảng kéo-thả xây Agent AI, có sẵn LLM (GAUSS), Embedding, FAISS |

## Vấn đề cần giải quyết

- Tìm PIC và Root Cause tốn nhiều công sức của Dev
- Issue giống nhau lặp lại nhiều lần, xử lý trùng lặp

## Giải pháp AITOPIA

1. **Issue giống đã xử lý** → Comment Root Cause + gợi ý xử lý
2. **Issue mới** → Tìm Root Cause → Comment lên PLM

## Cấu trúc dự án (2 Phase)

### Phase 1 (1 tháng): Tìm PIC + kiểm tra Issue tương tự
- Trích xuất thông tin PLM từ UTOPIA (Python)
- Thu thập knowledge base cho RAG
- **Thử nghiệm Agent Builder**: Kết quả không khả quan (Agent Builder thỉnh thoảng bị lag, nhiều component fix sẵn không thể tối ưu theo ý muốn)
- **Hướng tiếp theo**: Xây dựng hệ thống trên **server local - Linux**
- Tích hợp UTOPIA với hệ thống RAG

### Phase 2 (1 tháng): Tìm Root Cause + comment lên PLM
- Thiết lập MCP để lấy source code
- Phân tích Root Cause (ưu tiên: trích xuất file/hàm tiềm năng từ log)
- Tự động comment qua UTOPIA API

## Hướng đi kỹ thuật chính

- **RAG**: Dùng Issue đã xử lý làm knowledge base, tìm tương tự
- **Root Cause**: Log parser → trích file/hàm xuất hiện trong log → đưa LLM phân tích
- **Fallback**: LLM không tìm được → semi-automated + gợi ý cho Dev

## Cấu trúc PLM Issue

Xem chi tiết: **`memory-bank/PLM_ISSUE_STRUCTURE.md`**

File này mô tả cặn kẽ: định danh, Problem, Reproduction Route, PIC, Solution, Comment, hidden fields, và gợi ý trích xuất cho AITOPIA.

**Lưu ý**: Phần **Comment** chứa nhiều thông tin quan trọng (bằng chứng) → bắt buộc trích xuất cho RAG.

## Tài liệu chi tiết

- `memory-bank/PLM_ISSUE_STRUCTURE.md` - Cấu trúc PLM Issue chi tiết (đọc khi trích xuất/RAG)
- `Schedule/Plan.md` - Kế hoạch chi tiết (tiếng Việt)
- `Schedule/Overall.md` - Tổng quan, bối cảnh, risk mitigation
- `Schedule/Schedule.md` - Task breakdown theo Phase

## Local RAG (Phase 1 - Hướng chính)

Đã triển khai hệ thống RAG local tại `src/aitopia/`, giai đoạn tiếp theo sẽ phát triển trên server local Linux:

- **Chạy**: `python run.py index` → `python run.py analyze TEST-001`
- **Mock data**: `data/mock/issues.json`, `test_issues.json`
- **PIC detection**: RAG + LLM (OpenAI hoặc Mock rule-based)
- **Chi tiết**: Xem `README.md`

## Timeline

- **Mỗi Phase**: 1 tháng
- **Tổng**: 2 tháng (2 Phase)
- **Trạng thái**: Phase 1 đang triển khai (chuyển hướng sang local Linux server)
