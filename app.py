# app.py
from openai import OpenAI
from tool import get_recent_github_events

REPO = "Sandhya03242/Test-Repo"
client = OpenAI()

def main():
    print("💬 GitHub Chatbot started! Type your question (type 'exit' to quit):\n")

    while True:
        user_question = input("You: ")

        if user_question.strip().lower() in {"exit", "quit"}:
            print("Exiting!")
            break

        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[
                {"role": "system", "content": (
                    "You are a GitHub monitoring assistant. "
                    f"The repository name is '{REPO}'. "
                    "If the user asks about repository status or recent events, "
                    "use the get_recent_github_events tool to get live data."
                )},
                {"role": "user", "content": user_question}
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "get_recent_github_events",
                        "description": "Fetch recent GitHub events for the repository",
                        "parameters": {}
                    }
                }
            ],
            tool_choice="auto"
        )

        msg = response.choices[0].message

        if hasattr(msg, "tool_calls") and msg.tool_calls:
            print("[Agent decided to get live data from GitHub...]")
            events = get_recent_github_events()
            if events:
                latest = events[0]
                answer = (
                    f"The repository '{REPO}' has {len(events)} recent events.\n"
                    f"Latest: {latest['type']} by {latest['actor']['login']}."
                )
            else:
                answer = f"The repository '{REPO}' has no recent events."
        else:
            answer = msg.content

        print(f"\n🤖 Answer: {answer}\n")

if __name__ == "__main__":
    main()


