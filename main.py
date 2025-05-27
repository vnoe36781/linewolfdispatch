
import subprocess

# Run GPT-powered dispatcher
subprocess.run(["python3", "main_dispatcher.py"])

# Run line movement tracking logic
subprocess.run(["python3", "line_movement_poller.py"])
