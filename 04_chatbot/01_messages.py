from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import SecretStr
from os import environ as env

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
chatbot = graph.compile()

result = chatbot.invoke({"messages": [HumanMessage(content="What is the capital of India?")]})
print(len(result["messages"]))
print(result["messages"])