from db.db_functions import DbFunctions


class DbDataHandler:

    def __init__(self, db: DbFunctions):
        self.db = db

    def _get_aims_status_dict(self) -> dict:
        result = {}
        raw_aims_status = self.db.get_aims_status()
        for n, aim_tuple in enumerate(raw_aims_status, start=1):
            aim_name, completed, deadline = aim_tuple
            result.update(
                {
                    n:
                        {
                            "aim_name": aim_name,
                            "completed": completed,
                            "deadline": deadline
                        }
                }
            )
        return result

    def _get_tasks_status_dict(self, aim_id: int) -> dict:
        result = {}
        raw_tasks_status_by_aim_id = self.db.get_tasks_status_by_aim_id(aim_id)
        for n, tasks_tuple in enumerate(raw_tasks_status_by_aim_id, start=1):
            task_name, description, completed, aim_value, percent_complete = tasks_tuple
            result.update(
                {
                    n:
                        {
                            "task_name": task_name,
                            "description": description,
                            "completed": completed,
                            "aim_value": aim_value,
                            "percent_complete": percent_complete
                        }
                }
            )
        return result

    def get_aims_status_string(self) -> str:
        aims_status_dict = self._get_aims_status_dict()
        aims_status_string = ""
        for n, value in aims_status_dict.items():
            aim_name = value.get("aim_name")
            completed = value.get("completed")
            deadline = value.get("deadline")
            aim_string = f'{n}. aim_name: {aim_name},  completed: {completed}, deadline: {deadline}\n'
            aims_status_string += aim_string
        return aims_status_string

    def get_tasks_status_string(self, aim_id: int) -> str:
        tasks_status_dict = self._get_tasks_status_dict(aim_id)
        tasks_status_string = ""
        for n, value in tasks_status_dict.items():
            task_name = value.get("task_name")
            description = value.get("description")
            completed = value.get("completed")
            aim_value = value.get("aim_value")
            percent_complete = value.get("percent_complete")
            tasks_string = f'{n}. Задача № {n}\naim_name: {task_name}\ndescription: {description}\n' \
                           f'completed: {completed}\naim_value: {aim_value}\n' \
                           f'percent_complete: {percent_complete}\n'
            tasks_status_string = tasks_status_string + tasks_string
        return tasks_status_string
