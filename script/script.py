from datetime import datetime
import os

os.makedirs("logs", exist_ok=True)

with open("logs/log.txt", "a") as f:
    f.write(f"Script ran at {datetime.now()}\n")

print("Automation ran successfully!")
