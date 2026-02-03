import glob
import json
import os

def parse_csv(filepath):
    questions = []
    current_q = {"question": "", "options": []}
    
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        lines = [l.strip() for l in f.readlines()]
        
    for line in lines:
        if not line:
            if current_q["question"]:
                questions.append(current_q)
                current_q = {"question": "", "options": []}
            continue
            
        if not current_q["question"]:
            current_q["question"] = line
        else:
            # Parse Option: "Text,Boolean"
            # Split only on the last comma in case text contains commas
            parts = line.rsplit(',', 1)
            if len(parts) == 2:
                opt_text = parts[0].strip()
                # Translate True/False to Arabic
                if opt_text == "True":
                    opt_text = "صح"
                elif opt_text == "False":
                    opt_text = "خطأ"
                
                is_correct = parts[1].strip().lower() == 'true'
                current_q["options"].append({"text": opt_text, "correct": is_correct})
    
    # Add last one if exists
    if current_q["question"]:
        questions.append(current_q)
        
    return questions

def main():
    csv_files = glob.glob("*.csv")
    all_data = {}
    
    for f in csv_files:
        # Use filename without extension as Quiz Name
        quiz_name = os.path.splitext(os.path.basename(f))[0]
        print(f"Processing: {quiz_name}")
        try:
            questions = parse_csv(f)
            if questions:
                all_data[quiz_name] = questions
        except Exception as e:
            print(f"Error parsing {f}: {e}")
            
    # Output to JS
    js_content = f"const QUIZ_DATA = {json.dumps(all_data, ensure_ascii=False, indent=2)};"
    with open("quiz_data.js", "w", encoding="utf-8") as f:
        f.write(js_content)
        
    print(f"Done! Generated quiz_data.js with {len(all_data)} quizzes.")

if __name__ == "__main__":
    main()
