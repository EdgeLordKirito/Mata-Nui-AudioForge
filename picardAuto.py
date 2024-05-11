import os
import subprocess
import sys

def run_picard_command(path):
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to ScanAndSave.txt
    scan_and_save_path = os.path.join(script_directory, 'ScanAndSave.txt').strip()

    # Construct the command
    command = ['picard', '-e', f'LOAD {path}', '-e', f'FROM_FILE {scan_and_save_path}']

    # Execute the command
    subprocess.run(command)

if __name__ == "__main__":
    # Check if 'picard' command is available
    try:
        subprocess.run(['picard', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("\033[1;31mERROR: PICARD COMMAND NOT FOUND.\033[0m\n"
              "Please install Picard with pip (e.g., pip install picard) to use this script.")
        sys.exit(1)

    # Check if the path argument is provided
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_directory>")
        sys.exit(1)

    # Get the path from the command-line argument
    target_path = sys.argv[1]

    # Check if the path is a directory
    if not os.path.isdir(target_path):
        print(f"Error: {target_path} is not a valid directory.")
        sys.exit(1)

    # Run the Picard command
    run_picard_command(target_path)
