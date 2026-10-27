'''
Ab exercise: ye khud likho, mere code ke bina.

State: title, outline, content.
Node create_outline: title se outline banwao, {"outline": ...} return karo.
Node create_blog: title aur outline dono prompt me daalo, {"content": ...} return karo.
Edges: START → create_outline → create_blog → END.
Title "Rise of AI in India" se chalao. outline aur content ke pehle 300 characters paste karo.
'''

from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import environ as env
from pydantic import SecretStr

load_dotenv()


model = ChatOpenAI(
    base_url= env["AZURE_OPENAI_ENDPOINT"],
    api_key= SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-5-mini",
)

class State(TypedDict):
    title : str
    outline : str
    content : int

def create_outline(state : State):
    prompt = f"Write an outline around the topic: {state['title']}"
    answer = model.invoke(prompt).content
    return {"outline": answer}

def create_blog(state : State):
    prompt = f"Write a blog around the topic: {state['title']} which has the outline {state['outline']}"
    answer = model.invoke(prompt).content
    return {"content": answer}

b = StateGraph(State)
b.add_node("create_outline", create_outline)
b.add_node("create_blog", create_blog)

b.add_edge(START, "create_outline")
b.add_edge("create_outline", "create_blog")
b.add_edge("create_blog", END)

graph = b.compile()

result = graph.invoke(State({"title" : "Rise of AI in India", "outline" : "", "content" : 0}))

print("Outline : \n" + result["outline"][:300])
print("Content : \n" + result["content"][:300])