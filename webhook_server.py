from fastapi import FastAPI, Request
import uvicorn
import json
from pathlib import Path
app = FastAPI()
EVENTS_FILE = Path(__file__).parent / "github_events.json"
@app.post("/webhook/github")
async def receive_event(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event", "unknown")
    sender = payload.get("sender", {})
    event = {
        "event_type": event_type,
        "sender": sender,
        "payload": payload
    }
    if EVENTS_FILE.exists():
        with EVENTS_FILE.open("r") as file:
            events = json.load(file)
    else:
        events = []
    events.append(event)
    with EVENTS_FILE.open("w") as file:
        json.dump(events, file, indent=2)
    print(f"Received GiTHub event: {event_type}")
    return {"message": "Event received successfully"}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0",port=9000)