import shlex
import uuid

from database import Database


def init():
    global db
    db = Database()
    db.create_table()


def execute_command(command):
    tokens = shlex.split(command)

    opcode = tokens[0]
    if opcode == "create":
        context = tokens[1]
        date = tokens[2]
        duration = tokens[3]

        db.add_task(str(uuid.uuid4()), context, date, duration)
    elif opcode == "list":
        if len(tokens) <= 2:
            tasks = db.show_all()
        else:
            date = tokens[1]
            duration = tokens[2]

            tasks = db.show_within_time(date, duration)
        print(tasks)
    elif opcode == "edit":
        task_id = tokens[1]
        element_name = tokens[2]
        value = tokens[3]

        db.update_task(task_id, element_name, value)
    elif opcode == "remove":
        task_id = tokens[1]

        db.remove_task(task_id)
    elif opcode == "exit":
        db.close()
        return True

    return False


def llm(user_input):
    pass


def main():
    is_end = False
    while not is_end:
        user_input = input("Input: ")
        if user_input.startswith("/"):
            is_end = execute_command(user_input.split("/")[1])
        else:
            llm(user_input)


if __name__ == "__main__":
    init()
    main()
