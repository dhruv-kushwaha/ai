from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import environ
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field

# 1. Take review from customer
# 2. Find out the sentiment
# 3. reply based on different sentiments

load_dotenv()

model = ChatOpenAI(
  base_url= environ["AZURE_OPENAI_ENDPOINT"],
  api_key= environ["AZURE_OPENAI_API_KEY"],
  model = "gpt-5-mini"
)

class SentimentSchema(BaseModel):
  sentiment : Literal["positive", "negative"] = Field(description="Sentiment of the review")

sentiment_model = model.with_structured_output(SentimentSchema)

class DiagnosisSchema(BaseModel):
  issue_type: Literal["UX", "Performance", "Bug", "Support", "Other"]
  tone: Literal["angry", "frustrated", "disappointed", "calm"]
  urgency: Literal["low", "medium", "high"]

diagnosis_model = model.with_structured_output(DiagnosisSchema)

class ReviewState(TypedDict):
  review : str
  sentiment : Literal["positive", "negative"]
  diagnosis : DiagnosisSchema


def find_sentiment(state: ReviewState):
  result = SentimentSchema.model_validate(
    sentiment_model.invoke(
      f"You are a human sentiment analysis expert and can identify the sentiments of people purchasing products like a psychlogist. Analyse the following sentiment and tell me about the sentiment of the person's review. \n {state['review']}"
      )
    )
  return {"sentiment" : result.sentiment}

def check_sentiment(state : ReviewState) -> Literal["positive_run", "run_diagnosis"]:
    return "positive_response" if state["sentiment"] == "positive" else "run_diagnosis"

def diagnose_review(state: ReviewState):
  result = DiagnosisSchema.model_validate(
      diagnosis_model.invoke(
        f"You are a product review analysis expert and can diagnose the review of people purchasing products like a psychlogist. Analyse the following review and give me a diagnosis of the person's review. \n {state['review']}"
        )
      )
  return {"diagnosis" : result}

def positive_response(state : ReviewState):
  result = model.invoke(
    f"You are a response agent who give responses back to the user for their positive reviews. Thank them for their review and "
  )

builder = StateGraph(ReviewState)
builder.add_node("sentiment_analysis", find_sentiment)
builder.add_edge(START, "sentiment_analysis")
builder.add_conditional_edges("sentiment_analysis", check_sentiment)
builder.add_edge("sentiment_analysis", END)

graph = builder.compile()

review = input("How was the product?")
result = graph.invoke({"review": review})


print(result)