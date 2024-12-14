import json
import random
from colorama import init, Fore, Style

def load_questions():
    with open('../tests/ecs-test.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    questions = []
    for section in data:
        questions.extend(section['questions'])
    return questions

def quiz_user(questions):
    init()  # Initialize colorama
    score = 0
    random.shuffle(questions)

    for i, question in enumerate(questions, 1):
        print("\n" + "="*50)
        print(f"\nQuestion {i}:")
        print(Fore.MAGENTA + f"\n{question['question']}\n" + Style.RESET_ALL)

        options = question.get('options', {})
        if options:
            for key, value in sorted(options.items()):
                print(f" {key}: {value}")

        answer = input("\nYour answer: ").strip().upper()
        correct_answer = question.get('correct_answer', '').upper()

        if answer == correct_answer:
            print(Fore.GREEN + f"\n✓ Correct!" + Style.RESET_ALL)
            score += 1
        else:
            print(Fore.RED + f"\n✗ Incorrect" + Style.RESET_ALL + f" The correct answer was:" + Fore.GREEN + f" {correct_answer}" + Style.RESET_ALL )

        # Show explanation if available
        explanation = question.get('explanation', '')
        if explanation:
            # print("\nExplanation:", explanation)
            print(f"\nExplanation:\n\n" + Fore.MAGENTA + explanation + Style.RESET_ALL)

        input("\nPress Enter to continue...")

    print("\n" + "="*50)
    print(f"\nFinal Score: {score} out of {len(questions)} ({(score/len(questions)*100):.1f}%)")

if __name__ == "__main__":
    questions = load_questions()
    quiz_user(questions)