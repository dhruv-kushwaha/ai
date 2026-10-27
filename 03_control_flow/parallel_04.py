from pydantic import BaseModel, Field, SecretStr
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from os import environ

load_dotenv()

model = ChatOpenAI (
    base_url= environ["AZURE_OPENAI_ENDPOINT"],
    api_key=SecretStr(environ["AZURE_OPENAI_API_KEY"]),
    model="gpt-5-mini"
)

class EvaluationSchema(BaseModel):
    feedback : str = Field(description="Detailed feedback for the essay")
    score : int = Field(description="Score out of 10", ge=0, le=10)

structured_model = model.with_structured_output(EvaluationSchema)

class EssayInput(TypedDict):
    essay : str

class EssayState(EssayInput, total=False):
    language_feedback : str
    doa_feedback : str
    cot_feedback : str
    summarized_feedback : str
    individual_scores : Annotated[list[int], add]
    final_score : float

def evaluate_language(state: EssayState):
    out = EvaluationSchema.model_validate(structured_model.invoke(
        f"Evaluate the language quality of this essay and give feedback and a score out of 10:\n{state['essay']}"))
    return {"language_feedback": out.feedback, "individual_scores": [out.score]}

def evaluate_analysis(state: EssayState) :
    out = EvaluationSchema.model_validate(structured_model.invoke(
        f"Evaluate the depth of analysis of this essay and give feedback and a score out of 10:\n{state['essay']}"
    ))
    return {"doa_feedback" : out.feedback, "individual_scores" : [out.score]}

def evaluate_thought(state: EssayState):
    out = EvaluationSchema.model_validate(structured_model.invoke(
        f"Evaluate the clarity of thought of this essay and give feedback and a score out of 10:\n{state['essay']}"))
    return {"cot_feedback": out.feedback, "individual_scores": [out.score]}

def final_evaluation(state: EssayState):
    summary = model.invoke(
        "Summarize these feedbacks into one short overall feedback:\n"
        f"Language: {state.get('language_feedback', 'No language feedback available.')}\n"
        f"Depth of analysis: {state.get('doa_feedback', 'No analysis feedback available.')}\n"
        f"Clarity of thought: {state.get('cot_feedback', 'No clarity feedback available.')}"
    ).content
    scores = state.get("individual_scores", [])
    if not scores:
        return {"summarized_feedback": summary, "final_score": 0.0}
    return {"summarized_feedback": summary, "final_score": sum(scores) / len(scores)}

g = StateGraph(EssayState)
g.add_node("evaluate_language", evaluate_language)
g.add_node("evaluate_analysis", evaluate_analysis)
g.add_node("evaluate_thought", evaluate_thought)
g.add_node("final_evaluation", final_evaluation)

for n in ["evaluate_language", "evaluate_analysis", "evaluate_thought"]:
    g.add_edge(START, n)
    g.add_edge(n, "final_evaluation")
g.add_edge("final_evaluation", END)

workflow = g.compile()
result = workflow.invoke({"essay": "Concurrency in Java is the ability to execute multiple tasks during overlapping periods, improving application responsiveness and resource utilization. Java provides multithreading support through the Thread class, Runnable interface, and the Executor Framework. Multiple threads can perform independent tasks, such as processing requests, downloading files, or handling background operations. However, shared mutable data can cause race conditions when threads access or modify it simultaneously. Java provides synchronization using the synchronized keyword, locks, and atomic variables to maintain thread safety. The volatile keyword ensures visibility of variable updates across threads. Concurrent collections, such as ConcurrentHashMap, simplify safe data sharing. For scalable applications, thread pools and CompletableFuture help manage asynchronous tasks efficiently, reducing overhead and improving performance while requiring careful handling of synchronization and deadlocks."})
print(result["individual_scores"], result["final_score"])
print(result["summarized_feedback"])