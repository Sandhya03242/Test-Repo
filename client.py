import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from fastmcp import Client 
import asyncio


load_dotenv()
client = OpenAI()

mcp_client = Client("http://localhost:8050")

messages = [
    {"role": "system", "content": 
    "You are a GitHub monitoring assistant "
    "If the user asks repository status or recent GitHub action "
    "use the get_repository_status_tool tool."
    "For general questions, respond using your own reasoning."}
    ]

tools = [
        {
            "type": "function",
            "function": {
                "name": "get_repository_status_tool",
                "description": "Returns recent GitHub webhook events stored by the server",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit":{
                            "type":"integer",
                            "description":"Number of recent events to fetch"
                        }
                    },
                    "required": ["limit"],
                },
            }
        },
    ]

print("🤖 Ask me anything! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(model="gpt-4.1-nano", messages=messages, tools=tools, tool_choice="auto")

    message = response.choices[0].message

    if hasattr(message, "tool_calls") and message.tool_calls:
        for tool_call in message.tool_calls:
            # print("Tool was used by the agent")
            function_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if function_name == "get_repository_status_tool":
                result = mcp_client.call_tool("get_repository_status_tool", arguments)
            else:
                print(f"⚠️ Unknown function called: {function_name}")
                continue

            messages.append(message)
            messages.append({"role": "tool","tool_call_id": tool_call.id,"content": str(result)})
            print(f"Tool used: {function_name}")

            follow_up = client.chat.completions.create(
                    model="gpt-4.1-nano",
                    messages=messages
                )
            reply = follow_up.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            print(f"Agent: {reply}")
    else:
        print("LLM answered without using a tool")
        reply = message.content
        messages.append(message)
        print(f"Agent: {reply}")

