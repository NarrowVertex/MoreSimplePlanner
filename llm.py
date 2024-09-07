import json
import uuid
from datetime import datetime, timedelta, time
import os
from typing import Tuple

from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
from openai import BaseModel
from pydantic import Field

from database import Database

load_dotenv()


@tool
def get_today():
    """Get today's date and day of the week"""

    return datetime.today().strftime("%Y-%m-%d %H:%M %A")


@tool
def get_now():
    """Get the current time and day of the week"""

    return datetime.now().strftime("%Y-%m-%d %H:%M %A")


class GetPeriodicDaysArgs(BaseModel):
    start_date: str = Field(description="Start date, format: %Y-%m-%d %H:%M")
    end_date: str = Field(description="End date, format: %Y-%m-%d %H:%M")
    interval_day: str = Field(description="Interval of periodic days, format: %d")


@tool(args_schema=GetPeriodicDaysArgs)
def get_periodic_days(start_date, end_date, interval_day):
    """Get periodic date list from start_date to end_date as interval_day"""
    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    interval_day = int(interval_day)

    periodic_days = []

    current_date = start_date

    while current_date <= end_date:
        periodic_days.append(current_date.strftime("%Y-%m-%d %H:%M"))
        current_date += timedelta(days=interval_day)

    return str(periodic_days)


class GetSpecificWeekdaysArgs(BaseModel):
    start_date: str = Field(description="Start date, format: %Y-%m-%d %H:%M")
    end_date: str = Field(description="End date, format: %Y-%m-%d %H:%M")
    weekday_list: list = Field(description="List of desired weekdays, format: [weekday1(str), weekday2(str)]")


@tool(args_schema=GetSpecificWeekdaysArgs)
def get_specific_weekdays(start_date: str, end_date: str, weekday_list: list):
    """Get a list of dates between start_date and end_date that fall on the specified weekdays."""

    weekday_map = {
        "Monday": 0,
        "Tuesday": 1,
        "Wednesday": 2,
        "Thursday": 3,
        "Friday": 4,
        "Saturday": 5,
        "Sunday": 6
    }
    weekday_list = [weekday_map[x] for x in weekday_list]

    start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
    end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")

    selected_days = []

    current_date = start_date

    print(weekday_list, current_date.weekday())
    while current_date <= end_date:
        if current_date.weekday() in weekday_list:
            selected_days.append(current_date.strftime("%Y-%m-%d %H:%M"))
        current_date += timedelta(days=1)

    return selected_days


class CreateTaskArgs(BaseModel):
    name: str = Field(description="Task's name")
    date: str = Field(description="Task's start time, format: %Y%m%d%H%M")
    duration: str = Field(description="Task's duration, format: %M")


db = Database()
db.create_table()


@tool(args_schema=CreateTaskArgs)
def create_task(name, date, duration):
    """
    Make a task with name, date, duration
    """

    task_id = str(uuid.uuid4())
    db.add_task(task_id, name, date, duration)
    output = f"Created task[{task_id}]"
    return output


class CreateTaskArgs(BaseModel):
    task_list: list = Field(description="""
    format: list[tuple(name(str), date(str), duration(str)), ]
    Task list that contains tasks what you want to createTask's name
    task_list[tuple(name, date, duration), ...] # list and tuple, not dict
        name(str): Task's name
        date(str): Task's start time, format: %Y%m%d%H%M
        duration(str): Task's duration, format: %M
    """)


@tool(args_schema=CreateTaskArgs)
def create_tasks(task_list):
    """
    Make tasks with a task_list which contains multiple name, date, duration
    """

    tasks = []
    for task in task_list:
        if isinstance(task, dict):
            name = task['name']
            date = task['date']
            duration = task['duration']
        else:
            name = task[0]
            date = task[1]
            duration = task[2]

        task_id = str(uuid.uuid4())
        tasks.append((task_id, name, date, duration))
    db.add_tasks(tasks)

    output = f"Created [{len(task_list)}] tasks"
    return output


@tool
def list_task():
    """
    Get all tasks
    """

    tasks = db.show_all()
    output = str(tasks)
    return output


class ListWithinDateArgs(BaseModel):
    start_date: str = Field(description="start date you want to get the tasks from this time onwards, format: %Y-%m-%d")
    end_date: str = Field(description="end date you want to get the tasks before this time, format: %Y-%m-%d")


