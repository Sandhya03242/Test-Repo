# import os
# from openai import OpenAI
# from fastmcp import Client
# from dotenv import load_dotenv
# import asyncio
# import json

# load_dotenv()

# client = OpenAI()
# mcp_client = Client("http://localhost:8000/mcp/")

# messages = [
#     {"role": "system", "content":
#      "You are a GitHub monitoring assistant. "
#      "If the user asks for recent GitHub events, use get_recent_action_events. "
#      "If the user asks for repository status, use get_repository_status."
#      "If the user asks for the name of the repository, use get_repository_name"}
# ]
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "get_recent_action_events",
#             "description": "Get recent GitHub action events",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "limit": {
#                         "type": "integer",
#                         "description": "Number of recent events to return",
#                         "default": 10
#                     }
#                 }
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_repository_status",
#             "description": "Get repository status report",
#             "parameters": {
#                 "type": "object",
#                 "properties": {}
#             }
#         }
#     },
#     {
#         "type": "function",
#         "function": {
#             "name": "get_repository_name",
#             "description": "Get the name of the GitHub repository from recent events",
#             "parameters": {
#                 "type": "object",
#                 "properties": {}
#             }
#         }
#     }
# ]

# async def main():
#     async with mcp_client:
#         print("💬 Ask about your repository (type 'exit' to quit)")
#         while True:
#             user_input = input("You: ")
#             if user_input.lower() == 'exit':
#                 break

#             messages.append({"role": "user", "content": user_input})

#             response = client.chat.completions.create(
#                 model="gpt-4.1-nano",
#                 messages=messages,
#                 tools=tools,
#                 tool_choice="auto"
#             )

#             choice = response.choices[0]
#             tool_calls = getattr(choice.message, "tool_calls", None)

#             if tool_calls:
#                 tool_results = []
#                 for call in tool_calls:
#                     tool_name=call.function.name
#                     arguments=json.loads(call.function.arguments)
#                     tool_call_id=call.id
#                     tool_result = await mcp_client.call_tool(tool_name,arguments)
#                     tool_results.append({"role": "tool", "tool_call_id":tool_call_id, "content": str(tool_result)})

#                 messages.append(choice.message)
#                 messages.extend(tool_results)

#                 response = client.chat.completions.create(
#                     model="gpt-4.1-nano",
#                     messages=messages
#                 )
#                 answer = response.choices[0].message.content
#             else:
#                 answer = choice.message.content

#             print(f"🤖 {answer}")
#             messages.append({"role": "assistant", "content": answer})

# if __name__ == "__main__":
#     asyncio.run(main())



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
            "If the user asks for recent GitHub events, use get_recent_action_events. "
            "If the user asks for repository status, use get_repository_status. "
            "If the user asks for the name of the repository, use get_repository_name."
        )
    }
]

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_recent_action_events",
            "description": "Get recent GitHub action events",
            "parameters": {
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of recent events to return",
                        "default": 10
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_repository_status",
            "description": "Get repository status report",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_repository_name",
            "description": "Get the name of the GitHub repository from recent events",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

async def main():
    async with mcp_client:
        print("💬 Ask about your repository (type 'exit' to quit)")
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

                messages.append({"role": "assistant", "content": choice.content or ""})
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







