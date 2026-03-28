import json
import re
from collections import Counter

def extract_keywords_with_issue_count(input_file, output_file, top_n=50):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Không tìm thấy file {input_file}. Cậu kiểm tra lại đường dẫn nhé!")
        return

    main_modules = {"OMA", "SKMSAgent", "SEM", "SKPM"}
    
    # Bộ đếm tổng số lần xuất hiện của từ (Term Frequency)
    module_tf = {mod: Counter() for mod in main_modules}
    module_tf["Others"] = Counter()
    
    # Bộ đếm số lượng issue (file) chứa từ đó (Document Frequency)
    module_df = {mod: Counter() for mod in main_modules}
    module_df["Others"] = Counter()

    for issue in data:
        module_type = issue.get("type", "")
        if module_type not in main_modules:
            module_type = "Others"
            
        comments = issue.get("comments", []) 
        if not comments:
            continue
            
        full_comment_text = " ".join(comments).lower()
        full_comment_text = full_comment_text + " " + issue.get("title", "").lower()
        tokens = re.split(r'[ \\]+', full_comment_text)
        tokens = [token for token in tokens if token.strip()]
        
        # 1. Cập nhật tổng số lần xuất hiện
        module_tf[module_type].update(tokens)
        
        # 2. Cập nhật số lượng issue chứa từ này 
        # (Dùng set để mỗi từ chỉ được tính 1 lần cho 1 issue hiện tại)
        unique_tokens_in_issue = set(tokens)
        module_df[module_type].update(unique_tokens_in_issue)

    # Xóa các từ xuất hiện ở cả 4 module chính
    print("Đang phân tích để loại bỏ các từ chung...")
    words_oma = set(module_tf["OMA"].keys())
    words_skms = set(module_tf["SKMSAgent"].keys())
    words_sem = set(module_tf["SEM"].keys())
    words_skpm = set(module_tf["SKPM"].keys())
    
    common_words = words_oma.intersection(words_skms, words_sem, words_skpm)
    print(f"Đã tìm thấy {len(common_words)} từ xuất hiện chung ở cả 4 module. Tiến hành xóa...")
    
    for mod in module_tf.keys():
        for word in common_words:
            # Xóa khỏi cả 2 bộ đếm
            if word in module_tf[mod]:
                del module_tf[mod][word]
            if word in module_df[mod]:
                del module_df[mod][word]

    # Tổng hợp kết quả
    result = {}
    for mod, counter in module_tf.items():
        result[mod] = {}
        # Lấy top_n từ dựa trên tổng số lần xuất hiện (most_common)
        for word, total_freq in counter.most_common(top_n):
            issue_count = module_df[mod][word]
            # Lưu thành cấu trúc dictionary có chứa cả 2 thông số
            result[mod][word] = {
                "total_occurrences": total_freq,
                "issue_count": issue_count
            }

    # Xuất ra file JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"Hoàn tất! Cậu mở file '{output_file}' để xem kết quả nhé.")

if __name__ == "__main__":
    extract_keywords_with_issue_count('D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list.json', 'keyword_frequency_result.json', top_n=200)