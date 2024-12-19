import json
import random
import glob
import os
import sys
from colorama import init, Fore, Style

def get_script_dir():
    """Get absolute path to script directory"""
    return os.path.dirname(os.path.abspath(__file__))

def main():
    init()  # Initialize colorama
    # Set working directory to script location
    script_dir = get_script_dir()
    os.chdir(script_dir)

    # Build output path relative to script location
    output_dir = os.path.join(script_dir, '..\\tests' if os.name == 'nt' else '../tests')
    output_path = os.path.join(output_dir, 'ecs-practice-test.json')

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load JSON data with paths relative to script
    json_path = os.path.join(
        script_dir,
        '..\\question-bank\\full\\json' if os.name == 'nt' else '../question-bank/full/json',
        'ECS-HSE-Revision-Guide-24.json'
    )
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find data file at {json_path}")
        sys.exit(1)

    # Define requirements for each section (index, count)
    requirements = [
        (0, 6),  # Section 1: 6 questions
        (1, 4),  # Section 2: 4 questions
        (2, 3),  # Section 3: 3 questions
        (3, 4),  # Section 4: 4 questions
        (4, 3),  # Section 5: 3 questions
        (5, 9),  # Section 6: 9 questions
        (6, 5),  # Section 7: 5 questions
        (7, 4),  # Section 8: 4 questions
        (8, 3),  # Section 9: 3 questions
        (9, 6),  # Section 10: 6 questions
        (10, 3)  # Section 11: 3 questions
    ]

    print(f"\n{Fore.CYAN}Generating practice test...{Style.RESET_ALL}")
    print(f"\nLoading questions from: {json_path}\n")

    test_data = []
    total_questions = 0
    processed_sections = 0

    # Process each section
    for section_index, num_questions in requirements:
        try:
            # Get section data
            section_data = data[section_index]
            # Get random questions
            selected_questions = random.sample(section_data['questions'], num_questions)
            # Create new section with selected questions
            new_section = {
                'section_number': section_data['section_number'],
                'questions': selected_questions
            }
            test_data.append(new_section)
            processed_sections += 1
            total_questions += num_questions
            print(f"{Fore.GREEN}✓{Style.RESET_ALL} Section {section_index + 1}: {num_questions} questions selected")
        except (IndexError, KeyError) as e:
            print(f"{Fore.RED}✗{Style.RESET_ALL} Error in section {section_index + 1}: {e}")
            continue

    # Save to file with path relative to script
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    print(f"\n{Fore.GREEN}Practice test generated successfully:{Style.RESET_ALL}\n")
    print(f"- Processed sections: {processed_sections}")
    print(f"- Total questions: {total_questions}")
    print(f"- Output saved to: {output_path}\n")

if __name__ == "__main__":
    main()