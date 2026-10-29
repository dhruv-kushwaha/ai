from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from os import environ as env
from pydantic import SecretStr

prompt = ChatPromptTemplate.from_template("Answer in one line: {question}")
model = model = ChatOpenAI(
    base_url= env["AZURE_OPENAI_ENDPOINT"],
    api_key= SecretStr(env["AZURE_OPENAI_API_KEY"]),
    model="gpt-6-luna",
)
chain = prompt | model | StrOutputParser()

print(chain.invoke({"question": "What is observability?"}))