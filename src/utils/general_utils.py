# Returns an array of all months between start and end inclusive
def get_month_range(start_m, end_m=None) -> list[str]:
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
    if start_m is None or start_m not in months:
        return []
    if end_m is None:
        return [months[months.index(start_m)]]
    if end_m not in months:
        return []

    return months[months.index(start_m):months.index(end_m) + 1]
