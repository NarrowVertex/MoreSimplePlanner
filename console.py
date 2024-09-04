def execute_command(command):
    pass


def llm(user_input):
    pass


def main():
    while True:
        user_input = input("Input: ")
        if user_input.startswith("\\"):
            execute_command(user_input.split("\\")[1])
        else:
            llm(user_input)


if __name__ == "__main__":
    main()
