from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel

class State(BaseModel):
  text : str
  words : int = 0

def clean(state : State):
  return {"text" : state.text.strip().lower()}

def bad_node(state : State):
  return {"words" : "three"}

builder = StateGraph(State)
builder.add_node("clean", clean)
builder.add_node("bad_node", bad_node)

builder.add_edge(START, "clean")
builder.add_edge("clean", "bad_node")
builder.add_edge("bad_node", END)

print(builder.compile().invoke({"text" : " Hello There, I am Dhruv "}))