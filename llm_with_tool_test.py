import json
from datetime import datetime
import os

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from openai import BaseModel
from pydantic import Field

load_dotenv()


@tool
def get_today():
    """Get today's date"""

    return datetime.today().strftime("%Y-%m-%d %H:%M")


@tool
def get_now():
    """Get the current time"""

    return datetime.now().strftime("%Y-%m-%d %H:%M")


class CreateTaskArgs(BaseModel):
    context: str = Field(description="Task's context")
    date: str = Field(description="Task's start time, format: %Y%m%d%H%M")
    duration: str = Field(description="Task's duration, format: %M")


@tool(args_schema=CreateTaskArgs)
def create_task(context, date, duration):
    """
    Make a task with context, date, duration
    """

    print(context, date, duration)


tools = [
    get_today,
    get_now,
    create_task
]

prompt = ChatPromptTemplate.from_messages([
    ("human", "{query}"),
])

model = ChatOpenAI(
    model=os.getenv("OPENAI_DEPLOYMENT"),
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.5,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

model = model.bind_tools(tools=tools, tool_choice="auto")
output_parser = StrOutputParser()


def execute_tool(tool_call):
    tool_map = {
        "get_today": get_today,
        "get_now": get_now,
        "create_task": create_task
    }

    tool_id = tool_call['id']
    name = tool_call['name']
    args = tool_call['args']

    output = tool_map[name].invoke(args)
    return {"id": tool_id, "name": name, "args": args, "output": output}


def invoke(user_input):
    messages = prompt.invoke({
        "query": user_input
    }).to_messages()

    while True:
        result = model.invoke(messages)
        messages.append(result)

        if result.response_metadata["finish_reason"] == "tool_calls":
            assert isinstance(result, AIMessage)
            for tool_call in result.tool_calls:
                tool_output = execute_tool(tool_call)
                messages.append(ToolMessage(
                    content=json.dumps(tool_output['output']),
                    tool_call_id=tool_call['id'],
                    name=tool_call['name']
                ))
        else:
            break

    return output_parser.invoke(result)


if __name__ == "__main__":
    while True:
        print(invoke(input("Input: ")))
