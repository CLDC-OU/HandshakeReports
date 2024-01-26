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


class DepartmentFilter():
    def __init__(self, name: str, valid_appointments: FilterType):
        self.name = name
        self.valid_appointments = valid_appointments

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("name must be a string")
        self._name = value

    @property
    def valid_appointments(self) -> FilterType:
        return self._valid_appointments

    @valid_appointments.setter
    def valid_appointments(self, value: FilterType) -> None:
        if not isinstance(value, FilterType):
            raise ValueError("valid_appointments must be a FilterType")
        self._valid_appointments = value


class DepartmentsFilter():
    def __init__(self, departments: list[dict] | None = None):
        self.departments = departments
        self.current_department = 0

    def __next__(self):
        if self.current_department >= len(self):
            raise StopIteration
        else:
            self.current_department += 1
            return self.departments[self.current_department - 1]

    def __len__(self):
        return len(self.departments)

    def __getitem__(self, key):
        return self.departments[key]

    def get_department_by_name(self, name: str) -> DepartmentFilter | None:
        for department in self.departments:
            if department.name == name:
                return department
        return None

    def get_filter_by_name(self, name: str) -> FilterType:
        department = self.get_department_by_name(name)
        if department is None:
            return FilterType(None, None)
        return department.valid_appointments

    @property
    def departments(self) -> list[DepartmentFilter]:
        return self._departments

    @departments.setter
    def departments(self, value: list[dict] | None) -> None:
        if value is None:
            self._departments = [DepartmentFilter("default", FilterType(None, None))]
            return

        if not isinstance(value, list):
            raise ValueError("departments must be a list")
        # self._departments = [DepartmentFilter("default", FilterType(None, None))]
        self._departments = []
        for department in value:
            if not isinstance(department, dict):
                raise ValueError("departments must be a list of dictionaries")
            if "name" not in department:
                raise ValueError("departments must be a list of dictionaries with a name key")
            self._departments.append(DepartmentFilter(department["name"], FilterType.get_include_exclude(department, "valid_appointments")))
