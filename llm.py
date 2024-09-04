import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_template("""
{input}
""")

model = ChatOpenAI(
    model=os.getenv("OPENAI_DEPLOYMENT"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

output_parser = StrOutputParser()

chain = prompt | model | output_parser


def llm(user_input):
    result = chain.invoke({
        "input": user_input
    })
    print(result)
