import requests
import os
from fastmcp.tools import tool
from collections import Counter
from datetime import datetime,timezone
# from dotenv import load_dotenv
# load_dotenv()
MCP_URL="https://api.githubcopilot.com/mcp"
GITHUB_REPO="Sandhya03242/Test-Repo"
GITHUB_API_URL=f"https://api.github.com/repos/{GITHUB_REPO}/events"
GITHUB_TOKEN=os.getenv("GITHUB_TOKEN")
HEADERS={"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def get_today_event():
    response=requests.get(GITHUB_API_URL, headers=HEADERS)
    if response.status_code !=200:
        raise Exception(f"GitHub API error: {response.status_code}-{response.text}")
    all_events=response.json()
    today=datetime.now(timezone.utc).date()
    today_event=[e for e in all_events if datetime.strptime(e["created_at"], "%Y-%m-$dT%H:%M:%SZ").date()==today]
    return today_event

def summarize_events(events):
    summary={}
    for e in events:
        event_type=e.get("type")
        author=e.get("actor",{}).get("login","unknown")
        if event_type not in summary:
            summary[event_type]={
                "count":1,
                "author":{author}
            }
        else:
            summary[event_type]['count']+=1
            summary[event_type]["author"].add(author)
    return summary

def generate_agent_reply(summary,date):
    if not summary:
        return f"No events occured today({date}) in the repository."
    lines=[f"Repository status for {date}: "]
    for event_type,data in summary.items():
        author=",".join(data['author'])
        lines.append(f"- {event_type}: {data['count']} time(s), triggered by {author}")
        return "\n".join(lines)
    
def check_repo_status():
    today=datetime.now(timezone.utc).date()
    print(f"checking events for {GITHUB_REPO} on {today}")
    events=get_today_event()
    summarize=summarize_events(events)
    print("Agent Reply: ", generate_agent_reply(summarize,today))

if __name__=="__main__":
    check_repo_status()




