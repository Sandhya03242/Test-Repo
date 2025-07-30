import json
from collections import Counter
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("repo-status-server")
EVENTS_FILE = Path(__file__).parent / "github_events.json"

@mcp.tool()
def get_recent_actions_events(limit: int = 10) -> str:
    if not EVENTS_FILE.exists():
        return json.dumps([])
    with EVENTS_FILE.open("r") as file:
        events = json.load(file)
    return json.dumps(events[-limit:], indent=2)

def get_repository_status():
    try:
        result_json = get_recent_actions_events(limit=10)
        events = json.loads(result_json)
    except Exception as e:
        print(f"Error fetching events: {e}")
        return

    if not events:
        print("No events found.")
        return

    event_types = [event.get("event_type", "unknown") for event in events]
    counts = Counter(event_types)
    latest = events[-1]
    sender = latest.get("sender", {}).get("login", "unknown")
    latest_type = latest.get("event_type", "unknown")

    print("Repository Status Report:")
    print(f"Total Events: {len(events)}")
    print("Event Counts:")
    for event_type, count in counts.items():
        print(f"{event_type}: {count}")
    print(f"Latest Event: {latest_type} by {sender}")

if __name__ == "__main__":
    
    get_repository_status()
    mcp.run()

    










