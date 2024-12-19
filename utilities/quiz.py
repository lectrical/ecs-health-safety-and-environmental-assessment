import json
import random
import os
import shutil
import textwrap
import sys
import argparse
from colorama import init, Fore, Style
from datetime import datetime

# Constants


class TestType:
    PRACTICE = "practice"
    FULL = "full"


TEST_CONFIG = {
    TestType.PRACTICE: {
        "total_questions": 50,
        "pass_score": 43,  # 86%
        "name": "Practice Test",
    },
    TestType.FULL: {
        "total_questions": 327,
        "pass_score": 282,  # 86%
        "name": "Full Test",
    },
}


def get_script_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.getcwd()


def get_resource_path(relative_path):
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.getcwd()
    return os.path.join(base_path, relative_path)


def find_valid_path(possible_paths):
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return possible_paths[0]


# Define base path
base_path = get_base_path()


def convert_path(path):
    return path.replace("/", "\\") if os.name == "nt" else path


def get_executable_dir():
    if getattr(sys, "frozen", False):
        path = os.path.dirname(sys.executable)
    else:
        path = os.path.dirname(__file__)
    return path


def resolve_path(file_name: str, base_dir: str = None, create_dirs: bool = False) -> str:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.basename(script_dir)
    exe_dir = os.path.dirname(sys.executable if getattr(
        sys, "frozen", False) else script_dir)
    exe_parent_dir = os.path.basename(exe_dir)

    paths = []

    if base_dir:
        if parent_dir == "utilities":
            paths.append(os.path.join(script_dir, "..", base_dir, file_name))
        elif parent_dir == "ecs-health-safety-and-environmental-assessment":
            paths.append(os.path.join(script_dir, base_dir, file_name))
        elif exe_parent_dir == "ecs-health-safety-and-environmental-assessment":
            paths.append(os.path.join(exe_dir, base_dir, file_name))

    if getattr(sys, "frozen", False):
        paths.append(os.path.join(exe_dir, file_name))

    paths.extend([
        os.path.join(os.getcwd(), file_name),
        os.path.join(os.getcwd(), base_dir, file_name) if base_dir else None,
        os.path.join(os.getcwd(), "..", base_dir,
                     file_name) if base_dir else None
    ])

    paths = [p for p in paths if p]
    resolved_path = next((p for p in paths if os.path.exists(p)), paths[0])
    resolved_path = resolved_path.replace(
        "/", "\\") if os.name == "nt" else resolved_path

    if create_dirs:
        os.makedirs(os.path.dirname(resolved_path), exist_ok=True)

    return resolved_path


def get_quiz_file_path(file_name, create_dirs=True):
    return resolve_path(file_name, "tests", create_dirs)


def get_prioritized_paths(script_dir, base_dir, file_name):
    return [
        resolve_path(file_name, base_dir),
        resolve_path(file_name, base_dir, create_dirs=True)
    ]


def validate_paths():
    script_dir = get_script_dir()
    data_file = "ECS-HSE-Revision-Guide-24.json"
    test_file = "ecs-practice-test.json"

    paths = {
        "json_dir": convert_path(os.path.join("question-bank", "full", "json")),
        "tests_dir": convert_path("tests"),
    }

    data_paths = get_prioritized_paths(
        script_dir, paths["json_dir"], data_file)
    test_paths = get_prioritized_paths(
        script_dir, paths["tests_dir"], test_file)

    return data_paths, test_paths


DATA_PATHS, TEST_PATHS = validate_paths()


def find_data_file() -> str:
    if getattr(sys, "frozen", False):
        bundled_path = convert_path(
            get_resource_path("ECS-HSE-Revision-Guide-24.json"))
        if os.path.exists(bundled_path):
            return bundled_path

    found_path = find_valid_path(DATA_PATHS)
    if os.path.exists(found_path):
        return convert_path(found_path)

    raise FileNotFoundError(
        "Quiz data file not found. Checked paths:\n"
        + "\n".join(f"- {convert_path(path)}" for path in DATA_PATHS)
    )


def generate_test():
    try:
        data_path = find_data_file()
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as e:
        print(Fore.RED + f"\nError: {e}" + Style.RESET_ALL)
        return []

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
        (10, 3),  # Section 11: 3 questions
    ]

    test_data = []
    for section_index, num_questions in requirements:
        try:
            section_data = data[section_index]
            selected_questions = random.sample(
                section_data["questions"], num_questions)
            new_section = {
                "section_number": section_data["section_number"],
                "questions": selected_questions,
            }
            test_data.append(new_section)
        except (IndexError, KeyError) as e:
            print(f"Error processing section {section_index}: {e}")
            continue

    test_path = find_valid_path(TEST_PATHS)
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    with open(test_path, "w", encoding="utf-8") as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

    questions = []
    for section in test_data:
        questions.extend(section["questions"])
    return questions


