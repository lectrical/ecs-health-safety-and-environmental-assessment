## What is this?

This is an open source and free data source and toolset for the official revision questions that have been extracted from the official revision pdf and provided as plain text and `json` here.

## Assessment info

For ECS Health, Safety and Environmental Assessments from 6 May 2024 - The assessment will be based on a 50 randomly selected questions from the bank of 327 revision questions.

The ECS HSE assessment comprises questions covering eleven topics. The numbers of questions randomly selected from each topic are:

| Topic                                             | Questions |
| ------------------------------------------------- | --------- |
| General Health and Safety at Work                 | 6         |
| Manual Handling Operations                        | 4         |
| Reporting Accidents                               | 3         |
| Personal Protective Equipment at Work             | 4         |
| Health and Hygiene                                | 3         |
| Fire and Emergency (inc Fire Safety in Buildings) | 9         |
| Work at Height                                    | 5         |
| Work Equipment                                    | 4         |
| Special Site Hazards                              | 3         |
| Electrotechnical                                  | 6         |
| Environmental                                     | 3         |

> [!TIP]
> You will not be asked a question that is not in the revision pdf when taking the test. If you know all the questions and answers in the revision guide you will get 50/50

## Free revision

A Socrative room for all 317 questions across all 11 sections.

https://b.socrative.com/login/student/

Use `SMITH1980` to login.

> [!WARNING]
> It will not remember your progress if you close the session

Import link: https://b.socrative.com/teacher/#import-quiz/79399500

## Data sources

> [!NOTE]
> All this information is publicly available and free to use. Here are the source locations.

- Revision info : https://www.ecscard.org.uk/content/Preparation-and-Revision
- Revision guide pdf: https://www.ecscard.org.uk/getmedia/2bfce807-2289-4a51-a23e-b1c6f801f3e3/ECS-HSE-Revision-Guide-24-pdf.pdf

> [!TIP]
> This pdf is the basis of the information in this project. The information is freely available and you are supposed to revise it for the test.

## What do the scripts do?

> [!NOTE]
> Made with Co-pilot

`process_questions.py` will process all 327 questions across the 11 sections of the `txt-full/ECS-HSE-Revision-Guide-24.txt` that were taken from the `ECS-HSE-Revision-Guide-24.pdf`

This python script parses the txt into `json` in one of two ways.

- It creates a single `json` file with all sections in a single file in `json-full`
- It creates a `json` file per section in the `json-sections` directory

> [!NOTE]
> it defaults to `txt-full` and the source dir but can accept an input for the dir.

```bash
Usage: python process_questions.py <mode> [input_directory]
```

```bash
python .\process_questions.py full
python .\process_questions.py sections

python .\process_questions.py full .\txt-full\
python .\process_questions.py sections .\txt-full\
```

This just makes it easy to update the text file as and when the official revision guide is updated and the changed can easily be propagated to the json files.

`create-test.py` will generate a 50 question quiz with randomly selected questions from `json-full/ECS-HSE-Revision-Guide-24.json` in the same format as the official one. Every time it is run it will create file `tests/ecs-test.json`

`test_json_to_text.py` will convert `tests/ecs-test.json` to a human readable text file.

example Usage

```bash
git clone https://github.com/lectrical/ecs-health-safety-and-environmental-assessment.git
cd ecs-health-safety-and-environmental-assessment/scripts
python create-test.py
python test_json_to_text.py
```

The check the `tests` directory for the outputs. You can feed the txt version to ai quiz generators and revision platforms like:

https://quizgecko.com/
https://www.remnote.com/

`quiz.py` in `tests` will run a quiz via terminal from the generated tests/ecs-test.json.

requires `pip install colorama`

## codespaces

You can fork the repo and run a [preconfigured](.devcontainer/devcontainer.json) codespace that will generate a random 50 question quiz and launch it in the terminal.
