import glob
import json
import os
import re

def parse_csv(filepath):
    """Parse CSV and return (subtitle, questions) tuple."""
    questions = []
    subtitle = ""
    current_q = {"question": "", "options": []}
    pending_comment = ""  # Comment for the next option
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = [l.strip() for l in f.readlines()]
        
    for line in lines:
        # Handle directives
        if line.startswith("# SUBTITLE:"):
            subtitle = line[11:].strip()
            continue
        if line.startswith("# COMMENT:"):
            pending_comment = line[10:].strip()
            continue
            
        if not line:
            if current_q["question"]:
                questions.append(current_q)
                current_q = {"question": "", "options": []}
                pending_comment = ""
            continue
            
        if not current_q["question"]:
            current_q["question"] = line
        else:
            # Parse Option: "Text,Boolean"
            parts = line.rsplit(',', 1)
            if len(parts) == 2:
                opt_text = parts[0].strip()
                # Translate True/False to Arabic
                if opt_text == "True":
                    opt_text = "صح"
                elif opt_text == "False":
                    opt_text = "خطأ"
                
                is_correct = parts[1].strip().lower() == 'true'
                opt = {"text": opt_text, "correct": is_correct}
                
                # Add comment to this option if pending
                if pending_comment:
                    opt["comment"] = pending_comment
                    pending_comment = ""
                    
                current_q["options"].append(opt)
    
    # Add last one if exists
    if current_q["question"]:
        questions.append(current_q)
        
    return subtitle, questions

def load_ai_quizzes():
    """Load AI quizzes from Gemini_quiz.js"""
    if not os.path.exists("Gemini_quiz.js"):
        return {}
        
    try:
        with open("Gemini_quiz.js", "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract JSON object part: "const QUIZ_DATA = { ... };"
        # We find the first { and the last }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            json_str = content[start:end+1]
            # Try to handle potential trailing commas which valid JSON doesn't support but JS does
            # Simple regex to remove trailing commas before } or ]
            json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
            
            data = json.loads(json_str)
            
            # Tag as AI
            for key in data:
                data[key]["isAI"] = True
                
            return data
    except Exception as e:
        print(f"Error loading Gemini_quiz.js: {e}")
        return {}
        
    return {}

def main():
    all_data = {}
    
    # 1. Load CSV quizzes (Standard)
    csv_files = sorted(glob.glob("*.csv"))
    for f in csv_files:
        quiz_name = os.path.splitext(os.path.basename(f))[0]
        print(f"Processing CSV: {quiz_name}")
        try:
            subtitle, questions = parse_csv(f)
            if questions:
                all_data[quiz_name] = {
                    "subtitle": subtitle,
                    "questions": questions,
                    "isAI": False
                }
        except Exception as e:
            print(f"Error parsing {f}: {e}")

    # 2. Load AI quizzes and merge
    ai_data = load_ai_quizzes()
    if ai_data:
        print(f"Loaded {len(ai_data)} AI quizzes.")
        all_data.update(ai_data)
            
    # Output to JS
    js_content = f"const QUIZ_DATA = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
    with open("quiz_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"Done! Generated quiz_data.js with {len(all_data)} quizzes.")

if __name__ == "__main__":
    main()
