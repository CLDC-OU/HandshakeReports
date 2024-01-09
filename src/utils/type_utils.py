
import re
from utils.general_utils import list_to_regex_includes


class FilterType():
    def __init__(self, include: list[str] | str | None, exclude: list[str] | str | None) -> None:
        self.include = include
        self.exclude = exclude

    @staticmethod
    def get_set(input: str | list[str] | None) -> set[str]:
        if input is None:
            return set()
        if isinstance(input, str):
            return set(input.split(","))
        if isinstance(input, list):
            return set(input)
        return set()

    def get_include(self) -> re.Pattern[str]:
        return list_to_regex_includes(FilterType.get_set(self.include))

    def get_exclude(self) -> re.Pattern[str]:
        return list_to_regex_includes(FilterType.get_set(self.exclude))
