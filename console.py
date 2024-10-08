import shlex
import uuid

import llm
from database import Database


def init():
    global db
    db = Database()
    db.create_table()


def execute_command(command):
    command = command.split("/")[1]
    tokens = shlex.split(command)

    opcode = tokens[0]
    output = ""
    if opcode == "create":
        name = tokens[1]
        date = tokens[2]
        duration = tokens[3]

        task_id = str(uuid.uuid4())
        db.add_task(task_id, name, date, duration)
        output = f"Created task[{task_id}]"
    elif opcode == "list":
        if len(tokens) <= 2:
            tasks = db.show_all()
        else:
            start_date = tokens[1]
            end_date = tokens[2]

            tasks = db.show_within_time(start_date, end_date)
        output = tasks
    elif opcode == "edit":
        task_id = tokens[1]
        element_name = tokens[2]
        value = tokens[3]

        db.update_task(task_id, element_name, value)
        output = f"updated task[{task_id}]"
    elif opcode == "remove":
        task_id = tokens[1]

        db.remove_task(task_id)
        output = f"Removed task[{task_id}]"
    elif opcode == "exit":
        db.close()
        output = "closed the database"

    return output


def llm_input(user_input):
    result = llm.invoke(user_input)
    print(result)


def main():
    is_end = False
    while not is_end:
        user_input = input("Input: ")
        if user_input.startswith("/"):
            output = execute_command(user_input)
            print(output)
        else:
            llm_input(user_input)


if __name__ == "__main__":
    init()
    main()
