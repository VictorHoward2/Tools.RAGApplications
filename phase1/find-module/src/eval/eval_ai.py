import json
from collections import defaultdict
from pathlib import Path

def evaluate_ai_classification(json_file_path: Path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            issues = json.load(f)
    except FileNotFoundError:
        print(f"[Lỗi] Không tìm thấy file {json_file_path}. Cậu nhớ chạy script AI trước nhé!")
        return
        
    total_issues = len(issues)
    if total_issues == 0:
        print("File JSON trống không có dữ liệu để đánh giá.")
        return

    correct_predictions = 0
    
    # Khởi tạo từ điển để lưu trữ thống kê cho 4 module chính
    module_stats = defaultdict(lambda: {"true_positive": 0, "false_positive": 0, "false_negative": 0})
    target_modules = ["OMA", "SKMSAgent", "SEM", "SKPM"]
    
    for issue in issues:
        # Lấy nhãn thực tế (Ground Truth)
        metadata = issue.get("metadata", {})
        ground_truth = metadata.get("type", "").strip() if metadata.get("type") else "UNKNOWN"
        
        # Lấy kết quả dự đoán của AI (từ trường mới assignment_prediction_ai)
        prediction_ai_info = issue.get("assignment_prediction_ai", {})
        predicted = prediction_ai_info.get("predicted_module", "UNKNOWN").strip()
        
        # Đếm tổng số ca đoán đúng
        if predicted == ground_truth:
            correct_predictions += 1
            if predicted in target_modules:
                module_stats[predicted]["true_positive"] += 1
        else:
            # Nếu đoán sai, ghi nhận lỗi cho từng module
            if predicted in target_modules:
                # AI đoán là module X nhưng thực tế không phải -> Dương tính giả (vơ nhầm)
                module_stats[predicted]["false_positive"] += 1
                
            if ground_truth in target_modules:
                # Thực tế là module Y nhưng AI lại đoán ra cái khác hoặc UNKNOWN -> Âm tính giả (bỏ lọt)
                module_stats[ground_truth]["false_negative"] += 1
                
    # Tính toán kết quả tổng thể
    overall_accuracy = (correct_predictions / total_issues) * 100
    
    print("\n" + "="*55)
    print("BÁO CÁO ĐỘ CHÍNH XÁC CỦA AI (AI EVALUATION REPORT)")
    print("="*55)
    print(f"Tổng số lượng Issue đã quét : {total_issues}")
    print(f"Số lượng dự đoán chính xác  : {correct_predictions}")
    print(f"Độ chính xác tổng (Accuracy): {overall_accuracy:.2f}%\n")
    
    print("--- Phân tích chi tiết từng Module sau khi AI lọc ---")
    for module in target_modules:
        stats = module_stats[module]
        tp = stats["true_positive"]
        fp = stats["false_positive"]
        fn = stats["false_negative"]
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        
        print(f"[{module}]")
        print(f"  - Precision (Độ chuẩn xác): {precision:.2f}% (AI dự đoán {tp+fp} ca, đúng {tp} ca)")
        print(f"  - Recall (Độ bao phủ)     : {recall:.2f}% (Thực tế có {tp+fn} ca, AI bắt được {tp} ca)")
        print()

if __name__ == "__main__":
    # Điền tên file output từ script Ollama lúc nãy vào đây
    INPUT_JSON = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag_with_assignment_ai.json")
    evaluate_ai_classification(INPUT_JSON)