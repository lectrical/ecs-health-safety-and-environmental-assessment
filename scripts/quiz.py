import json
import random
import os
import shutil
import textwrap
import sys
import argparse
from colorama import init, Fore, Style

MIN_PASS_SCORE = 43

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.getcwd()

def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)

def find_valid_path(possible_paths):
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0]  # Default to first path

# Define base path
base_path = get_base_path()

def validate_paths():
    data_file = 'ECS-HSE-Revision-Guide-24.json'
    test_file = 'ecs-test.json'

    # First check if running as frozen executable
    if getattr(sys, 'frozen', False):
        bundled_data = get_resource_path(data_file)
        if os.path.exists(bundled_data):
            # If using bundled data, default test file to base path
            return ([bundled_data],
                   [os.path.join(base_path, test_file)])

    # Check if data file exists in root
    if os.path.exists(os.path.join(base_path, data_file)):
        return [os.path.join(base_path, data_file)], [os.path.join(base_path, test_file)]

    # Check in json-full directory
    if os.path.exists(os.path.join(base_path, 'json-full', data_file)):
        return [os.path.join(base_path, 'json-full', data_file)], [os.path.join(base_path, 'tests', test_file)]

    # Default paths as fallback
    return [
        os.path.join(base_path, 'json-full', data_file),
        os.path.join(base_path, '../json-full', data_file),
        os.path.join(base_path, data_file),
    ], [
        os.path.join(base_path, 'tests', test_file),
        os.path.join(base_path, '../tests', test_file),
        os.path.join(base_path, test_file),
    ]

DATA_PATHS, TEST_PATHS = validate_paths()

def find_data_file():
    print("\nBase path:", base_path)
    print("\nChecking paths:")
    print("="*50)

    # First check bundled path if frozen
    if getattr(sys, 'frozen', False):
        bundled_path = get_resource_path('ECS-HSE-Revision-Guide-24.json')
        if os.path.exists(bundled_path):
            print(f"[FOUND] {bundled_path} (bundled)")
            return bundled_path

    # Then check external paths
    for path in DATA_PATHS:
        exists = os.path.exists(path)
        status = "FOUND" if exists else "NOT FOUND"
        print(f"[{status}] {path}")

    found_path = find_valid_path(DATA_PATHS)
    if os.path.exists(found_path):
        return found_path

    raise FileNotFoundError("Could not find question data file")

def generate_test():
    try:
        data_path = find_data_file()
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print(Fore.RED + f"\nError: {e}" + Style.RESET_ALL)
        return []

    # Define requirements for each section (index, count)
    requirements = [
        (0, 6),   # Section 1: 6 questions
        (1, 4),   # Section 2: 4 questions
        (2, 3),   # Section 3: 3 questions
        (3, 4),   # Section 4: 4 questions
        (4, 3),   # Section 5: 3 questions
        (5, 9),   # Section 6: 9 questions
        (6, 5),   # Section 7: 5 questions
        (7, 4),   # Section 8: 4 questions
        (8, 3),   # Section 9: 3 questions
        (9, 6),   # Section 10: 6 questions
        (10, 3)   # Section 11: 3 questions
    ]

    # Create test data
    test_data = []
    for section_index, num_questions in requirements:
        try:
            section_data = data[section_index]
            selected_questions = random.sample(section_data['questions'], num_questions)
            new_section = {
                'section_number': section_data['section_number'],
                'questions': selected_questions
            }
            test_data.append(new_section)
        except (IndexError, KeyError) as e:
            print(f"Error processing section {section_index}: {e}")
            continue

    # Save generated test
    test_path = find_valid_path(TEST_PATHS)
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    # Return flattened questions
    questions = []
    for section in test_data:
        questions.extend(section['questions'])
    return questions

