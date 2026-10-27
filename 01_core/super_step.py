from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    log: Annotated[list[str], add]

def mk(name):
    return lambda s: {"log": [name]}

b = StateGraph(S)
for n in "abcd":
    b.add_node(n, mk(n))
b.add_edge(START, "a")
b.add_edge("a", "b")
b.add_edge("a", "c")
b.add_edge("b", "d")
# b.add_edge("c", "d")
b.add_edge("d", END)
g = b.compile()

for ev in g.stream({"log": []}, stream_mode="debug"):
    if ev["type"] == "task_result":
        print("super-step", ev["step"], "->", ev["payload"]["name"])