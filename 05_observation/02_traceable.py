from dotenv import load_dotenv
load_dotenv()

from os import environ as env
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langsmith import traceable

model = ChatOpenAI(
    base_url=env["AZURE_OPENAI_ENDPOINT"],
    api_key=SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)

DOCS = [
    "LangSmith records every run of an LLM app.",
    "A trace is one end-to-end request.",
    "A run is one step inside a trace.",
    "FAISS is a vector store.",
]

@traceable(name="retrieve")
def retrieve(question: str):
    words = question.lower().split()
    return [d for d in DOCS if any(w in d.lower() for w in words)][:2]

@traceable(name="build_prompt")
def build_prompt(question: str, docs: list[str]) -> str:
    context = "\n".join(docs)
    return f"Use only this context.\nContext:\n{context}\n\nQuestion: {question}"

@traceable(name="answer")
def answer(question: str) -> str:
    docs = retrieve(question)
    prompt = build_prompt(question, docs)
    return model.invoke(prompt).content

print(answer("What is a trace?"))