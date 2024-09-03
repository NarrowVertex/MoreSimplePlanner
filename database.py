import sqlite3

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
        self.cursor.execute('''
                INSERT INTO tasks (task_id, context, date, duration) VALUES (?, ?, ?, ?)
                ''', (task_id, context, date, duration))

        self.conn.commit()

    def show_all(self):
        self.cursor.execute('SELECT * FROM tasks')

        rows = self.cursor.fetchall()

        print(f"found data: {len(rows)}")
        for row in rows:
            print(row)

    def remove_task(self, task_id):
        self.cursor.execute('''
                    DELETE FROM tasks WHERE task_id = ?
                    ''', ("test_task",))

        # 변경 사항을 저장합니다.
        self.conn.commit()

    def close(self):
        self.conn.close()


db = Database()
db.create_table()
db.add_task("test_task", "test task", 202409031544, 90)
db.show_all()
db.remove_task("test_task")
db.close()