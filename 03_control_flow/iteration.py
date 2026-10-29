import operator
from typing import TypedDict, Literal, Annotated
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from os import environ as env
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    base_url= env["AZURE_OPENAI_ENDPOINT"],
    api_key= SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)

class TweetEvaluation(BaseModel):
    evaluation: Literal["approved", "needs_improvement"] = Field(..., description="Final evaluation result.")
    feedback: str = Field(..., description="Feedback for the tweet.")

evaluator = llm.with_structured_output(TweetEvaluation)

class TweetState(TypedDict):
    topic: str
    tweet: str
    evaluation: Literal["approved", "needs_improvement"]
    feedback: str
    iteration: int
    max_iteration: int
    tweet_history: Annotated[list[str], operator.add]
    feedback_history: Annotated[list[str], operator.add]

def generate_tweet(state: TweetState):
    msgs = [SystemMessage(content="You are a funny and clever Twitter/X influencer."),
            HumanMessage(content=f'Write a short, original, hilarious tweet on: "{state["topic"]}". '
                                 "No Q&A format. Max 280 characters. Observational humor.")]
    r = llm.invoke(msgs).content
    return {"tweet": r, "tweet_history": [r]}

def evaluate_tweet(state: TweetState):
    msgs = [
    SystemMessage(content="You are a ruthless Twitter critic."),
    HumanMessage(content=(
        f'Evaluate: "{state["tweet"]}". Criteria: originality, humor, punchiness, '
        "virality, format. Auto-reject Q&A format, over 280 chars, or weak endings. "
        "Respond ONLY with: evaluation (approved or needs_improvement) and feedback "
        "(one short paragraph of strengths and weaknesses). Do NOT write rewrites."
    )),
]
    r = TweetEvaluation.model_validate(evaluator.invoke(msgs))
    return {"evaluation": r.evaluation, "feedback": r.feedback, "feedback_history": [r.feedback]}

def optimize_tweet(state: TweetState):
    msgs = [
    SystemMessage(content="You punch up tweets based on feedback."),
    HumanMessage(content=(
        f'Feedback: "{state["feedback"]}"\nTopic: "{state["topic"]}"\n'
        f'Original: {state["tweet"]}\nRewrite it. Under 280 characters. '
        "Return ONLY the final tweet text. No options, no labels, no commentary."
    )),
]
    r = llm.invoke(msgs).content
    return {"tweet": r, "iteration": state["iteration"] + 1, "tweet_history": [r]}

def route_evaluation(state: TweetState):
    if state["evaluation"] == "approved" or state["iteration"] >= state["max_iteration"]:
        return "approved"
    return "needs_improvement"

g = StateGraph(TweetState)
g.add_node("generate", generate_tweet)
g.add_node("evaluate", evaluate_tweet)
g.add_node("optimize", optimize_tweet)
g.add_edge(START, "generate")
g.add_edge("generate", "evaluate")
g.add_conditional_edges("evaluate", route_evaluation, {"approved": END, "needs_improvement": "optimize"})
g.add_edge("optimize", "evaluate")
workflow = g.compile()

result = workflow.invoke({"topic": "Indian Railways", "iteration": 1, "max_iteration": 3})
print(result["evaluation"], result["iteration"], len(result["tweet_history"]))
for i, (t, f) in enumerate(zip(result["tweet_history"], result["feedback_history"]), 1):
    print(f"\nRound {i}\n  tweet: {t}\n  feedback: {f}")