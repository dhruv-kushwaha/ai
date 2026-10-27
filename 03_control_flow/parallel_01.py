import time
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    a: str
    b: str
    c: str
    result: str

def slow_a(state):
    time.sleep(2)
    return {"a": "A done"}      # sirf apni field return karo

def slow_b(state):
    time.sleep(2)
    return {"b": "B done"}

def slow_c(state):
    time.sleep(2)
    return {"c": "C done"}

def merge(state):
    return {"result": f"{state['a']} | {state['b']} | {state['c']}"}

g = StateGraph(S)
g.add_node("slow_a", slow_a)
g.add_node("slow_b", slow_b)
g.add_node("slow_c", slow_c)
g.add_node("merge", merge)

# fan-out: START se teen edges
g.add_edge(START, "slow_a")
g.add_edge(START, "slow_b")
g.add_edge(START, "slow_c")

# fan-in: teeno se merge
g.add_edge("slow_a", "merge")
g.add_edge("slow_b", "merge")
g.add_edge("slow_c", "merge")

g.add_edge("merge", END)
workflow = g.compile()

t = time.time()
out = workflow.invoke({})
print(out)
print(f"Time: {time.time() - t:.1f}s")