def load_questions():
    test_path = find_valid_path(TEST_PATHS)
    has_existing_test = os.path.exists(test_path)

    while True:
        print(Fore.GREEN + "\nSelect quiz mode:\n" + Style.RESET_ALL)
        print(
            "1. Full test (all 327 questions from main database question bank)"
            + Style.RESET_ALL
        )
        print(
            "2. Generate new 50-question practice test in official ECS quiz format"
            + Style.RESET_ALL
        )
        if has_existing_test:
            print("3. Reuse existing practice test" + Style.RESET_ALL)
            print(
                Fore.YELLOW
                + "\nNote on option 3: "
                + Style.RESET_ALL
                + "Question order is randomized each time but it's the same 50 questions.\n"
            )
        else:
            print()
        max_choice = 3 if has_existing_test else 2
        choice = input(f"Enter choice (1-{max_choice}): " + Style.RESET_ALL)

        if choice == "1":
            with open(find_data_file(), "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = []
                for section in data:
                    questions.extend(section["questions"])
                return questions
        elif choice == "2":
            return generate_test()
        elif choice == "3" and os.path.exists(test_path):
            with open(test_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                questions = []
                for section in data:
                    questions.extend(section["questions"])
                return questions
        else:
            print(Fore.RED + "Please enter a valid choice" + Style.RESET_ALL)


def review_wrong_answers(wrong_answers):
    print(Fore.YELLOW + "\nReviewing incorrect answers:\n" + Style.RESET_ALL)
    print("=" * 80)

    for wrong in wrong_answers:
        print(
            f"\nQ{wrong['question_num']}: "
            + Fore.MAGENTA
            + f"{wrong['question']}\n"
            + Style.RESET_ALL
        )

        for key, value in sorted(wrong["options"].items()):
            if key == wrong["correct_answer"]:
                print(Fore.GREEN + f" {key}: {value}" + Style.RESET_ALL)
            elif key == wrong["user_answer"]:
                print(Fore.RED + f" {key}: {value}" + Style.RESET_ALL)
            else:
                print(f" {key}: {value}")

        print(
            f"\nYour answer: " + Fore.RED +
            f"{wrong['user_answer']}" + Style.RESET_ALL
        )
        print(
            f"Correct answer: "
            + Fore.GREEN
            + f"{wrong['correct_answer']}"
            + Style.RESET_ALL
        )

        if wrong["explanation"]:
            print(
                f"\n{Fore.YELLOW}{create_box(wrong['explanation'])}{Style.RESET_ALL}")

        input("\nPress Enter for next question...")


def get_valid_answer():
    valid_answers = ["A", "B", "C", "D"]
    while True:
        answer = input("\nAnswer?: ").strip().upper()
        if answer in valid_answers:
            return answer
        print(
            Fore.RED
            + "\nInvalid input: "
            + answer
            + Fore.YELLOW
            + " - Please enter a, b, c, or d."
            + Style.RESET_ALL
        )


def clear_terminal():
    os.system("cls" if os.name == "nt" else "clear")


def get_test_config(total_questions):
    return (
        TEST_CONFIG[TestType.FULL]
        if total_questions == 327
        else TEST_CONFIG[TestType.PRACTICE]
    )


def create_score_table(score, wrong_answers, current_index, total_questions, questions_answered):
    test_type = "full" if total_questions == 327 else "practice"
    config = TEST_CONFIG[TestType.FULL if test_type ==
                         "full" else TestType.PRACTICE]

    left_width = 13
    score_width = len(str(total_questions)) * 2 + 3
    pct_width = 10

    progress_pct = (questions_answered / total_questions) * 100
    correct_pct = (score / total_questions) * 100
    wrong_pct = ((questions_answered - score) / total_questions) * 100
    projected_score = int((score / questions_answered) *
                          total_questions) if questions_answered > 0 else 0

    title = "Full Test" if test_type == "full" else "Practice"

    table = [
        f"┌{'─' * left_width}┬{'─' * score_width}┬{'─' * pct_width}┐",
        f"│ {title:<{left_width-2}} │{' Score ':^{score_width}}│{'   %  ':^{pct_width}}│",
        f"├{'─' * left_width}┼{'─' * score_width}┼{'─' * pct_width}┤",
        f"│ Progress    │{
            f'{questions_answered}/{total_questions}':^{score_width}}│{progress_pct:>7.1f}%  │",
        f"│ Correct     │{Fore.GREEN}{f'{score}/{total_questions}':^{score_width}}{
            Style.RESET_ALL}│{Fore.GREEN}{correct_pct:>7.1f}%  {Style.RESET_ALL}│",
        f"│ Wrong       │{Fore.RED}{f'{questions_answered - score}/{total_questions}':^{
            score_width}}{Style.RESET_ALL}│{Fore.RED}{wrong_pct:>7.1f}%  {Style.RESET_ALL}│",
        f"├{'─' * left_width}┼{'─' * score_width}┼{'─' * pct_width}┤",
        f"│ Projected   │{Fore.YELLOW}{f'{projected_score}/{total_questions}':^{score_width}}{
            Style.RESET_ALL}│{Fore.YELLOW}{(projected_score/total_questions*100):>7.1f}%  {Style.RESET_ALL}│",
        f"│ Target      │{Fore.GREEN}{f'{config["pass_score"]}/{total_questions}':^{score_width}}{
            Style.RESET_ALL}│{Fore.GREEN}{(config["pass_score"]/total_questions*100):>7.1f}%  {Style.RESET_ALL}│",
        f"└{'─' * left_width}┴{'─' * score_width}┴{'─' * pct_width}┘"
    ]

    return "\n".join(table)


