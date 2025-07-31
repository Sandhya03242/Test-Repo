import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.environ.get("GITHUB_PAT")
REPO = "Sandhya03242/Test-Repo"

def get_recent_github_events():
    url = f"https://api.github.com/repos/{REPO}/events"
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()



