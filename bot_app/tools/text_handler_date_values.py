from datetime import datetime
from typing import Optional


class DateTextHandler:

    USER_DATE_VALUES_DICT = {
        "day": ["день", "дней", "дня"],
        "week": ["неделя", "недели", "недель"],
        "month": ["месяц", "месяца", "месяцев"],
        "year": ["год", "года", "лет"]
    }

    @staticmethod
    def validate_user_text(text: str, format_string: str = '%d-%m-%Y') -> bool:
        try:
            datetime.strptime(text, format_string)
        except ValueError:
            return False
        return True

    @staticmethod
    def get_date_type_for_db(text: str) -> Optional[str]:
        _format_string = '%d-%m-%Y'
        date_var = datetime.strptime(text, _format_string)
        return date_var.isoformat()

    @staticmethod
    def convert_values_to_date_str_format(text: str) -> Optional[str]:
        for key in DateTextHandler.USER_DATE_VALUES_DICT.keys():
            if text in DateTextHandler.USER_DATE_VALUES_DICT[key]:
                return key
        return