@tool(args_schema=ListWithinDateArgs)
def list_within_date(start_date, end_date):
    """
    Get tasks set between start_date and end_date
    """
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    end_date = datetime.combine(end_date, time(23, 59))

    tasks = db.show_within_time(
        start_date.strftime("%Y%m%d%H%M"),
        end_date.strftime("%Y%m%d%H%M")
    )

    output = f"Found {len(tasks)} tasks within {start_date} and {end_date} \n"
    output += f"{tasks}"
    return output


class RemoveTaskArgs(BaseModel):
    task_id_list: list[str] = Field(description="list of tasks' id that you want to delete, task id type: uuid4")


@tool(args_schema=RemoveTaskArgs)
def remove_task(task_id_list):
    """
    Remove tasks by task id list
    """
    for task_id in task_id_list:
        db.remove_task(task_id)
    output = f"Removed {len(task_id_list)} tasks successfully"
    return output


class EditTaskArgs(BaseModel):
    task_id: str = Field(description="Task's id, format: uuid4")
    element_name: str = Field(description="value name of task which you want to edit")
    value: str = Field(description="value you want to upload")


@tool(args_schema=EditTaskArgs)
def edit_task(task_id, element_name, value):
    """
    Edit task information by task_id, element_name, value
    """

    db.update_task(task_id, element_name, value)
    output = f"Updated {task_id} successfully"
    return output


class EditTasksArgs(BaseModel):
    task_list: list = Field(description="""
    format: list[tuple(task_id(str), element_name(str), value(str)), ]
    Task list that contains tasks that you want to edit
    task_list[(task_id, element_name, value), ...]
        task_id(str): Task's id, format: uuid4
        element_name(str): value name of task which you want to edit
        value(str): value you want to upload
    """)


@tool(args_schema=EditTasksArgs)
def edit_tasks(task_list):
    """
    Edit tasks with a task_list which contains multiple task_id, element_name, value
    """
    tasks = []
    for task in task_list:
        if isinstance(task, dict):
            task_id = task['task_id']
            element_name = task['element_name']
            value = task['value']
        else:
            task_id = task[0]
            element_name = task[1]
            value = task[2]

        tasks.append((task_id, element_name, value))

    db.update_tasks(task_list)
    output = f"Updated {len(task_list)} tasks successfully"
    return output


tools = [
    get_today,
    get_now,
    get_periodic_days,
    get_specific_weekdays,
    create_task,
    create_tasks,
    list_task,
    list_within_date,
    remove_task,
    edit_task,
    edit_tasks
]

tool_map = {
    "get_today": get_today,
    "get_now": get_now,
    "get_periodic_days": get_periodic_days,
    "get_specific_weekdays": get_specific_weekdays,
    "create_task": create_task,
    "create_tasks": create_tasks,
    "list_task": list_task,
    "list_within_date": list_within_date,
    "remove_task": remove_task,
    "edit_task": edit_task,
    "edit_tasks": edit_tasks
}

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    you are an assistant.
    As user's query, you can do what user need with basic data and tools.
    """),
    ("system", """
    Basic data:
    today date: {today_date}
    now time: {now_time}
    """),
    ("human", "{query}")
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
    tool_id = tool_call['id']
    name = tool_call['name']
    args = tool_call['args']

    output = tool_map[name].invoke(args)
    return {"id": tool_id, "name": name, "args": args, "output": output}


def invoke(user_input):
    messages = prompt.invoke({
        "today_date": datetime.today().strftime("%Y-%m-%d %A"),
        "now_time": datetime.now().strftime("%H:%M"),
        "query": user_input
    }).to_messages()

    while True:
        result = model.invoke(messages)
        messages.append(result)

        if result.response_metadata["finish_reason"] == "tool_calls":
            assert isinstance(result, AIMessage)
            for tool_call in result.tool_calls:
                print("call tool: ", tool_call['name'])

                tool_output = execute_tool(tool_call)
                messages.append(ToolMessage(
                    content=json.dumps(tool_output['output']),
                    tool_call_id=tool_call['id'],
                    name=tool_call['name']
                ))
        else:
            break

    return output_parser.invoke(result)
