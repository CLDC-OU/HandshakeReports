import re


months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December"]


def get_month_range(start_m, end_m=None) -> list[str]:  # Returns an array of all months between start and end inclusive
    if start_m is None or start_m not in months:
        return []
    if end_m is None:
        return [months[months.index(start_m)]]
    if end_m not in months:
        return []

    if months.index(start_m) >= months.index(end_m):
        return months[months.index(start_m):] + months[:months.index(end_m) + 1]

    return months[months.index(start_m):months.index(end_m) + 1]


def int_month_to_str(month: int) -> str:
    if month < 1 or month > 12:
        raise ValueError("Invalid month")
    return months[month - 1]


def list_to_regex_includes(li: set[str] | list[str] | tuple[str]) -> re.Pattern[str]:
    return re.compile('|'.join(li))