def quiz_user(questions, progress=None):
    progress = progress or QuizProgress()
    total_questions = len(questions)
    wrong_answers = []

    try:
        for i, question in enumerate(questions[progress.current_index:], progress.current_index + 1):
            clear_terminal()
            print(
                f"\nQ{i}:" + Fore.MAGENTA +
                f" {question['question']}\n" + Style.RESET_ALL
            )

            options = question.get("options", {})
            if options:
                for key, value in sorted(options.items()):
                    print(f" {key}: {value}")

            answer = get_valid_answer()
            correct_answer = question.get("correct_answer", "").upper()

            if answer == correct_answer:
                progress.score += 1
                print(Fore.GREEN + "\n✓ Correct!" + Style.RESET_ALL)
            else:
                wrong_answer = {
                    "question_num": i,
                    "question": question["question"],
                    "options": question.get("options", {}),
                    "user_answer": answer,
                    "correct_answer": correct_answer,
                    "explanation": question.get("explanation", "")
                }
                progress.wrong_answers.append(wrong_answer)
                print(f"\n{Fore.RED} ✗ Incorrect{Style.RESET_ALL}")

            progress.current_index = i
            progress.questions_answered += 1  # Increment answered count
            progress.answers.append(
                {"q": i, "a": answer, "correct": answer == correct_answer})
            progress.save()

            explanation = question.get("explanation", "")
            if explanation:
                print(
                    f"\n{Fore.YELLOW}{create_box(explanation)}{Style.RESET_ALL}")

            print(
                f"\n{create_score_table(progress.score, progress.wrong_answers, progress.current_index, len(questions), progress.questions_answered)}")
            input("\nPress Enter to continue...")

        QuizProgress.clear()

        return progress.score, progress.wrong_answers

    except KeyboardInterrupt:
        progress.save()
        print(Fore.YELLOW + "\n\nProgress saved. Resume later." + Style.RESET_ALL)
        sys.exit(0)


def get_terminal_width():
    try:
        width = shutil.get_terminal_size().columns
        return min(width - 4, 120)
    except:
        return 76


def create_box(text):
    width = get_terminal_width()
    wrapper = textwrap.TextWrapper(
        width=width - 4,
        break_long_words=True,
        replace_whitespace=True,
    )
    lines = wrapper.wrap(text)

    # Create box
    box = [
        f"╔{'═' * (width-2)}╗",
        *[f"║ {line:<{width-4}} ║" for line in lines],
        f"╚{'═' * (width-2)}╝",
    ]
    return "\n".join(box)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--full-test", action="store_true", help="Run full test using all questions"
    )
    return parser.parse_args()


def run_full_test(questions):
    config = get_test_config(len(questions))
    score = 0
    total = len(questions)
    print(f"\nStarting full test with {total} questions")
    print("=" * 80)

    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i}/{total}")
        options = [f"{chr(65+i)}. {opt}" for i, opt in enumerate(q["options"])]
        print(textwrap.fill(q["question"], width=80))
        print("\n".join(options))

        answer = input("\nYour answer (A-D): ").upper()
        if answer == chr(65 + q["correct"]):
            score += 1
            print(f"{Fore.GREEN}Correct!{Style.RESET_ALL}")
        else:
            print(
                f"{Fore.RED}Incorrect. The correct answer was {
                    chr(65 + q['correct'])}{Style.RESET_ALL}"
            )

    percentage = (score / total) * 100
    print(f"\nFinal Score: {score}/{total} ({percentage:.1f}%)")
    print(f"{'PASS' if percentage >= config['pass_score'] else 'FAIL'}")
    return score


