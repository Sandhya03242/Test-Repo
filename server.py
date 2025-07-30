import json
from collections import Counter
from pathlib import Path
from fastmcp import FastMCP

mcp = FastMCP("server")
EVENTS_FILE = Path(__file__).parent / "github_events.json"

@mcp.tool()
def get_recent_action_events(limit: int = 10) -> str:
    if not EVENTS_FILE.exists():
        return json.dumps([])
    with EVENTS_FILE.open("r") as f:
        events = json.load(f)
    return json.dumps(events[-limit:], indent=2)

@mcp.tool()
def get_repository_status() -> str:
    try:
        result_json = get_recent_action_events(limit=10)
        events = json.loads(result_json)
    except Exception as e:
        return f"Error fetching events: {e}"

    if not events:
        return "No recent events found."

    event_types = [event.get("event_type", "unknown") for event in events]
    counts = Counter(event_types)
    latest = events[-1]
    sender = latest.get("sender", "unknown")
    latest_type = latest.get("event_type", "unknown")

    report = [
        "📊 Repository Status Report:",
        f"Total Events: {len(events)}",
        "Event Counts:"
    ]
    for event_type, count in counts.items():
        report.append(f" - {event_type}: {count}")
    report.append(f"Latest Event: {latest_type} by {sender}")
    return "\n".join(report)

if __name__ == "__main__":
    print("Running repo status tools server...")
    mcp.run(transport="http", host="localhost", port=8000)


    










