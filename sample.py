from datetime import datetime

with open("log.txt", "a") as f:
    f.write(f"Hello! Script ran at {datetime.now()}\n")

print("Script executed successfully")