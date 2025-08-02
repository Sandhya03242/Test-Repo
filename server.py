from fastmcp import FastMCP
import os
import json
from pathlib import Path
from dotenv import load_dotenv
import requests

load_dotenv()
SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")
EVENTS_FILE = Path(__file__).parent / "github_events.json"

mcp = FastMCP("server")

@mcp.tool
def notify_slack_about_latest_event():
    """Send the most recent GitHub event to Slack"""
    if not EVENTS_FILE.exists():
        return {"status": "error", "message": "No events to post."}
    with open(EVENTS_FILE) as f:
        events = json.load(f)
    if not events:
        return {"status": "error", "message": "No events to post."}
    latest = events[-1]
    message = f"""
🚀 GitHub Event Notification:
Event: {latest.get('event_type', 'unknown')} | Action: {latest.get('action', '')}
Repository: {latest.get('repository', 'unknown')}
Sender: {latest.get('sender', 'unknown')}
"""
    response = requests.post(SLACK_WEBHOOK_URL, json={"text": message.strip()})
    return {
        "status": "sent" if response.ok else "failed",
        "slack_response": response.text,
        "event_summary": message.strip()
    }

if __name__ == "__main__":
    print("✅ Starting MCP server...")
    mcp.run(transport="http", host="localhost", port=8000)
