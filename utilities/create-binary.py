import PyInstaller.__main__
import os
import sys


def create_binary():
    try:
        # Set paths
        cwd = os.getcwd()  # Get directory where script is called from
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script_path = os.path.join(base_path, 'utilities', 'quiz.py')
        data_file = os.path.join(
            base_path, 'question-bank/full/json', 'ECS-HSE-Revision-Guide-24.json')
        icon_path = os.path.join(base_path, '.github',
                                 'media', 'images', 'icon.ico')

        print(f"Creating binary from: {script_path}")
        print(f"Including data from: {data_file}")

        # Define PyInstaller arguments with minimal flags
        pyinstaller_args = [
            f'--icon={icon_path}',
            '--noupx',
            '--onefile',
            '--name=ecs-quiz.exe',
            '--clean',
            '--hidden-import=sys',
            '--hidden-import=os',
            f'--distpath={cwd}',  # Output to current directory
            '--workpath=build',   # Keep build files in build/
            f'--add-data={data_file};.',  # Include data file in binary
        ]

        # Add icon if exists
        if os.path.exists(icon_path):
            pyinstaller_args.append(f'--icon={icon_path}')

        pyinstaller_args.append(script_path)

        # Run PyInstaller
        PyInstaller.__main__.run(pyinstaller_args)
        print("Binary creation successful!")

    except Exception as e:
        print(f"Error creating binary: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    create_binary()
