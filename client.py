import os
import json
import asyncio
from openai import OpenAI
from fastmcp import Client
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
mcp_client = Client("http://localhost:8000/mcp/")

messages = [
    {
        "role": "system",
        "content": (
            "You are a GitHub monitoring assistant. "
            "If the user asks to notify Slack, use notify_slack_about_latest_event."
        )
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "notify_slack_about_latest_event",
            "description": "Send the most recent GitHub event to Slack",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

async def main():
    async with mcp_client:
        print("💬 Type anything to send the latest event to Slack (or 'exit')")
        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "exit":
                break

            messages.append({"role": "user", "content": user_input})

            response = client.chat.completions.create(
                model="gpt-4.1-nano",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )

            choice = response.choices[0].message
            tool_calls = getattr(choice, "tool_calls", None)

            if tool_calls:
                tool_results = []
                for call in tool_calls:
                    tool_name = call.function.name
                    arguments = json.loads(call.function.arguments)
                    tool_call_id = call.id

                    tool_result = await mcp_client.call_tool(tool_name, arguments)
                    tool_results.append({
                        "role": "tool",
                        "tool_call_id": tool_call_id,
                        "content": str(tool_result)
                    })

                messages.append(choice)     
                messages.extend(tool_results) 

                followup_response = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=messages
                )
                answer = followup_response.choices[0].message.content

            else:
                answer = choice.content

            print(f"🤖 {answer}")
            messages.append({"role": "assistant", "content": answer})

if __name__ == "__main__":
    asyncio.run(main())

