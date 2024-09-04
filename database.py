import sqlite3
from datetime import datetime


def format_datetime_str(value):
    return datetime2str(datetime.strptime(str(value), "%Y%m%d%H%M"))


def datetime2str(value):
    return value.strftime("%Y-%m-%d %H:%M:%S")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect('database.db')
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS tasks (
                        task_id TEXT PRIMARY KEY,
                        context TEXT,
                        date LONG,
                        duration INTEGER
                    )
                    ''')
        self.conn.commit()

    def add_task(self, task_id, context, date, duration):
        date_str = format_datetime_str(date)

        self.cursor.execute('''
                INSERT INTO tasks (task_id, context, date, duration) VALUES (?, ?, ?, ?)
                ''', (task_id, context, date_str, duration))

        self.conn.commit()

    def show_all(self):
        self.cursor.execute('SELECT * FROM tasks')

        rows = self.cursor.fetchall()

        return rows

    def show_within_time(self, time, duration):
        current_time_str = format_datetime_str(time)

        query = '''
            SELECT *
            FROM tasks
            WHERE DATETIME(?) <= DATETIME(date)
            AND DATETIME(date, '+' || duration || ' minutes') <= DATETIME(?, '+' || ? || ' minutes')
            '''

        # SQL 쿼리 실행
        self.cursor.execute(query, (current_time_str, current_time_str, duration))
        rows = self.cursor.fetchall()

        return rows

    def update_task(self, task_id, element_name, value):
        if element_name == "context":
            value = str(value)
        elif element_name == "date":
            value = format_datetime_str(value)
        elif element_name == "duration":
            value = int(value)
        else:
            print(f"There is no element[{element_name}] in Table[tasks]")
            return

        self.cursor.execute(f'''
               UPDATE tasks SET {element_name} = ? WHERE task_id = ?
               ''', (value, task_id))

        self.conn.commit()

    def remove_task(self, task_id):
        self.cursor.execute('''
                    DELETE FROM tasks WHERE task_id = ?
                    ''', (task_id,))

        # 변경 사항을 저장합니다.
        self.conn.commit()

    def close(self):
        self.conn.close()


"""
db = Database()
db.create_table()
db.remove_task("test_task")
db.add_task("test_task", "test task", 202409031544, 90)
db.show_all()

result = db.show_within_time(202409011559, 165080)
print(result)

result = db.show_within_time(202409101544, 50)
print(result)

db.remove_task("test_task")
db.close()
"""