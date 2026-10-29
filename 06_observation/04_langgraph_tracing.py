from dotenv import load_dotenv
load_dotenv()

from os import environ as env
from typing import TypedDict
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

model = ChatOpenAI(
    base_url=env["AZURE_OPENAI_ENDPOINT"],
    api_key=SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)

class State(TypedDict):
    topic: str
    draft: str
    feedback: str
    rounds: int

def write(state: State):
    if state["feedback"]:
        prompt = (
            f"Rewrite this tweet using the feedback.\n"
            f"Tweet: {state['draft']}\nFeedback: {state['feedback']}"
        )
    else:
        prompt = f"Write a one-line tweet about {state['topic']}."
    return {"draft": model.invoke(prompt).content}

def review(state: State):
    prompt = f"Give one short suggestion to improve this tweet:\n{state['draft']}"
    return {"feedback": model.invoke(prompt).content, "rounds": state["rounds"] + 1}

def route(state: State):
    return "write" if state["rounds"] < 2 else END

builder = StateGraph(State)
builder.add_node("write", write)
builder.add_node("review", review)
builder.add_edge(START, "write")
builder.add_edge("write", "review")
builder.add_conditional_edges("review", route, ["write", END])
graph = builder.compile()

result = graph.invoke(
    {"topic": "observability", "draft": "", "feedback": "", "rounds": 0},
    config={
        "run_name": "tweet_loop",
        "tags": ["staging"],
        "metadata": {"max_rounds": 2},
    },
)
print(result["draft"])