
import subprocess

# Run LineWolf Dispatcher (calls OpenAI)
subprocess.run(["python3", "main_dispatcher.py"])

# Run Line Movement Poller (calls TheOddsAPI only)
subprocess.run(["python3", "line_movement_poller.py"])
