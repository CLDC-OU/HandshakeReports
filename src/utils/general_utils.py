from datetime import date
import logging
import re


def get_date_ranges(str_date_ranges: str) -> list[tuple[date, date]]:
    """
    Parses a string of date ranges and returns a list of tuples representing the start and end dates.

    Args:
        str_date_ranges (str): The string of comma separated date ranges (deliminated by a hyphen) including string month (e.g., "January") and 4-digit year to be parsed. Takes the format `MONTH_STRING YYYY - MONTH_STRING YYYY`.

    Returns:
        list[tuple[date, date]]: A list of tuples representing the start and end dates with the end date being exclusive.

    Raises:
        ValueError: If the date range is invalid.

    Example:
        ```python
        str_date_ranges = "September 2023 - December 2024, September 2024 - January 2025"
        get_date_ranges(str_date_ranges)
        # Output: [(date(2023, 9, 1), date(2024, 1, 1)), (date(2024, 9, 1), date(2025, 2, 1))]
        ```
    """

    if str_date_ranges is None:
        start_d = date.today()
        end_d = date.today()
        return [(start_d, end_d)]

    # Split the date ranges into individual ranges (e.g. "September 2023 - December 2023, September 2024 - January 2025" -> ["September 2023 - December 2023", "September 2024 - January 2025"])
    ranges = str_date_ranges.split(',')
    date_ranges = []

    for i in range(len(ranges)):
        if not ranges[i] or len(ranges[i]) == 0:
            logging.error(f"Invalid date range at index {i} in {str_date_ranges}")
            continue

        # Split the date range into start and end dates (e.g. "September 2023 - December 2023" -> "September 2023", "December 2023")
        range_i = ranges[i].split('-')
        if len(range_i) == 1:
            end_date_str = range_i[0].strip()
        elif len(range_i) != 2:
            raise ValueError(f"Invalid date range at index {i} in {str_date_ranges}")
        else:
            end_date_str = range_i[1].strip()
        start_date_str = range_i[0].strip()

        # Separate the month and year from the string (e.g. "September 2023", "December 2023" -> ("September", "2023"), ("December", "2023"))
        start_split_month_year = start_date_str.split(" ")
        end_split_month_year = end_date_str.split(" ")

        if len(start_split_month_year) != 2 or len(end_split_month_year) != 2:
            raise ValueError(f"Invalid date range at index {i} in {str_date_ranges}")

        start_month = start_split_month_year[0].strip()
        start_year = start_split_month_year[1].strip()
        end_month = end_split_month_year[0].strip()
        end_year = end_split_month_year[1].strip()

        # Validate and convert the month and year to a date object (e.g. ("September", "2023"), ("December", "2023") -> (date(2023, 9, 1), date(2024, 1, 1)) )
        if start_month not in months or end_month not in months:
            raise ValueError(f"Invalid date range at index {i} in {str_date_ranges}")

        if not start_year.isdigit() or not end_year.isdigit():
            raise ValueError(f"Invalid date range at index {i} in {str_date_ranges}")

        start_date = date(int(start_year), months.index(start_month) + 1, 1)

        end_month = months.index(end_month) + 1
        if end_month == 12:
            end_year = int(end_year) + 1
            end_month = 1
        else:
            end_year = int(end_year)
            end_month += 1
        end_date = date(end_year, end_month, 1)
        date_ranges.append((start_date, end_date))

    return date_ranges


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
