import os

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv

load_dotenv()

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are an assistant.
By the following the command manual, create commands that the user want.
You have to create just a one command.

And you can get the output by commands you created.
By that, you can request information you need to operate some missions.
If you seems the user's request is already completed, say just END.

You can just answer commands only, don't need to say the other words.
And don't need any symbols like ```, $ but only /, END

There are absolute words:
/create, /list, /remove, /edit

This words can't be modified in any situation.
    """),
    ("system", """
/create "context" date duration
create task with 'context', 'date' and 'duration'
'context' is what the task is
'date' is when the task starts, the format is 'YYYYmmddHHMM'
'duration' is a time that the task spends, the format is interger by minute

/list
show all tasks
output would be like this:
[('task_id', 'context', 'date', duration)]

/list date duration
show all tasks which the date is between date and date + duration
output would be like this:
[('task_id', 'context', 'date', duration)

/remove task_id
remove task by task_id
you can get task_id by '/list' or '/list date duration' command

/edit task_id element_name value
edit task information
element_name is like 'context', 'date' and 'duration'
value is what be updated to element
    """),
    ("human", "user input: {query}"),
    ("system", """
Output for the command you create: 
{information}
    """)
])

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


def invoke(user_input, information):
    result = chain.invoke({
        "query": user_input,
        "information": information
    })
    return result
