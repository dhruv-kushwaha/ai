from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from os import environ as env
from pydantic import SecretStr

load_dotenv()

class EvaluationSchema(BaseModel):
    feedback: str = Field(description="Detailed feedback for the essay")
    score: int = Field(description="Score out of 10", ge=0, le=10)
    improvements: list[str] = Field(description="Top 3 concrete improvements")

model = ChatOpenAI(
    base_url= env["AZURE_OPENAI_ENDPOINT"],
    api_key= SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-5-mini",
)
structured_model = model.with_structured_output(EvaluationSchema)

essay = "India is a big country with many peoples and it have many culture."
result = structured_model.invoke(
    f"Evaluate the language quality of this essay and give a score out of 10:\n\n{essay}"
)

print(type(result))
print(result.model_dump())