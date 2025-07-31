import os
import requests
from dotenv import load_dotenv
from tool import get_recent_github_events

load_dotenv()

MCP_BASE_URL = "https://api.githubcopilot.com/mcp"
GITHUB_TOKEN = os.environ.get("GITHUB_PAT")

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Content-Type": "application/json"
}

def create_session():
    """
    Try to create a new MCP session.
    """
    url = f"{MCP_BASE_URL}/sessions"
    payload = {
        "model": "gpt-4.1-nano", 
        "tools": [
            {
                "name": "get_recent_github_events",
                "description": "Fetch recent GitHub events",
                "parameters": {}
            }
        ]
    }

    print(f"🔧 Creating MCP session...")
    response = requests.post(url, json=payload, headers=HEADERS)
    print(f"✅ Response: {response.status_code}: {response.text}")

    if response.status_code == 200:
        data = response.json()
        return data.get("session_id")
    else:
        print("❌ Failed to create session")
        return None

def send_message(session_id, user_question):
    """
    Send user message to MCP server with session_id
    """
    url = f"{MCP_BASE_URL}/sessions/{session_id}/messages"
    payload = {
        "messages": [
            {"role": "user", "content": user_question}
        ],
        "tool_choice": "auto"
    }

    print(f"💬 Sending message to MCP...")
    response = requests.post(url, json=payload, headers=HEADERS)
    print(f"✅ Response: {response.status_code}: {response.text}")

    if response.status_code == 200:
        return response.json()
    else:
        print("❌ MCP server error:", response.status_code, response.text)
        return None

def main():
    print("💬 MCP chatbot started (type 'exit' to quit):\n")

    # Step 1: create MCP session
    session_id = create_session()
    if not session_id:
        print("❌ Could not create session. Exiting.")
        return

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() in {"exit", "quit"}:
            print("👋 Bye!")
            break

        data = send_message(session_id, user_input)
        if not data:
            continue

        # Check if agent asked us to call the tool
        tool_calls = data.get("tool_calls", [])
        if tool_calls:
            print("[🤖 Agent decided to call the tool...]")
            events = get_recent_github_events()
            if events:
                latest = events[0]
                answer = (
                    f"The repository has {len(events)} recent events.\n"
                    f"Latest: {latest['type']} by {latest['actor']['login']} at {latest['created_at']}."
                )
            else:
                answer = "No recent events found."
        else:
            answer = data.get("content", "🤖 (No content returned)")

        print(f"\n🤖 Answer: {answer}\n")

if __name__ == "__main__":
    main()
