from typing import List, Tuple, Any

import psycopg2 as pg

from environs import Env

env = Env()
env.read_env()


class DbFunctions:

    def __init__(self):
        self.conn = pg.connect(
            database=env('BOT_DB_NAME', ''),
            user=env('BOT_DB_USER', ''),
            password=env('BOT_DB_PASSWORD', ''),
            host=env('BOT_DB_HOST', ''),
            port=env('BOT_DB_PORT', ''),
        )

    def _get_cursor(self):
        return self.conn.cursor()

    def _execute(self, query, values=None):
        cursor = self._get_cursor()
        cursor.execute(query, values)

    def find_user_by_email(self, email_to_check: str, values: tuple = None):
        query = """SELECT name, surname, email, telegram_id FROM planning_bot_user WHERE email = '%s';""" \
                % (email_to_check,)
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query, values)
            return cursor.fetchone()

    def insert_bot_user_info(self, name: str, lastname: str, email: str, telegram_id: int):
        query = """INSERT INTO planning_bot_user(name, surname, email, telegram_id) VALUES(%s, %s, %s, %s);
        """
        with self.conn:
            self._execute(query, (name, lastname, email, telegram_id,))

    def insert_aim(self, aim_value: str):
        query = """INSERT INTO aims(aim_name) VALUES (%s);"""
        with self.conn:
            self._execute(query, (aim_value,))

    def get_all_aims_info(self) -> List[Tuple[Any, ...]]:
        query = """SELECT * FROM aims;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def get_all_aims_ids_and_names(self) -> List[Tuple[Any, ...]]:
        query = """SELECT id, aim_name FROM aims;"""
        with self.conn as conn:
            cursor = self._get_cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def get_aims_status(self) -> List[Tuple[Any, ...]]:
        query = """SELECT aim_name, completed, aim_deadline FROM aims;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def get_tasks_status_by_aim_id(self, aim_id: int) -> List[Tuple[Any, ...]]:
        query = """SELECT task_name, description, completed_from_target_value, target_value, 
        TRUNC((cast(completed_from_aim_value as decimal) / aim_value * 100), 2)percent_complete 
        FROM tasks WHERE aim_id=%s;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query, (aim_id,))
            return cursor.fetchall()

    def insert_task(self, task_name: str, aim_id: int, description: str,
                    target_value: int = None, completed_from_target_value=0) -> int:
        query = """INSERT INTO tasks(task_name, description, aim_id, completed_from_target_value,
        target_value) VALUES(%s, %s, %s, %s, %s) RETURNING id"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query, (task_name, description, aim_id, completed_from_target_value, target_value,))
            task_id = cursor.fetchone()[0]
            return task_id

    def insert_deadline(self, deadline: str, task_id: int):
        query = """INSERT INTO deadline(deadline, task_id) VALUES(%s, %s)"""
        with self.conn:
            self._execute(query=query, values=(deadline, task_id,))
