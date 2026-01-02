from datetime import datetime, timedelta

__all__ = ["DateTimeUtil"]


class DateTimeUtil(datetime):
    """
    A utility class extending Python's datetime to add custom date calculations.

    This class adds methods and properties for start and end dates of a month,
    month differences, and day differences, while retaining all functionality
    of the original datetime class.
    """

    @property
    def start_date(self) -> "DateTimeUtil":
        """
        Returns the first day of the month for the given date.

        Returns:
            DateTimeUtil: A DateTimeUtil instance representing the first day of the month.
        """
        return DateTimeUtil(self.year, self.month, 1)

    @property
    def end_date(self) -> "DateTimeUtil":
        """
        Returns the last day of the month for the given date.

        Returns:
            DateTimeUtil: A DateTimeUtil instance representing the last day of the month.
        """
        if self.month == 12:
            end_date = DateTimeUtil(self.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = DateTimeUtil(self.year, self.month + 1, 1) - timedelta(days=1)
        return DateTimeUtil(end_date.year, end_date.month, end_date.day)

    def month_difference(self, from_date: datetime) -> int:
        """
        Calculates the difference in months between this date and a given date.

        Args:
            from_date (datetime): The date to compare against.

        Returns:
            int: The difference in months.
        """
        year_diff: int = from_date.year - self.year
        month_diff: int = from_date.month - self.month
        return year_diff * 12 + month_diff

    def day_difference(self, from_date: datetime) -> int:
        """
        Calculates the difference in days between this date and a given date.

        Args:
            from_date (datetime): The date to compare against.

        Returns:
            int: The difference in days. A positive value indicates that the given date
            is after this date, and a negative value indicates it is before.
        """
        delta = from_date - self
        return delta.days

    def to_pydatetime(self) -> datetime:
        """
        Returns the instance as a standard datetime object.

        Returns:
            datetime: The instance represented as a standard datetime object.
        """
        return datetime(
            self.year,
            self.month,
            self.day,
            self.hour,
            self.minute,
            self.second,
            self.microsecond,
        )


if __name__ == "__main__":
    # Example usage
    date_util = DateTimeUtil.today()
    print(date_util)
    print(date_util.start_date)
    print(date_util.end_date)
    print(date_util.month_difference(DateTimeUtil(2000, 1, 1)))
    print(date_util.day_difference(DateTimeUtil(2000, 1, 1)))
