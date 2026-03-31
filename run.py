# run.py
import subprocess
import sys

def clear_moves(*file_paths):
    for file_path in file_paths:
        try:
            with open(file_path, 'w') as f:
                f.truncate(0)
        except IOError as e:
            print(f"File I/O error clearing {file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error clearing {file_path}: {e}")

# Clear both move files on startup
clear_moves('human_move.txt', 'engine_move.txt')

venv_python = 'python3'
script1 = 'gameProcessing.py'
script2 = 'cv_input.py'
script3 = 'GUI.py'

print("Starting all three processes...")
print(f"  1. Brain:   {script1}")
print(f"  2. Camera:  {script2}")
print(f"  3. Display: {script3}")

processes = []
try:
    processes.append(subprocess.Popen([venv_python, script1]))
    processes.append(subprocess.Popen([venv_python, script2]))
    processes.append(subprocess.Popen([venv_python, script3]))

    for p in processes:
        p.wait()

except KeyboardInterrupt:
    print("\nShutting down all processes...")
    for p in processes:
        p.terminate()
    print("Done.")

except Exception as e:
    print(f"An error occurred in run.py: {e}")
    for p in processes:
        p.terminate()