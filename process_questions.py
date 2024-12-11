# process_questions.py
import json
import re
import glob
from pathlib import Path

def parse_question_number(question_num):
    """Parse '1.1' into section(1) and question(1)"""
    section, number = map(int, question_num.split('.'))
    return section, number

def parse_questions(text):
    """Parse questions from text and return structured data"""
    sections = {}
    question_pattern = r"QUESTION (\d+\.\d+)\n\n(.*?)\n\n([A-D].*?)Right Answer: ([A-D])\n\n(.*?)(?=QUESTION|\Z)"
    option_pattern = r"([A-D])\. (.*?)(?=\n[A-D]\.|\n\nRight|$)"

    matches = re.finditer(question_pattern, text, re.DOTALL)

    for match in matches:
        question_num = match.group(1)
        section_num, q_num = parse_question_number(question_num)
        question_text = match.group(2).strip()
        options_text = match.group(3)
        correct_answer = match.group(4)
        explanation = match.group(5).strip()

        options = {}
        for opt_match in re.finditer(option_pattern, options_text, re.DOTALL):
            opt_letter = opt_match.group(1)
            opt_text = opt_match.group(2).strip()
            options[opt_letter] = opt_text

        question_data = {
            "question_number": q_num,
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "explanation": explanation
        }

        if section_num not in sections:
            sections[section_num] = []
        sections[section_num].append(question_data)

    result = [
        {
            "section_number": section,
            "questions": questions
        }
        for section, questions in sections.items()
    ]

    return sorted(result, key=lambda x: x["section_number"])

def find_matching_files(directory, prefix):
    """Find all files beginning with prefix in directory"""
    pattern = f"{directory}/{prefix}*.txt"
    return glob.glob(pattern)

def save_json(data, output_file):
    """Save data to JSON file with proper formatting"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Successfully saved to {output_file}")
    except Exception as e:
        print(f"Error saving JSON: {e}")

def process_question_file(input_file):
    """Process question file and return structured data"""
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_questions(content)
    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def main():
    directory = "."  # Current directory, modify as needed
    prefix = "ECS-HSE"  # File prefix to match

    matching_files = find_matching_files(directory, prefix)

    for input_file in matching_files:
        input_path = Path(input_file)
        output_file = input_path.stem + ".json"

        print(f"Processing {input_file}...")
        questions = process_question_file(input_file)
        if questions:
            save_json(questions, output_file)

if __name__ == "__main__":
    main()