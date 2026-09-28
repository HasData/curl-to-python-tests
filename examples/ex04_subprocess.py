import json
import subprocess

# Running the copied command as-is. Pass a list, not a shell string: no quoting surprises,
# no shell injection when the URL comes from user input.
command = [
    "curl", "--silent", "--show-error", "--fail", "--max-time", "30",
    "https://quotes.toscrape.com/api/quotes?page=1",
    "-H", "accept: application/json",
    "--compressed",
]
result = subprocess.run(command, capture_output=True, text=True, check=True)
data = json.loads(result.stdout)
print(len(data["quotes"]), "quotes via subprocess, exit code", result.returncode)
