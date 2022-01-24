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

    def _execute(self, query, values: tuple = None):
        cursor = self._get_cursor()
        cursor.execute(query, values)

    def get_users_telegram_ids(self):
        query = """SELECT telegram_id FROM planning_bot_user;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query)
            return cursor.fetchall()

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
        query = """SELECT t.id, t.task_name FROM tasks t 
        INNER JOIN deadline d ON t.id=d.task_id WHERE aim_id=%s 
        AND d.date_end IS Null ORDER BY t.id;"""
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

    def check_task_current_and_target_values(self, task_id: int) -> List[Tuple[Any, ...]]:
        query = """SELECT completed_from_target_value, target_value FROM tasks WHERE id=%s;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(task_id,))
            return cursor.fetchone()

    def get_tasks_status_by_aim_id(self, aim_id: int) -> List[Tuple[Any, ...]]:
        query = """SELECT task_name, description, completed_from_target_value, target_value, 
        TRUNC((cast(completed_from_target_value as decimal) / target_value * 100), 2)percent_complete 
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

    def select_deadline_by_task_id(self, task_id: int) -> List[Tuple[Any, ...]]:
        query = """SELECT * FROM deadline;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query, (task_id,))
            return cursor.fetchall()

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
        as residue_to_deadline FROM tasks t INNER JOIN deadline d ON t.id=d.task_id 
        WHERE aim_id=%s AND d.date_end IS NULL)td;
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
        WHERE aim_id=%s AND task_id=%s AND d.date_end IS NULL)td;
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

    def select_active_or_not_active_tasks_by_aim_id(self, aim_id: int, active: bool) -> List[tuple]:
        query = """SELECT * FROM tasks t INNER JOIN deadline d ON t.id = d.task_id
        WHERE active=%s AND aim_id=%s AND d.date_end IS NULL ORDER BY t.id;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active, aim_id,))
            return cursor.fetchall()

    def select_all_active_tasks_ids(self) -> List[tuple]:
        """Функция для получения активных тасков. if self.conn.closed используется
        для обхода проблемы с 'psycopg2.InterfaceError: connection already closed'.
        В связке celery+psycopg2 есть проблема с закрытием соединения. Эта функция
        является входной для celery приложения. В остальных функциях, которые осуществляют
        запросы к бд, которые работают после этой проблем не возникает.
        """
        query = """SELECT aim_id, id FROM tasks;
        """
        if self.conn.closed:
            cursor = self._get_cursor()
            cursor.execute(query=query)
            info = cursor.fetchall()
            cursor.close()
            return info
        else:
            with self.conn:
                cursor = self._get_cursor()
                cursor.execute(query=query)
                return cursor.fetchall()

    def select_all_active_or_not_active_tasks(self, active: bool) -> List[tuple]:
        query = """SELECT t.task_name, t.completed_from_target_value, 
        t.target_value, d.date_start, d.deadline
        FROM tasks t INNER JOIN deadline d ON t.id = d.task_id
        WHERE active=%s AND d.date_end IS NULL ORDER BY t.id;"""
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active,))
            return cursor.fetchall()

    def set_aim_status_active(self, aim_id: int) -> str:
        query = """
        UPDATE aims SET active=True WHERE id=%s RETURNING aim_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(aim_id,))
            aim_name = cursor.fetchone()[0]
            return aim_name

    def set_aim_status_not_active(self, aim_id: int) -> str:
        query = """
        UPDATE aims SET active=False WHERE id=%s RETURNING aim_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(aim_id,))
            aim_name = cursor.fetchone()[0]
            return aim_name

    def set_task_status(self, task_id: int, active: bool) -> str:
        query = """
        UPDATE tasks SET active=%s WHERE id=%s RETURNING task_name;
        """
        with self.conn:
            cursor = self._get_cursor()
            cursor.execute(query=query, vars=(active, task_id,))
            task_name = cursor.fetchone()[0]
            return task_name

    def set_task_status_not_active_by_aim_id(self, aim_id: int):
        query = """
        UPDATE tasks SET active=False WHERE aim_id=%s;
        """
        with self.conn:
            self._execute(query=query, values=(aim_id,))

    def insert_result_for_active_task(self, task_id, result: int):
        query = """UPDATE tasks SET 
        completed_from_target_value=completed_from_target_value+%s WHERE id=%s;
        """
        with self.conn:
            self._execute(query=query, values=(result, task_id,))

    def update_deadline_date_end(self, task_id: int):
        query = """UPDATE deadline SET date_end=CURRENT_DATE WHERE task_id=%s;
        """
        with self.conn:
            self._execute(query=query, values=(task_id,))

    def insert_into_task_results_by_day(self, task_id: int, result: int = None):
        query = """INSERT INTO task_results_for_day(task_id, date, result) 
        VALUES(%s, CURRENT_DATE, %s)
        """
        with self.conn:
            self._execute(query=query, values=(task_id, result))
