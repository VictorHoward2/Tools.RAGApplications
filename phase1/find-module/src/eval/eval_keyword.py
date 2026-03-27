import json
from collections import defaultdict


def evaluate_classification(json_file_path: str):
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
        # Lấy nhãn thực tế (Ground Truth) từ metadata và kết quả dự đoán
        metadata = issue.get("metadata", {})
        ground_truth = metadata.get("type", "").strip() if metadata.get("type") else "UNKNOWN"
        
        prediction_info = issue.get("assignment_prediction", {})
        predicted = prediction_info.get("predicted_module", "UNKNOWN").strip()
        
        # Đếm tổng số ca đoán đúng
        if predicted == ground_truth:
            correct_predictions += 1
            if predicted in target_modules:
                module_stats[predicted]["true_positive"] += 1
        else:
            # Nếu đoán sai, ghi nhận lỗi cho từng module
            if predicted in target_modules:
                # Hệ thống đoán là module X nhưng thực tế không phải -> Dương tính giả (vơ nhầm)
                module_stats[predicted]["false_positive"] += 1
                
            if ground_truth in target_modules:
                # Thực tế là module Y nhưng hệ thống lại đoán ra cái khác -> Âm tính giả (bỏ lọt)
                module_stats[ground_truth]["false_negative"] += 1
                
    # Tính toán kết quả tổng thể
    overall_accuracy = (correct_predictions / total_issues) * 100 if total_issues > 0 else 0
    
    print("="*50)
    print(f"BÁO CÁO ĐỘ CHÍNH XÁC (EVALUATION REPORT)")
    print("="*50)
    print(f"Tổng số lượng Issue đã quét : {total_issues}")
    print(f"Số lượng dự đoán chính xác  : {correct_predictions}")
    print(f"Độ chính xác tổng (Accuracy): {overall_accuracy:.2f}%\n")
    
    print("--- Phân tích chi tiết từng Module ---")
    for module in target_modules:
        stats = module_stats[module]
        tp = stats["true_positive"]
        fp = stats["false_positive"]
        fn = stats["false_negative"]
        
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
        
        print(f"[{module}]")
        print(f"  - Precision (Độ chuẩn xác): {precision:.2f}% (Hệ thống dự đoán {tp+fp} ca thuộc về {module}, đúng {tp} ca)")
        print(f"  - Recall (Độ bao phủ)     : {recall:.2f}% (Thực tế có {tp+fn} ca thuộc về {module}, hệ thống bắt được {tp} ca)")
        print()

if __name__ == "__main__":
    evaluate_classification("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag_with_assignment.json")