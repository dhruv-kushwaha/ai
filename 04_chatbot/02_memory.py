from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import SecretStr
from os import environ as env
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

load_dotenv()

llm = ChatOpenAI(
    base_url= env["AZURE_OPENAI_ENDPOINT"],
    api_key= SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)

def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

checkpointer = MemorySaver()
chatbot = graph.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "dhruv-1"}}
config2 = {"configurable": {"thread_id": "dhruv-2"}}


chatbot.invoke({"messages": [HumanMessage(content="My name is Dhruv Kushwaha")]}, config= config)
snapshot = chatbot.get_state(config)
print(snapshot.values["messages"])   # the saved conversation
print(snapshot.next)                  # () when the run is finished

result1 = chatbot.invoke({"messages": [HumanMessage(content="What is my name?")]}, config= config)

print(f"Result1:\n {result1["messages"]} ")

result2 = chatbot.invoke({"messages": [HumanMessage(content="What is my name?")]}, config=config2)

print(f"Result2:\n {result2["messages"]}")