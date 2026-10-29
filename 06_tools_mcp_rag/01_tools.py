from os import environ as env
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()

from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition


llm = ChatOpenAI(
    base_url=env["AZURE_OPENAI_ENDPOINT"],
    api_key=SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)

@tool
def calculator(a: float, b: float, op: str) -> float:
    """Do basic arithmetic on two numbers.
    op must be one of: add, sub, mul, div.
    Use this for any math instead of calculating in your head."""
    ops = {"add": a + b, "sub": a - b, "mul": a * b, "div": a / b if b else float("nan")}
    return ops[op]

llm_with_tools = llm.bind_tools([calculator])

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def build(with_loop: bool):
    g = StateGraph(ChatState)
    g.add_node("chat_node", chat_node)
    g.add_node("tools", ToolNode([calculator]))
    g.add_edge(START, "chat_node")
    g.add_conditional_edges("chat_node", tools_condition)
    g.add_edge("tools", "chat_node" if with_loop else END)
    return g.compile()

q = "What is 654 times 713? Then add 1000 to that result."
for loop in (False, True):
    out = build(loop).invoke({"messages": [HumanMessage(q)]})
    print(f"\n=== with_loop={loop} | {len(out['messages'])} messages ===")
    for m in out["messages"]:
        print(type(m).__name__, "|", m.text[:120], "|", getattr(m, "tool_calls", None))