import operator
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver

class S(TypedDict):
    steps: Annotated[list[str], operator.add]

def a(state): return {"steps": ["a"]}
def b(state): return {"steps": ["b"]}
def c(state): return {"steps": ["c"]}

g = StateGraph(S)
g.add_node("a", a); g.add_node("b", b); g.add_node("c", c)
g.add_edge(START, "a")
g.add_edge("a", "b"); g.add_edge("a", "c"); g.add_edge("c", END)
g.add_edge("b", END)

wf = g.compile(checkpointer=InMemorySaver())
cfg = {"configurable": {"thread_id": "t1"}}
print(wf.invoke({"steps": []}, cfg))

for i, snap in enumerate(reversed(list(wf.get_state_history(cfg)))):
    print(i, snap.values, snap.next)