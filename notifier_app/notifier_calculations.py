from db.db_functions import DbFunctions


class NotifierCalculations:

    def __init__(self, db: DbFunctions):
        self.db = db

    def _get_target_value(self, aim_id: int, task_id: int, value_to_divide: int):
        return self.db.select_task_statistics(
            aim_id=aim_id,
            task_id=task_id,
            value_for_division=value_to_divide
        )

    def get_notification_to_send(self, aim_id: int, task_id: int, value_to_divide: int):
        target_value_info = self._get_target_value(
            aim_id=aim_id,
            task_id=task_id,
            value_to_divide=value_to_divide
        )
        tv_task_id, tv_task_name, tv_target_value, tv_residue_value, \
        tv_residue_days_or_weeks, tv_target_by_period = target_value_info
        if value_to_divide == 1:
            text = f"Целевые показатели на день для задачи {tv_task_name}:\n" \
                   f"Целевое значение: {tv_target_value}\n" \
                   f"Осталось до целевого значения: {tv_residue_value}\n" \
                   f"Осталось до дедлайна: {tv_residue_days_or_weeks}\n" \
                   f"За день нужно сделать: {tv_target_by_period}"
            return text
        elif value_to_divide == 7:
            text = f"Целевые показатели на неделю для задачи {tv_task_name}:\n" \
                   f"Целевое значение: {tv_target_value}\n" \
                   f"Осталось до целевого значения: {tv_residue_value}\n" \
                   f"Осталось недель до дедлайна: {tv_residue_days_or_weeks}\n" \
                   f"За неделю нужно сделать: {tv_target_by_period}"
            return text