def load_questions():
    test_path = find_valid_path(TEST_PATHS)
    has_existing_test = os.path.exists(test_path)

    while True:
        print(Fore.GREEN + "\nSelect quiz mode:\n" + Style.RESET_ALL)
        print("1. Full test (all 327 questions from main database question bank)" + Style.RESET_ALL)
        print("2. Generate new 50-question practice test in official ECS quiz format" + Style.RESET_ALL)
        if has_existing_test:
            print("3. Reuse existing practice test" + Style.RESET_ALL)
            print(Fore.YELLOW + "\nNote on option 3: " + Style.RESET_ALL + "Question order is randomized each time but it's the same 50 questions.\n")
        else:
            print()
        max_choice = 3 if has_existing_test else 2
        choice = input(f"Enter choice (1-{max_choice}): " + Style.RESET_ALL)


        if choice == '1':
            # Load full question database
            with open(find_data_file(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Flatten all questions into single list
                questions = []
                for section in data:
                    questions.extend(section['questions'])
                return questions
        elif choice == '2':
            return generate_test()
        elif choice == '3' and os.path.exists(test_path):
            with open(test_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                questions = []
                for section in data:
                    questions.extend(section['questions'])
                return questions
        else:
            print(Fore.RED + "Please enter a valid choice" + Style.RESET_ALL)

def review_wrong_answers(wrong_answers):
    print(Fore.YELLOW + "\nReviewing incorrect answers:\n" + Style.RESET_ALL)
    print("="*50)

    for wrong in wrong_answers:
        print(f"\nQ{wrong['question_num']}: " + Fore.MAGENTA + f"{wrong['question']}\n" + Style.RESET_ALL)

        for key, value in sorted(wrong['options'].items()):
            if key == wrong['correct_answer']:
                print(Fore.GREEN + f" {key}: {value}" + Style.RESET_ALL)
            elif key == wrong['user_answer']:
                print(Fore.RED + f" {key}: {value}" + Style.RESET_ALL)
            else:
                print(f" {key}: {value}")

        print(f"\nYour answer: " + Fore.RED + f"{wrong['user_answer']}" + Style.RESET_ALL)
        print(f"Correct answer: " + Fore.GREEN + f"{wrong['correct_answer']}" + Style.RESET_ALL)

        if wrong['explanation']:
            print(f"\n{Fore.YELLOW}{create_box(wrong['explanation'])}{Style.RESET_ALL}")

        input("\nPress Enter for next question...")

def get_valid_answer():
    valid_answers = ['A', 'B', 'C', 'D']
    while True:
        answer = input("\nAnswer?: ").strip().upper()
        if answer in valid_answers:
            return answer
        print(Fore.RED + "\nInvalid input: " + answer + Fore.YELLOW + " - Please enter a, b, c, or d." + Style.RESET_ALL)

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

# Test type constants
class TestType:
    PRACTICE = "practice"
    FULL = "full"

# Test configuration
TEST_CONFIG = {
    TestType.PRACTICE: {
        "total_questions": 50,
        "pass_score": 43,  # 86%
        "name": "Practice Test"
    },
    TestType.FULL: {
        "total_questions": 327,
        "pass_score": 282,  # 86%
        "name": "Full Test"
    }
}

def get_test_config(total_questions):
    return TEST_CONFIG[TestType.FULL] if total_questions == 327 else TEST_CONFIG[TestType.PRACTICE]

def create_practice_score_table(score, wrong_answers, total_questions=50, min_pass_score=43):
    table = [
        "┌─────────────┬──────────┬──────────┐",
        "│   Practice  │  Score   │    %     │",
        "├─────────────┼──────────┼──────────┤",
       f"│   Correct   │{Fore.GREEN}    {str(score).rjust(2)}    {Style.RESET_ALL}│{Fore.GREEN}   {str(int(score/total_questions*100)).rjust(3)}%   {Style.RESET_ALL}│",
       f"│    Wrong    │{Fore.RED}    {str(len(wrong_answers)).rjust(2)}    {Style.RESET_ALL}│{Fore.RED}   {str(int(len(wrong_answers)/total_questions*100)).rjust(3)}%   {Style.RESET_ALL}│",
        "├─────────────┼──────────┼──────────┤",
       f"│   Target    │{Fore.GREEN}   {str(min_pass_score).rjust(2)}{Style.RESET_ALL}/{str(total_questions).rjust(2)}  │{Fore.GREEN}{str(int(min_pass_score/total_questions*100)).rjust(3)}%{Style.RESET_ALL}/100% │",
        "└─────────────┴──────────┴──────────┘"
    ]
    return '\n'.join(table)

def create_full_score_table(score, wrong_answers, total_questions=327, min_pass_score=282):
    table = [
        "┌─────────────┬───────────┬──────────┐",
        "│  Full Test  │   Score   │    %     │",
        "├─────────────┼───────────┼──────────┤",
       f"│   Correct   │{Fore.GREEN}    {str(score).rjust(3)}    {Style.RESET_ALL}│{Fore.GREEN}   {str(int(score/total_questions*100)).rjust(3)}%   {Style.RESET_ALL}│",
       f"│    Wrong    │{Fore.RED}    {str(len(wrong_answers)).rjust(3)}    {Style.RESET_ALL}│{Fore.RED}   {str(int(len(wrong_answers)/total_questions*100)).rjust(3)}%   {Style.RESET_ALL}│",
        "├─────────────┼───────────┼──────────┤",
       f"│   Target    │{Fore.GREEN}  {str(min_pass_score).rjust(3)}{Style.RESET_ALL}/{str(total_questions)}  │{Fore.GREEN}{str(int(min_pass_score/total_questions*100)).rjust(3)}%{Style.RESET_ALL}/100% │",
        "└─────────────┴───────────┴──────────┘"
    ]
    return '\n'.join(table)

def create_score_table(score, wrong_answers, total_questions):
    config = get_test_config(total_questions)
    if total_questions == TEST_CONFIG[TestType.FULL]["total_questions"]:
        return create_full_score_table(score, wrong_answers,
                                     total_questions=config["total_questions"],
                                     min_pass_score=config["pass_score"])
    else:
        return create_practice_score_table(score, wrong_answers,
                                         total_questions=config["total_questions"],
                                         min_pass_score=config["pass_score"])

def quiz_user(questions):
    init()  # Initialize colorama
    score = 0
    wrong_answers = []
    total_questions = len(questions)
    random.shuffle(questions)

    for i, question in enumerate(questions, 1):
        clear_terminal()
        print("\n" + "="*50)
        print(f"\nQ{i}:" + Fore.MAGENTA + f" {question['question']}\n" + Style.RESET_ALL)

        options = question.get('options', {})
        if options:
            for key, value in sorted(options.items()):
                print(f" {key}: {value}")

        answer = get_valid_answer()
        correct_answer = question.get('correct_answer', '').upper()

        if answer == correct_answer:
            print(Fore.GREEN + "\n✓ Correct!" + Style.RESET_ALL)
            score += 1
        else:
            print(f"\n{Fore.RED} ✗ Incorrect{Style.RESET_ALL} - The correct answer was: {Fore.GREEN}{correct_answer}{Style.RESET_ALL}")
            wrong_answers.append({
                'question_num': i,
                'question': question['question'],
                'options': options,
                'user_answer': answer,
                'correct_answer': correct_answer,
                'explanation': question.get('explanation', '')
            })

        explanation = question.get('explanation', '')
        if explanation:
            print(f"\n{Fore.YELLOW}{create_box(explanation)}{Style.RESET_ALL}")

        print(f"\n{create_score_table(score, wrong_answers, len(questions))}")
        input("\nPress Enter to continue...")

    print("\n" + "="*50)
    print(f"\nFinal Score: {score} out of {len(questions)} ({(score/len(questions)*100):.1f}%)")

    if wrong_answers:
        review_wrong_answers(wrong_answers)

    input("\nPress Enter to exit...")

def get_terminal_width():
    try:
        width = shutil.get_terminal_size().columns
        return min(width - 4, 120)  # Cap at 120 chars, leave margin
    except:
        return 76  # Fallback width

def create_box(text):
    width = get_terminal_width()
    wrapper = textwrap.TextWrapper(
        width=width-4,  # Account for borders
        break_long_words=True,
        replace_whitespace=True
    )
    lines = wrapper.wrap(text)

    # Create box
    box = [
        f"╔{'═' * (width-2)}╗",
        *[f"║ {line:<{width-4}} ║" for line in lines],
        f"╚{'═' * (width-2)}╝"
    ]
    return '\n'.join(box)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--full-test', action='store_true', help='Run full test using all questions')
    return parser.parse_args()

def run_full_test(questions):
    config = get_test_config(len(questions))
    score = 0
    total = len(questions)
    print(f"\nStarting full test with {total} questions")
    print("="*50)

    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}/{total}")
        # Format question with letter options
        options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q['options'])]
        print(textwrap.fill(q['question'], width=80))
        print("\n".join(options))

        answer = input("\nYour answer (A-D): ").upper()
        if answer == chr(65 + q['correct']):
            score += 1
            print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Incorrect. The correct answer was {chr(65 + q['correct'])}{Style.RESET_ALL}")

    percentage = (score/total) * 100
    print(f"\nFinal Score: {score}/{total} ({percentage:.1f}%)")
    print(f"{'PASS' if percentage >= config['pass_score'] else 'FAIL'}")
    return score

if __name__ == "__main__":
    try:
        init()  # Initialize colorama
        args = parse_args()

        with open(find_data_file()) as f:
            all_questions = json.load(f)

        if args.full_test:
            run_full_test(all_questions)
        else:
            questions = load_questions()
            quiz_user(questions)
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nQuiz terminated by user. Goodbye!" + Style.RESET_ALL)
    finally:
        # Reset terminal state
        print(Style.RESET_ALL)
        if os.name == 'nt':
            os.system('color')  # Reset colors on Windows