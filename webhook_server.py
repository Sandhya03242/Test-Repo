import json
from datetime import datetime
from pathlib import Path
from aiohttp import web

EVENTS_FILE = Path(__file__).parent / "github_events.json"

async def handle_webhook(request):
    try:
        data = await request.json()

        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": request.headers.get("X-GitHub-Event", "unknown"),
            "action": data.get("action"),
            "workflow_run": data.get("workflow_run"),
            "check_run": data.get("check_run"),
            "repository": data.get("repository", {}).get("full_name"),
            "sender": data.get("sender", {}).get("login")
        }

        events = []
        if EVENTS_FILE.exists():
            with open(EVENTS_FILE, 'r') as f:
                events = json.load(f)

        events.append(event)
        events = events[-100:]

        with open(EVENTS_FILE, 'w') as f:
            json.dump(events, f, indent=2)

        return web.json_response({"status": "received"})
    except Exception as e:
        return web.json_response({"error": str(e)}, status=400)

app = web.Application()
app.router.add_post('/webhook/github', handle_webhook)

if __name__ == '__main__':
    print("🚀 Starting webhook server on http://localhost:9000")
    print("🔗 Webhook URL: http://localhost:9000/webhook/github")
    web.run_app(app, host='localhost', port=9000)
