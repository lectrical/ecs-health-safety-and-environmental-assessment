import json
import os
import sys
from colorama import init, Fore, Style

def get_script_dir():
    """Get absolute path to script directory"""
    return os.path.dirname(os.path.abspath(__file__))

def convert_json_to_text():
    init()  # Initialize colorama
    script_dir = get_script_dir()
    os.chdir(script_dir)

    # Build paths relative to script location
    json_path = os.path.join(script_dir, '..\\tests' if os.name == 'nt' else '../tests', 'ecs-practice-test.json')
    text_path = os.path.join(script_dir, '..\\tests' if os.name == 'nt' else '../tests', 'ecs-practice-test.txt')

    print(f"\n{Fore.CYAN}Converting JSON test to text format...{Style.RESET_ALL}")
    print(f"\nLoading from: {json_path}\n")

    try:
        with open(json_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)

        total_sections = len(data)
        total_questions = 0
        text_output = ""

        for section_num, section in enumerate(data, 1):
            questions = section.get('questions', [])
            total_questions += len(questions)
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Processing Section {section_num}: {len(questions)} questions")

            section_number = section.get('section_number', 'Unknown Section')
            section_title = section.get('title', '')
            text_output += f"Section {section_number}"
            if section_title:
                text_output += f": {section_title}"
            text_output += "\n" + "=" * 50 + "\n\n"

            for idx, question in enumerate(questions, 1):
                question_number = question.get('question_number', 'Unknown')
                question_text = question.get('question', 'No question text provided.')
                text_output += f"Q{idx} (Question {question_number}): {question_text}\n\n"

                # Handle options if present
                options = question.get('options', {})
                if options:
                    for key, value in options.items():
                        text_output += f"- {key}: {value}\n"

                # Handle the answer
                answer = question.get('correct_answer') or question.get('answer', 'No answer provided.')
                text_output += f"\nAnswer: {answer}\n\n"

                # Include explanation if available
                explanation = question.get('explanation', '')
                if explanation:
                    text_output += f"Explanation: {explanation}\n"

                text_output += "\n"

            text_output += "\n"

        # Ensure output directory exists
        os.makedirs(os.path.dirname(text_path), exist_ok=True)

        with open(text_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text_output)

        print(f"\n{Fore.GREEN}Conversion completed successfully:{Style.RESET_ALL}\n")
        print(f"- Sections processed: {total_sections}")
        print(f"- Questions converted: {total_questions}")
        print(f"- Output saved to: {text_path}\n")

    except FileNotFoundError:
        print(f"{Fore.RED}Error: Could not find input file at {json_path}{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        print(f"{Fore.RED}Error processing file: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == "__main__":
    convert_json_to_text()