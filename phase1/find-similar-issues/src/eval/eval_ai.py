import json
import requests

# Cấu hình Ollama
OLLAMA_API_URL = "http://localhost:11434/api/generate" # Thay đổi port nếu cần
MODEL_NAME = "gemma3:270m"

def ask_ai_if_similar(query_issue, retrieved_issue):
    
    prompt = f"""
Task: Compare two technical issues and determine if they describe the SAME root cause or technical problem.
Instruction: Answer ONLY "TRUE" if they are the same, or "FALSE" if they are different. Do not explain.

[ISSUE 1]
Title: {query_issue.get('search_text')}
Problem Description: {query_issue.get('evidence_text')}
Root Cause: {query_issue.get('root_cause')}

[ISSUE 2]
Title: {retrieved_issue.get('search_text')}
Problem Description: {retrieved_issue.get('evidence_text')}
Root Cause: {retrieved_issue.get('root_cause')}

Final Answer (TRUE/FALSE):"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.0,  # Ép model trả về kết quả nhất quán
            "num_predict": 5     # Giới hạn độ dài câu trả lời để tránh AI nói lan man
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload)
        response.raise_for_status()
        
        # Xử lý kết quả trả về
        raw_answer = response.json().get('response', '').strip().upper()
        
        # Trả về kiểu Boolean (True/False)
        # Nếu trong câu trả lời có chứa "TRUE" thì trả về True, ngược lại là False
        return "TRUE" in raw_answer
            
    except Exception as e:
        print(f"Error calling Ollama: {e}")
        return False

def process_evaluation(input_file, output_file):
    # Đọc dữ liệu từ file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Bắt đầu đánh giá với model {MODEL_NAME}...")

    for q_idx, item in enumerate(data['queries']):
        query_issue = item['query']['snapshot']
        retrieval_list = item['retrieval']
        
        # Tạo bản đồ dữ liệu retrieval để tra cứu nhanh thông tin issue tương ứng
        retrieval_map = {res['case_code']: res['snapshot'] for res in retrieval_list}
        
        # Duyệt qua danh sách đánh giá của AI
        ai_eval = item['evaluation']['ai']
        for hit in ai_eval['per_hit']:
            case_code = hit['case_code']
            retrieved_issue = retrieval_map.get(case_code)
            
            if retrieved_issue:
                print(f"Đang so sánh Query {q_idx} với {case_code}...", end=" ")
                is_match = ask_ai_if_similar(query_issue, retrieved_issue)
                hit['problem_match'] = is_match
                print(f"Kết quả: {is_match}")
        
        # Đánh dấu đã hoàn thành phần AI
        ai_eval['filled'] = True

    # Lưu kết quả
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nĐã hoàn thành! Kết quả lưu tại: {output_file}")

if __name__ == "__main__":
    INPUT_PATH = 'D:\\Projects\\AITOPIA\\phase1\\find-similar-issues\\data\\719\\rag_eval_batch.json'
    OUTPUT_PATH = 'D:\\Projects\\AITOPIA\\phase1\\find-similar-issues\\data\\719\\rag_eval_batch_ai.json'
    process_evaluation(INPUT_PATH, OUTPUT_PATH)