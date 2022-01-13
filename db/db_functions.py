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
        query = """SELECT id, aim_name FROM aims ORDER BY id;"""
        with self.conn as conn:
            cursor = self._get_cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def get_all_tasks_ids_and_names_by_aim_id(self, aim_id: int) -> List[Tuple[Any, ...]]:
        query = """SELECT id, task_name FROM tasks WHERE aim_id=%s ORDER BY id;"""
        with self.conn as conn:
            cursor = self._get_cursor()
            cursor.execute(query, (aim_id,))
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

    def select_aim_statistics(self, aim_id: int, value_for_division: int = 1) -> List[tuple]:
        query = """SELECT td.id, td.task_name, td.residue_target_value, residue_to_deadline, 
        TRUNC((cast(td.residue_target_value as decimal) / td.residue_to_deadline), 2)
        as target_value_per_week FROM (SELECT t.id, t.task_name, 
        (t.target_value - t.completed_from_target_value)as residue_target_value, 
        TRUNC(cast((deadline - CURRENT_DATE) as decimal) / %s ,2)
        as residue_to_deadline FROM tasks t INNER JOIN deadline d ON t.id=d.task_id WHERE aim_id=%s)td;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(value_for_division, aim_id,))
            return cursor.fetchall()

    def select_task_statistics(self, aim_id: int, task_id: int,
                               value_for_division: int = 1) -> List[tuple]:
        query = """SELECT td.id, td.task_name, td.residue_target_value, residue_to_deadline, 
        TRUNC((cast(td.residue_target_value as decimal) / td.residue_to_deadline), 2)
        as target_value_per_week FROM (SELECT t.id, t.task_name, 
        (t.target_value - t.completed_from_target_value)as residue_target_value, 
        TRUNC(cast((deadline - CURRENT_DATE) as decimal) / %s ,2)
        as residue_to_deadline FROM tasks t INNER JOIN deadline d ON t.id=d.task_id 
        WHERE aim_id=%s and task_id=%s)td;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(value_for_division, aim_id, task_id,))
            return cursor.fetchone()

    def select_active_or_not_active_aims(self, active: bool) -> List[tuple]:
        query = """SELECT id, aim_name, aim_deadline FROM aims WHERE active=%s ORDER BY id;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active,))
            return cursor.fetchall()

    def select_active_or_not_active_tasks(self, aim_id: int, active: bool) -> List[tuple]:
        query = """SELECT * FROM tasks WHERE active=%s and aim_id=%s ORDER BY id;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active, aim_id,))
            return cursor.fetchall()

    def select_all_active_or_not_active_tasks(self, active: bool):
        query = """SELECT task_name FROM tasks WHERE active=%s ORDER BY id;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active,))
            return cursor.fetchall()

    def set_aim_status_active(self, aim_id: int):
        query = """
        UPDATE aims SET active=True WHERE id=%s RETURNING aim_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(aim_id,))
            aim_name = cursor.fetchone()[0]
            return aim_name

    def set_aim_status_not_active(self, aim_id: int):
        query = """
        UPDATE aims SET active=False WHERE id=%s RETURNING aim_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(aim_id,))
            aim_name = cursor.fetchone()[0]
            return aim_name

    def set_task_status_active(self, task_id: int):
        query = """
        UPDATE tasks SET active=True WHERE id=%s RETURNING task_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(task_id,))
            task_name = cursor.fetchone()[0]
            return task_name

    def set_task_status_not_active(self, task_id: int):
        query = """
        UPDATE tasks SET active=False WHERE id=%s RETURNING task_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(task_id,))
            task_name = cursor.fetchone()[0]
            return task_name

    def set_task_status_not_active_by_aim_id(self, aim_id: int):
        query = """
        UPDATE tasks SET active=False WHERE aim_id=%s;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(aim_id,))
