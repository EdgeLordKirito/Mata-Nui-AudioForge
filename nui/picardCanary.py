import os
import shutil
import subprocess
import sys
import threading
import time

def copy_canary_file(target_path):
    source_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'canary.mp3')
    destination_file = os.path.join(target_path, 'canary.mp3')
    shutil.copyfile(source_file, destination_file)

def get_canary_file_size(target_path):
    canary_file_path = os.path.join(target_path, 'canary.mp3')
    return os.path.getsize(canary_file_path)

def run_picard_command(path):
    # Get the directory of the current script
    script_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the absolute path to ScanAndSave.txt
    scan_and_save_path = os.path.join(script_directory, 'ScanAndSave.txt').strip()

    # Copy the canary file to the target directory
    copy_canary_file(path)

    # Get the initial size of the canary file
    initial_size = get_canary_file_size(path)

    # Construct the command
    command = ['picard', '-e', f'LOAD {path}', '-e', f'FROM_FILE {scan_and_save_path}']

    # Execute the command in a separate thread
    process_thread = threading.Thread(target=execute_command, args=(command,))
    process_thread.start()

    # Monitor changes to the canary file's size
    while True:
        current_size = get_canary_file_size(path)
        if current_size != initial_size:
            print("Canary file has been modified. Execution completed.")
            break
        time.sleep(1)

    # Wait for additional time after the canary file is modified
    time.sleep(10)

    # Remove the canary file
    remove_canary_file(path)

    # Terminate the subprocess
    if process_thread.is_alive():
        print("Terminating the Picard command execution.")
        process_thread.terminate()

def execute_command(command):
    # Execute the command
    subprocess.run(command)

def remove_canary_file(target_path):
    canary_file_path = os.path.join(target_path, 'canary.mp3')
    if os.path.exists(canary_file_path):
        os.remove(canary_file_path)

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
