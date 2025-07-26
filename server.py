import json
from pathlib import Path
from fastmcp import FastMCP
mcp= FastMCP("repo-status-server")
EVENTS_FILE=Path(__file__).parent / "github_events.json"

@mcp.tool()
async def get_recent_actions_events(limit:int=10)->str:
    if not EVENTS_FILE.exists():
        return json.dumps([])
    with EVENTS_FILE.open("r") as file:
        events = json.load(file)
    return json.dumps(events[-limit:],indent=2)
if __name__ == "__main__":
    mcp.run()
    
