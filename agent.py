from langchain_openai import ChatOpenAI
import os
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, ToolMessage, SystemMessage
from typing import TypedDict, List, Union, Annotated, Sequence
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph,END
from langgraph.graph.message import add_messages
import requests
from fastmcp import FastMCP
from fastmcp import tools
from collections import Counter
import json
from dotenv import load_dotenv
load_dotenv()

class AgentState(TypedDict):
    message:Annotated[Sequence[BaseMessage],add_messages]


GITHUB_TOKEN=os.environ.get("GITHUB_PAT")
owner="Sandhya03242"
REPO="Test-Repo"

github_mcp=FastMCP(name="github_mcp")

@github_mcp.tool
def github_recent_events()->str:
    """Fetch the latest GitHub event from repository."""
    url=f"https://api.github.com/repos/{owner}/{REPO}/events"
    header={
        "Authorization":f"Bearer {GITHUB_TOKEN}","Accept":"application/vnd.github+json"
    }
    response=requests.get(url,headers=header)
    events=response.json()
    event_summary={}
    for event in events:
        event_type=event.get("type","Unknown")
        actor=event.get("actor",{}).get("login","unknown")
        key=(event_type,actor)
        event_summary[key]=event_summary.get(key,0)+1
    summary=[]
    for(event_type,actor),count in event_summary.items():
        type_event=event_type.replace("Event","")
        summary.append(f"{type_event} event occured {count} times by {actor}")
    summary="Recent activity: "+",".join(summary)
    return f"Repository: {REPO}. {summary}"

# ------------------------------------------------------------------------------------------------------------------
# slack
# ------------------------------------------------------------------------------------------------------------------
slack_mcp=FastMCP(name="slack_agent")
SLACK_TOKEN=os.environ.get("SLACK_API_KEY")
SLACK_ID=os.environ.get("SLACK_Channel_ID")
slack_header={
        "Authorization":f"Bearer {SLACK_TOKEN}","Accept":"application/json"
    }

@slack_mcp.tool
def slack_post_message(text:str)->str:
    """Post message to the channel"""
    url="https://slack.com/api/chat.postMessage"
    payload={
        "channel":SLACK_ID,
        "text":text
    }
    response=requests.post(url=url,json=payload,headers=slack_header).json()
    return "Message Sent" if response.get("ok") else f"Error: {response.get('error')}"

@slack_mcp.tool
def slack_add_reaction(emoji:str,timestamp:str)->str:
    """Add a reaction to a message."""
    url="https://slack.com/api/reactions.add"
    payload={
        "channel":SLACK_ID,
        "timestamp":timestamp,
        "name":emoji
    }
    response=requests.post(url=url,json=payload,headers=slack_header).json()
    return "Reaction added" if response.get("ok") else f"Error: {response.get('error')}"


@slack_mcp.tool
def slack_get_channel_history(limit:int=3)->list:
    """Get messages from the channel"""
    url="https://slack.com/api/conversations.history"
    payload={
        "channel":SLACK_ID,
        "limit":limit
    }
    response=requests.get(url=url,params=payload,headers=slack_header).json()
    if not response.get("ok"):
        return f"Error: {response.get('error')}"
    messages=response.get("messages",[])
    text_list=[f"{m.get('text')}" for m in messages]
    return "Last messages:\n"+"\n".join(text_list)

@slack_mcp.tool
def github_notification_slack(message:str)->str:
    """Notify slack with a github update or alert."""
    url="https://slack.com/api/chat.postMessage"
    payload={
        "channel":SLACK_ID,
        "text":message
    }
    response=requests.post(url=url,json=payload,headers=slack_header).json()
    return "GitHub alert sent to slack" if response.get("ok") else f"Error: {response.get('error')}"

@slack_mcp.tool
def slack_join_channel(channel_id="C05C241BE4V")->str:
    """Join a slack channel"""
    url="https://slack.com/api/conversations.join"
    response=requests.post(url,json={"channel":channel_id},headers=slack_header).json()
    return "joined channel" if response.get("ok") else f"Error: {response.get('error')}"

# ------------------------------------------------------------------------------------------------------------------
# Main
# -------------------------------------------------------------------------------------------------------------------


llm=ChatOpenAI(model="gpt-4.1-nano",temperature=0)

tools=[github_recent_events.fn,slack_add_reaction.fn,slack_get_channel_history.fn,slack_post_message.fn,github_notification_slack.fn,slack_join_channel.fn]
llm=llm.bind_tools(tools)


def should_continue(state:AgentState):
    """Check if the last message contain tool call."""
    result=state['message'][-1]
    return hasattr(result,'tool_call') and len(result.tool_calls)>0

sys_prompt="""
You are a multi-agent assistant.
You can use these tools: get_recent_events (to check github repository status or recent events),
and slack tools (to get latest slack messages, post message, add reaction etc).
If the user asks about GitHub, call get_recent_events.
"""


# llm agent
def call_llm(state:AgentState)->AgentState:
    "Function to call the LLM with the current state."
    message=list(state['message'])
    message=[SystemMessage(content=sys_prompt)]+message
    message=llm.invoke(message)
    return {"message":[message]+[message]}

def get_agent_route(state):
    tool_calls=state['message'][-1].tool_calls
    if not tool_calls:
        return "__end__"
    tool_name=tool_calls[0]['name']
    if 'github' in tool_name:
        return "GitHubAgent"
    elif "slack" in tool_name:
        return "SlackAgent"
    else:
        return "__end__"
    
github_tools=[github_recent_events.fn]
github_tool_map={tool.__name__:tool for tool in github_tools}

def github_agent(state):
    tool_calls=state['message'][-1].tool_calls
    results=[]
    for t in tool_calls:
        fn=github_tool_map.get(t['name'])
        if fn:
            result=fn(**t['args'])
            results.append(ToolMessage(tool_call_id=t['id'],name=t['name'],content=str(result)))
    return {"message":state['message']+results}


slack_tools=[slack_add_reaction.fn,slack_get_channel_history.fn,slack_post_message.fn,github_notification_slack.fn,slack_join_channel.fn]
slack_tool_map={tool.__name__:tool for tool in slack_tools}

def slack_agent(state):
    tool_calls=state['message'][-1].tool_calls
    results=[]
    for t in tool_calls:
        fn=slack_tool_map.get(t['name'])
        if fn:
            result=fn(**t['args'])
            results.append(ToolMessage(tool_call_id=t['id'],name=t['name'],content=str(result)))
    return {"message":state['message']+results}


graph=StateGraph(state_schema=AgentState)
graph.add_node("MainAgent",call_llm)
graph.add_node("GitHubAgent",github_agent)
graph.add_node("SlackAgent",slack_agent)

graph.add_conditional_edges(
    "MainAgent",get_agent_route,{
        "GitHubAgent":"GitHubAgent",
        "SlackAgent":"SlackAgent",
        "__end__":"__end__"
    }
)

graph.add_edge("GitHubAgent","MainAgent")
graph.add_edge("SlackAgent","MainAgent")
graph.set_entry_point("MainAgent")
multi_agent=graph.compile()

def run_agent():
    print("🤖 Multi-Agent Assitant")
    while True:
        q=input("You: ")
        if q.lower() in {"exit","quit"}:
            break
        state={"message":[HumanMessage(content=q)]}
        result=multi_agent.invoke(state)
        print("Agent: ", result['message'][-1].content)

if __name__=="__main__":
    run_agent()


