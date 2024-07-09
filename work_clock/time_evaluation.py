import datetime
import functools
from typing import Optional, Self

@functools.total_ordering
class BookingTime:
    def __init__(self, hours: int, minutes: int):
        self._total_minutes = hours * 60 + minutes

    @property
    def negative(self) -> bool:
        return self._total_minutes < 0

    @property
    def hours(self) -> int:
        hours = abs(self._total_minutes) // 60
        if self.negative:
            hours = -hours
        return hours

    @property
    def minutes(self) -> int:
        minutes = abs(self._total_minutes) % 60
        if self.negative:
            minutes = -minutes
        return minutes

    @classmethod
    def from_string(cls, time_str: str) -> Self:
        negative = time_str.startswith('-')
        hours = abs(int(time_str.split(':')[0].strip()))
        minutes = abs(int(time_str.split(':')[1].strip()))
        if negative:
            hours = -hours
            minutes = -minutes
        return cls(hours=hours, minutes=minutes)

    @classmethod
    def from_hour_float(cls, hour_float: float) -> Self:
        hours = int(hour_float)
        minutes = int(round((hour_float % 1) * 60, 0))
        return cls(hours=hours, minutes=minutes)

    @classmethod
    def create_now(cls) -> Self:
        now = datetime.datetime.now()
        return cls(hours=now.hour, minutes=now.minute)

    def __sub__(self, other: Self) -> Self:
        diff_time = BookingTime(0, 0)
        diff_time._total_minutes = self._total_minutes - other._total_minutes
        return diff_time

    def __add__(self, other: Self) -> Self:
        sum_time = BookingTime(0, 0)
        sum_time._total_minutes = self._total_minutes + other._total_minutes
        return sum_time

    def __str__(self) -> str:
        sign = "-" if self.negative else ""
        return f"{sign}{abs(self.hours)}:{abs(self.minutes):02}"

    def __repr__(self) -> str:
        return f"BookingTime({self})"

    def __eq__(self, other: Self) -> bool:
        return self._total_minutes == other._total_minutes

    def __lt__(self, other: Self) -> bool:
        return self._total_minutes < other._total_minutes


TimeBookingList = list[tuple[BookingTime, BookingTime]]


DEFAULT_BREAKS: TimeBookingList = [
    (BookingTime(9, 15), BookingTime(9, 30)),
    (BookingTime(12, 30), BookingTime(13, 0)),
]


class DailyBookings:
    def __init__(self,
                 bookings: Optional[TimeBookingList] = None,
                 break_times: Optional[TimeBookingList] = None,
                 normal_hours_per_day: Optional[float] = None,
                 ) -> None:
        if normal_hours_per_day is None:
            normal_hours_per_day = 7.0
        self._bookings: TimeBookingList = bookings if bookings is not None else []
        self._break_times: TimeBookingList = DEFAULT_BREAKS if break_times is None else break_times
        self._hours_per_day: BookingTime = BookingTime.from_hour_float(normal_hours_per_day)

    def add(self, in_time: BookingTime, out_time: BookingTime) -> None:
        self._bookings.append((in_time, out_time))

    def add_from_string(self, in_time: str, out_time: str) -> None:
        self._bookings.append((
            BookingTime.from_string(in_time),
            BookingTime.from_string(out_time),
        ))

    @property
    def total(self) -> BookingTime:
        total_time = BookingTime(0, 0)
        for check_in, check_out in self._bookings:
            total_time += self.__time_increment(check_in, check_out)
        return total_time

    @property
    def daily_saldo(self) -> BookingTime:
        daily_saldo = self.total - self._hours_per_day
        return daily_saldo

    @property
    def done_for_today(self) -> BookingTime:
        partial_booking = DailyBookings(bookings=[], break_times=self._break_times)
        for check_in, check_out in self._bookings:
            partial_booking.add(check_in, check_out)
            if partial_booking.total >= self._hours_per_day:
                break
        while partial_booking.total != self._hours_per_day:
            difference = self._hours_per_day - partial_booking.total
            last_in, last_out = partial_booking._bookings[-1]
            partial_booking._bookings[-1] = (last_in, last_out + difference)
        return partial_booking._bookings[-1][1]

    def __time_increment(self, check_in: BookingTime, check_out: BookingTime) -> BookingTime:
        increment = check_out - check_in
        # subtract falsely added break times
        for break_start, break_end in self._break_times:
            incl_start = check_in < break_start < check_out
            incl_end = check_in < break_end < check_out
            if incl_start and incl_end:
                increment -= break_end - break_start
            elif incl_start:
                increment -= check_out - break_start
            elif incl_end:
                increment -= break_end - check_in
        return increment

    def __len__(self) -> int:
        return len(self._bookings)
