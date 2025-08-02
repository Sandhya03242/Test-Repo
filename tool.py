import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import json

load_dotenv()

SLACK_WEBHOOK_URL=os.environ.get("SLACK_WEBHOOK_URL")
EVENTS_FILE = Path(__file__).parent / "github_events.json"

def notify_slack_about_latest_event():
    """Post the most recent GitHub event to slack"""
    if not EVENTS_FILE.exists():
        return {"status":"error","message":"No events to post."}
    with open(EVENTS_FILE,"r") as f:
        events=json.load(f)

    if not events:
        return {"status":"error","message":"No events to post."}
    latest=events[-1]
    repo=latest.get("repository","unknown")
    event_type=latest.get("event_type","unknown")
    action=latest.get("action","")
    sender=latest.get("sender","unknown")
    workflow=latest.get("workflow_run",{})
    check=latest.get("check_run",{})

    message=f"GitHub Event Notification\n"
    message+=f"Event: `{event_type}` | Action: `{action}`\n"
    message+=f"Repository: `{repo}`\n"
    message+=f"Sender: `{sender}`\n"
    if workflow:
        message+=f"Workflow: `{workflow.get('name')}`\n"
        message+=f"Status: `{workflow.get('conclusion')}`\n"
    if check:
        message+=f"Check: `{check.get('name')}` | Status: `{check.get('conclusion')}`\n"
    response=requests.post(SLACK_WEBHOOK_URL,json={"text":message})
    return {
        "status":"sent" if response.ok else 'failed',
        "slack_response":response.text,
        "event_summary":message
    }



