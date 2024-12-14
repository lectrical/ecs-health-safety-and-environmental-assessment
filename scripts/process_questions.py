import json
import re
import glob
import sys
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

def find_matching_files(directory):
    pattern = f"{directory}/*.txt"
    print(f"Searching for files with pattern: {pattern}")
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
    if len(sys.argv) < 2:
        print("Usage: python process_questions.py <mode> [input_directory]")
        sys.exit(1)

    mode = sys.argv[1]
    input_directory = sys.argv[2] if len(sys.argv) > 2 else "../txt-full"

    # Check if the input directory exists
    if not Path(input_directory).is_dir():
        print(f"Error: The directory '{input_directory}' does not exist.")
        sys.exit(1)

    matching_files = find_matching_files(input_directory)
    print(f"Found {len(matching_files)} matching files.")

    for input_file in matching_files:
        input_path = Path(input_file)
        print(f"Processing {input_file}...")
        sections = process_question_file(input_file)
        if sections:
            if mode == 'sections':
                output_directory = "../json-sections"
                Path(output_directory).mkdir(parents=True, exist_ok=True)
                for section in sections:
                    section_number = f"{int(section['section_number']):02d}"
                    output_file = Path(output_directory) / f"{input_path.stem}-{section_number}.json"
                    print(f"Saving section {section_number} to {output_file}")
                    save_json(section, output_file)
            else:
                output_directory = "../json-full"
                Path(output_directory).mkdir(parents=True, exist_ok=True)
                output_file = Path(output_directory) / f"{input_path.stem}.json"
                print(f"Saving full data to {output_file}")
                save_json(sections, output_file)

if __name__ == "__main__":
    main()