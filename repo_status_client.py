import json
from collections import Counter
import requests
MCP_SERVER_URL = "http://localhost:9000/get_recent_actions_events"

async def get_repository_status():
        try:
            response = requests.get(MCP_SERVER_URL)
            if response.status_code != 200:
                print(f"Error fetching events: {response.status_code}-{response.text}")
                return
            events = response.json()
        except Exception as e:
            print(f"Error fetching events: {e}")
            return 
        if not events:
            print("No events found.")
            return
        event_types = [event.get("event_type","unknown") for event in events]
        counts=Counter(event_types)
        latest=events[-1]
        sender=latest.get("sender", {}).get("login", "unknown")
        latest_type=latest.get("event_type", "unknown")
        print("Repository Status Report: ")
        print(f"Total Events: {len(events)}")
        print("Event Counts:")
        for event_type, count in counts.items():
            print(f"{event_type}: {count}")
        print(f"Latest Event: {latest_type} by {sender}")

if __name__ == "__main__":
    get_repository_status()
    










