import json
import random
import glob

def main():
    # Load JSON data
    with open('../json-full/ECS-HSE-Revision-Guide-24.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

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

    # Create new test data structure
    test_data = []

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
        except (IndexError, KeyError) as e:
            print(f"Error processing section {section_index}: {e}")
            continue

    # Save to file
    with open('../tests/ecs-test.json', 'w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()