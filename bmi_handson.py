from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    weight : float
    height : float
    bmi : float
    error : str
    category : str

def calculate_bmi(state: State):
    if state["height"] != 0:
        bmi = state["weight"] / (state["height"] * state["height"])
        return {"bmi" : bmi}
    else :
        return {"error" : "Height cannot be 0."}

def label_bmi(state : State):
    if(state["bmi"] <= 18.5):
        return {"category" : "underweight"}
    elif state["bmi"] > 18.5 and state["bmi"] < 25:
        return {"category" : "normal"}
    elif state["bmi"] >=25 and state["bmi"] < 30:
        return {"category" : "overweight"}
    else :
        return {"category" : "obese"}

b = StateGraph(State)

b.add_node("bmi", calculate_bmi)
b.add_node("label_bmi", label_bmi)

b.add_edge(START, "bmi")
b.add_edge("bmi", "label_bmi")
b.add_edge("label_bmi", END)

graph = b.compile()

print(graph.invoke(State(weight=86.00, height=1.75, bmi=0.0, error="", category="")))
# print(graph.get_graph().draw_mermaid())