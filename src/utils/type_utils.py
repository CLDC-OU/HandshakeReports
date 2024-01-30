import logging
from src.utils.general_utils import list_to_regex_includes


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

    @staticmethod
    def get_include_exclude(dictionary: dict, key: str, log: bool = False, config_file: str = "", report_index: int = 0, report_type: str = "") -> "FilterType":

        # Check for key in dictionary
        if key not in dictionary:
            if log:
                logging.warning(
                    f"WARNING! \"{key}\" key not present for {report_type} report in {config_file} at index {report_index}. Setting to default including all")
            return FilterType(None, None)
        val = dictionary[key]

        # Check for None value
        if val is None:
            if log:
                logging.warning(
                    f"WARNING! \"{key}\" key not present for {report_type} report in {config_file} at index {report_index}. Setting to default including all")
            return FilterType(None, None)

        # Get include values
        if "include" not in val:
            if log:
                logging.warning(
                    f"WARNING! \"include\" key for \"{key}\" not present for {report_type} report in {config_file} at index {report_index}. Setting to default including all")
            include = None
        else:
            include = val["include"]
            if include == "" or include == []:
                include = None

        # Get exclude values
        if "exclude" not in val:
            if log:
                logging.warning(
                    f"WARNING! \"exclude\" key for \"{key}\" not present for {report_type} report in {config_file} at index {report_index}. Setting to default including all")
            exclude = None
        else:
            exclude = val["exclude"]
            if exclude == "" or exclude == []:
                exclude = None

        return FilterType(include, exclude)

    def get_include(self) -> str:
        if self.include is None:
            return ".*?"
        return list_to_regex_includes(FilterType.get_set(self.include)).pattern

    def get_exclude(self) -> str:
        if self.exclude is None:
            return "a^"
        return list_to_regex_includes(FilterType.get_set(self.exclude)).pattern
