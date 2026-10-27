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
    question : str
    answer : str
    word_count : int

def answer_question(state : State):
    prompt = f"Answer the following question: {state['question']}"
    answer = model.invoke(prompt).content
    return {"answer": answer}

def count_words(state: State):
    return {"word_count" : len(state["answer"].split())}

b = StateGraph(State)
b.add_node("llm_qa", answer_question)
b.add_node("word_counter", count_words)

b.add_edge(START, "llm_qa")
b.add_edge("llm_qa", "word_counter")
b.add_edge("word_counter", END)

graph = b.compile()

result = graph.invoke(State({"question" : "What is concurrency in java?", "answer" : "", "word_count" : 0}))

print(result["word_count"])
print(graph.get_graph().draw_mermaid())