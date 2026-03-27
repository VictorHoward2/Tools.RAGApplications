import json

def calculate_metrics(file_path):
    # Đọc dữ liệu từ file JSON
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Lặp qua 2 đối tượng đánh giá là 'ai' và 'human'
    for evaluator in ['ai', 'human']:
        print(f"{'-' * 10} KẾT QUẢ ĐÁNH GIÁ BỞI: {evaluator.upper()} {'-' * 10}")

        
        total_queries = 0            # Tổng số lượng query đã được đánh giá
        total_hits_evaluated = 0     # Tổng số lượng kết quả (issue) đã được đánh giá
        total_correct_hits = 0       # Tổng số lượng kết quả ĐÚNG (problem_match == True)
        queries_with_hit = 0         # Số lượng query tìm được ít nhất 1 kết quả đúng
        queries_top1_correct = 0     # Số lượng query có Top 1 là kết quả đúng

        for item in data.get('queries', []):
            eval_data = item['evaluation'].get(evaluator, {})
            per_hit = eval_data.get('per_hit', [])
            
            # Lọc ra những kết quả (hit) đã thực sự được đánh giá (khác null)
            evaluated_hits = [hit for hit in per_hit if hit.get('problem_match') is not None]
            
            # Nếu query này chưa có hit nào được đánh giá, ta bỏ qua
            if not evaluated_hits:
                continue 
            
            total_queries += 1
            has_hit = False
            top1_correct = False

            # Duyệt qua các kết quả đã đánh giá của query này
            for hit in evaluated_hits:
                total_hits_evaluated += 1
                
                if hit.get('problem_match') is True:
                    total_correct_hits += 1
                    has_hit = True
                    
                    # Kiểm tra xem kết quả đúng này có phải là Top 1 không
                    if hit.get('rank') == 1:
                        top1_correct = True
            
            if has_hit:
                queries_with_hit += 1
            if top1_correct:
                queries_top1_correct += 1

        # Nếu chưa có dữ liệu đánh giá nào
        if total_queries == 0:
            print("-> Chưa có dữ liệu đánh giá.\n")
            continue

        # Tính toán các tỷ lệ (Tránh lỗi chia cho 0)
        precision = (total_correct_hits / total_hits_evaluated) * 100 if total_hits_evaluated > 0 else 0
        hit_rate = (queries_with_hit / total_queries) * 100 if total_queries > 0 else 0
        top_1_acc = (queries_top1_correct / total_queries) * 100 if total_queries > 0 else 0

        # In kết quả theo đúng format cậu yêu cầu
        print(f"1. Tỉ lệ Precision (Độ chính xác tổng thể): {precision:.2f}%")
        print(f"   -> Ý nghĩa: Cứ 100 kết quả trả về thì có {precision:.2f} kết quả là đúng.")
        
        print(f"\n2. Tỉ lệ Hit Rate (Khả năng tìm thấy): {hit_rate:.2f}%")
        print(f"   -> Ý nghĩa: Có {hit_rate:.2f}% số lần tìm kiếm tìm được ít nhất 1 Issue đúng.")
        
        print(f"\n3. Tỉ lệ Top-1 Accuracy (Độ chuẩn xác hạng 1): {top_1_acc:.2f}%")
        print(f"   -> Ý nghĩa: Có {top_1_acc:.2f}% trường hợp kết quả tốt nhất là kết quả đúng.\n")

if __name__ == "__main__":
    # Cậu thay đổi tên file này thành file đã chạy ra kết quả nhé
    # Ví dụ: 'rag_eval_batch_completed.json'
    FILE_PATH = 'D:\\Projects\\AITOPIA\\phase1\\find-similar-issues\\data\\719\\rag_eval_batch_ai.json' 
    calculate_metrics(FILE_PATH)