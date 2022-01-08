import re
from typing import List, Union, Optional

from environs import Env


class UserTextParser:

    def __init__(self):
        env = Env()
        env.read_env()

        self.re_text_format_parse = env.str("RE_FOR_DATE_LETTERS")
        self.re_date_format_parse = env.str("RE_FOR_DATE_DATETIME_FORMAT")

    def parse_text(self, text: str) -> Optional[Union[str, List[str]]]:
        re_text_format = re.findall(pattern=self.re_text_format_parse, string=text)
        re_text_format = [i for i in re_text_format if i]
        if re_text_format:
            return re_text_format
        re_date_format = re.search(pattern=self.re_date_format_parse, string=text)
        if re_date_format:
            return re_date_format.group()
        return

    @staticmethod
    def get_parsed_values_list(parsed_list: List[str]) -> Union[List[str], str]:
        if len(parsed_list) < 3:
            return [i for i in parsed_list[0].split() if i]
        return "Внесено больше 1 срока исполненеия задачи. Нужно занаво внести данные о сроке выполнения задачи"
