import sqlite3
from datetime import datetime


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
        date = datetime.strptime(str(date), "%Y%m%d%H%M")
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('''
                INSERT INTO tasks (task_id, context, date, duration) VALUES (?, ?, ?, ?)
                ''', (task_id, context, date_str, duration))

        self.conn.commit()

    def show_all(self):
        self.cursor.execute('SELECT * FROM tasks')

        rows = self.cursor.fetchall()

        print(f"found data: {len(rows)}")
        for row in rows:
            print(row)

    def show_within_time(self, time, duration):
        current_time = datetime.strptime(str(time), "%Y%m%d%H%M")
        current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

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

    def remove_task(self, task_id):
        self.cursor.execute('''
                    DELETE FROM tasks WHERE task_id = ?
                    ''', ("test_task",))

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