def set_working_directory():
    try:
        script_dir = get_script_dir()
        os.chdir(script_dir)
        return script_dir
    except Exception as e:
        print(f"Error setting working directory: {e}")
        sys.exit(1)


class QuizProgress:
    @staticmethod
    def get_save_path():
        return resolve_path("quiz_progress.json", "tests", create_dirs=True)

    def __init__(self, quiz_type):
        if quiz_type not in [TestType.FULL, TestType.PRACTICE]:
            raise ValueError(f"Invalid quiz type: {quiz_type}")
        self.quiz_type = quiz_type
        self.current_index = 0
        self.questions_answered = 0
        self.answers = []
        self.score = 0
        self.wrong_answers = []
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")

    def save(self):
        data = {
            "quiz_type": self.quiz_type,
            "current_index": self.current_index,
            "questions_answered": self.questions_answered,
            "answers": self.answers,
            "score": self.score,
            "wrong_answers": self.wrong_answers,
            "timestamp": self.timestamp
        }
        save_path = self.get_save_path()
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        with open(save_path, 'w') as f:
            json.dump(data, f)

    @classmethod
    def load(cls):
        save_path = cls.get_save_path()
        if not os.path.exists(save_path):
            return None
        try:
            with open(save_path, 'r') as f:
                data = json.load(f)
                quiz_type = data.get("quiz_type")
                if quiz_type not in [TestType.FULL, TestType.PRACTICE]:
                    raise ValueError(
                        f"Invalid quiz type in save file: {quiz_type}")
                progress = cls(quiz_type)
                for key, value in data.items():
                    if key != "quiz_type":
                        setattr(progress, key, value)
                return progress
        except Exception as e:
            print(f"{Fore.RED}Error loading progress: {e}{Style.RESET_ALL}")
            return None

    @classmethod
    def check_progress(cls):
        progress = cls.load()
        if not progress:
            return None

        quiz_type = progress.quiz_type
        total_questions = TEST_CONFIG[quiz_type]["total_questions"]
        completion = (progress.current_index / total_questions) * 100
        score_percentage = (progress.score / progress.questions_answered) * \
            100 if progress.questions_answered else 0

        print(f"\n{Fore.CYAN}Found Saved Quiz Progress:{Style.RESET_ALL}")
        print("─" * 50)
        print(
            f"Quiz Type: {Fore.GREEN}{TEST_CONFIG[quiz_type]['name']}{Style.RESET_ALL}")
        print(f"Started: {Fore.YELLOW}{progress.timestamp}{Style.RESET_ALL}")
        print(
            f"Questions Completed: {Fore.GREEN}{progress.questions_answered}{Style.RESET_ALL}/{total_questions}")
        print(
            f"Current Score: {Fore.GREEN}{progress.score}{Style.RESET_ALL}/{total_questions}")
        print(
            f"Progress: {Fore.GREEN}{completion:.1f}%{Style.RESET_ALL} complete")
        print("─" * 50)

        while True:
            choice = input(
                f"{Fore.YELLOW}Continue this quiz? (y/n):{Style.RESET_ALL} ").lower()
            if choice == 'y':
                return progress
            if choice == 'n':
                cls.clear()
                return None

    @classmethod
    def clear(cls):
        save_path = cls.get_save_path()
        if os.path.exists(save_path):
            os.remove(save_path)


def load_full_questions():
    with open(find_data_file(), "r", encoding="utf-8") as f:
        data = json.load(f)
        questions = []
        for section in data:
            questions.extend(section["questions"])
        return questions


def main():
    try:
        init()
        args = parse_args()

        progress = QuizProgress.check_progress()
        if progress:
            if progress.quiz_type == TestType.FULL:
                questions = load_full_questions()
            else:
                test_path = find_valid_path(TEST_PATHS)
                with open(test_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    questions = []
                    for section in data:
                        questions.extend(section["questions"])
        else:
            quiz_type = TestType.FULL if args.full_test else None
            questions = load_full_questions() if quiz_type == TestType.FULL else load_questions()
            progress = QuizProgress(quiz_type or (TestType.FULL if len(questions) == 327
                                                  else TestType.PRACTICE))

        score, wrong_answers = quiz_user(questions, progress)

        if wrong_answers:
            review_wrong_answers(wrong_answers)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\nQuiz terminated by user." + Style.RESET_ALL)
    finally:
        print(Style.RESET_ALL)
        if os.name == "nt":
            os.system("color")


if __name__ == "__main__":
    main()
