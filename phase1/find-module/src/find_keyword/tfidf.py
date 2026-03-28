import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_tfidf(input_file, output_file, top_n=50):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Không tìm thấy file {input_file}. Cậu kiểm tra lại nhé!")
        return

    main_modules = {"OMA", "SKMSAgent", "SEM", "SKPM"}
    
    # Gom tất cả comments của từng module thành 1 "văn bản" (document) duy nhất
    module_docs = {"OMA": [], "SKMSAgent": [], "SEM": [], "SKPM": [], "Others": []}

    for issue in data:
        module_type = issue.get("type", "")
        if module_type not in main_modules:
            module_type = "Others"
            
        comments = issue.get("comments", [])
        if comments:
            module_docs[module_type].extend(comments)

    # Chuyển dữ liệu thành danh sách 5 chuỗi lớn tương ứng với 5 nhóm module
    corpus = []
    module_names = []
    for mod, comments in module_docs.items():
        module_names.append(mod)
        # Chuyển tất cả về chữ thường
        corpus.append(" ".join(comments).lower())

    # Hàm tách từ (tokenizer) tuân theo chính xác yêu cầu của cậu
    def custom_tokenizer(text):
        tokens = re.split(r'[ \,]+', text)
        return [t for t in tokens if t.strip()]

    print("Đang chạy thuật toán TF-IDF và loại bỏ từ nhiễu...")
    
    # max_df=4: Bí quyết ở đây! Tính năng này sẽ tự động loại bỏ BẤT KỲ từ nào 
    # xuất hiện ở tất cả 5 nhóm module, hoạt động y hệt logic tớ viết thêm cho cậu ở Cách 1.
    vectorizer = TfidfVectorizer(tokenizer=custom_tokenizer, token_pattern=None, max_df=4)
    
    # Tính toán ma trận điểm TF-IDF
    tfidf_matrix = vectorizer.fit_transform(corpus)
    feature_names = vectorizer.get_feature_names_out()
    
    result = {}
    
    # Trích xuất top từ khóa cho từng module
    for i, mod in enumerate(module_names):
        # Lấy vector điểm của module hiện tại
        module_vector = tfidf_matrix[i].toarray()[0]
        
        # Sắp xếp các từ theo điểm TF-IDF giảm dần và lấy top_n
        top_indices = module_vector.argsort()[::-1][:top_n]
        
        result[mod] = {}
        for idx in top_indices:
            word = feature_names[idx]
            score = module_vector[idx]
            if score > 0: # Chỉ lấy những từ thực sự có mặt trong module này
                # Lưu điểm số làm tròn 4 chữ số thập phân
                result[mod][word] = round(score, 4)

    # Xuất ra file JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)
        
    print(f"Hoàn tất! Cậu mở file '{output_file}' để xem kết quả nhé.")

if __name__ == "__main__":
    extract_keywords_tfidf('D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list.json', 'keyword_tfidf_result.json', top_n=100)