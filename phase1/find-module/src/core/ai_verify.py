import json
import requests
import re
from pathlib import Path

OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:270m"

INPUT_FILE = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag_with_assignment.json")
OUTPUT_FILE = Path("D:\\Projects\\AITOPIA\\phase1\\find-module\\data\\719\\Defect_list_rag_with_assignment_ai.json")

# Tách thuật ngữ chung để đưa vào bối cảnh của mọi câu hỏi
TERMINOLOGY_CONTEXT = """
Terminology:
- Secure Element: Smart chip manages and stores information securely, isolated from the rest of the device (hardware isolation).
- SD (Security Domain): Trong chip Secure Element, nó được chia ra các phân vùng nhỏ, gọi là SD.
- Applet: Applet được chứa trong SD, nó có vai trò lưu trữ thông tin.
"""

# Tách riêng bối cảnh cho từng Module
MODULE_DESCRIPTIONS = {
    "OMA": "OMA (Open Mobile API): It is an AOSP (Android Open Source Project). It is a communication standard that allows android applications to access eSE.",
    "SKMSAgent": "Samsung eSE API (SKMSAgent - Samsung Key Management System Agent): Basically eSE SDK allows client application to communicate with eSE. Also eSE SDK act as proxy application between SKMS server and eSE. From now on, I will use the name SKMSAgent.",
    "SEM": "SEM (Secure Element Manage): Located behind SKMSAgent, it provides additional security features to ensure transactions to eSE are conducted correctly.",
    "SKPM": "SKPM (Samsung Key Provisioning Mamagement): A mechanism that allows key injection from the server to an application that needs it."
}

def clean_text(text):
    if not text:
        return ""
    return str(text).replace("\r", " ").replace("\n", " ").strip()

def evaluate_with_ollama(issue_text: str, module_name: str) -> bool:
    """
    Gọi Ollama API để đánh giá xem issue có thuộc về module_name hay không.
    Trả về True hoặc False.
    """
    module_desc = MODULE_DESCRIPTIONS.get(module_name, "")
    
    # Prompt được thiết kế tối giản, yêu cầu trả lời True/False rõ ràng cho mô hình nhỏ (270m)
    prompt = f"""You are an Android Secure Element Expert.
Read the Terminology and the Module Description carefully.

{TERMINOLOGY_CONTEXT}

Module Description to check:
{module_desc}

Issue Details:
{issue_text}

Task: Based on the Issue Details, does this issue belong to the module '{module_name}'? 
Answer exactly with one word: "true" if it belongs to this module, or "false" if it does not.
Answer:"""

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1 # Để nhiệt độ thấp giúp AI trả lời ổn định, bớt sáng tạo linh tinh
        }
    }

    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        result_text = response.json().get("response", "").strip().lower()
        
        # Parse kết quả để lấy True hoặc False
        if "true" in result_text:
            return True
        elif "false" in result_text:
            return False
        else:
            print(f"[Cảnh báo] AI trả lời không rõ ràng cho {module_name}: {result_text}")
            return False # Default là False nếu AI trả lời linh tinh
            
    except Exception as e:
        print(f"[Lỗi] Không thể kết nối tới Ollama: {e}")
        return False

def process_issues(input_file: str, output_file: str):
    print(f"Đang đọc dữ liệu từ {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        issues = json.load(f)

    for index, issue in enumerate(issues):
        issue_id = issue.get("id", f"Unknown-{index}")
        print(f"\n[{index + 1}/{len(issues)}] Đang xử lý Issue: {issue_id}")
        
        # Gộp các trường văn bản lại để tạo context cho AI
        search_text = clean_text(issue.get("search_text", ""))
        evidence_text = clean_text(issue.get("evidence_text", ""))
        raw_comments_list = issue.get("raw_comments", [])
        raw_comments = clean_text(" ".join([str(c) for c in raw_comments_list if c]))
        
        # Rút gọn text nếu quá dài để tránh vượt context window của model nhỏ
        issue_text = f"Title/Symptoms: {search_text}\nEvidence: {evidence_text}\nComments: {raw_comments}"
        issue_text = issue_text[:2000] 
        
        assignment_prediction = issue.get("assignment_prediction", {})
        top_2_candidates = assignment_prediction.get("top_2_candidates", [])
        
        predicted_module = "UNKNOWN"
        
        # Đánh giá tuần tự từng candidate từ cao xuống thấp
        for candidate in top_2_candidates:
            candidate_module = candidate.get("module")
            if not candidate_module or candidate_module not in MODULE_DESCRIPTIONS:
                continue
                
            print(f"  -> Hỏi AI về module: {candidate_module}...")
            is_match = evaluate_with_ollama(issue_text, candidate_module)
            
            if is_match:
                print(f"  => AI XÁC NHẬN: Issue thuộc về {candidate_module}. Bỏ qua các ứng viên sau.")
                predicted_module = candidate_module
                break # Tìm thấy True thì dừng luôn, không check module thứ 2 nữa
            else:
                print(f"  => AI TỪ CHỐI: Không thuộc về {candidate_module}.")
        
        # Cập nhật kết quả vào JSON
        issue["assignment_prediction_ai"] = {
            "predicted_module": predicted_module,
            "evaluated_candidates": [c.get("module") for c in top_2_candidates]
        }

    # Lưu file kết quả
    print(f"\nĐang lưu kết quả ra file: {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(issues, f, ensure_ascii=False, indent=2)
    print("Hoàn thành!")

if __name__ == "__main__":
    
    process_issues(INPUT_FILE, OUTPUT_FILE)