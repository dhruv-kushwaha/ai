from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

@tool
def divide(a: float, b: float) -> float:
    """Divide a by b."""
    return a / b  # raises ZeroDivisionError when b == 0

from langgraph.graph import StateGraph, MessagesState, START, END

def call(args, **node_kwargs):
    msg = AIMessage(content="", tool_calls=[
        {"name": "divide", "args": args, "id": "call_1", "type": "tool_call"}
    ])
    g = StateGraph(MessagesState)
    g.add_node("tools", ToolNode([divide], **node_kwargs))
    g.add_edge(START, "tools")
    g.add_edge("tools", END)
    app = g.compile()
    try:
        out = app.invoke({"messages": [msg]})
        m = out["messages"][-1]
        print("  ->", type(m).__name__, "| status:", m.status, "|", m.content)
    except Exception as e:
        print("  -> RAISED", type(e).__name__, ":", e)

cases = {
    "valid":       {"a": 10, "b": 2},
    "bad args":    {"a": "abc", "b": 2},
    "body raises": {"a": 1, "b": 0},
}
for label, args in cases.items():
    print(f"\n[{label}] default")
    call(args)
    print(f"[{label}] handle_tool_errors=True")
    call(args, handle_tool_errors=True)
    print(f"[{label}] custom string")
    call(args, handle_tool_errors="Tool failed. Check the inputs and try again.")