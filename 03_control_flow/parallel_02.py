import operator
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    scores: Annotated[list[int], operator.add]   # reducer yahan hai
    avg: float

def n1(state): return {"scores": [8]}
def n2(state): return {"scores": [7]}
def n3(state): return {"scores": [9]}

def average(state):
    return {"avg": sum(state["scores"]) / len(state["scores"])}

g = StateGraph(S)
for name, fn in [("n1", n1), ("n2", n2), ("n3", n3), ("average", average)]:
    g.add_node(name, fn)

for n in ["n1", "n2", "n3"]:
    g.add_edge(START, n)
    g.add_edge(n, "average")
g.add_edge("average", END)

workflow = g.compile()
print(workflow.invoke({"scores": []}))