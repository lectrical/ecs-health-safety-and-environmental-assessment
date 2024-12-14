import json

def convert_json_to_text():
    with open('../tests/ecs-test.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    text_output = ""

    for section in data:
        section_number = section.get('section_number', 'Unknown Section')
        section_title = section.get('title', '')
        text_output += f"Section {section_number}"
        if section_title:
            text_output += f": {section_title}"
        text_output += "\n" + "=" * 50 + "\n\n"

        questions = section.get('questions', [])
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

    with open('../tests/ecs-test.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(text_output)

if __name__ == "__main__":
    convert_json_to_text()