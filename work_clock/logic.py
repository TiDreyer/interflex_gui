import logging
from datetime import datetime
from typing import Optional

from work_clock.interflex_requests import SeleniumTimeBooker
from work_clock.settings import SETTINGS
from work_clock.time_evaluation import DailyBookings, BookingTime


class ClockState:
    def __init__(self):
        self._vpn_connected: Optional[bool] = None
        self._saldo: Optional[BookingTime] = None
        self._clocked_in: Optional[bool] = None
        self._bookings: Optional[DailyBookings] = None
        self._last_check: Optional[datetime] = None

    def toggle_clock(self) -> None:
        booker = SeleniumTimeBooker(
            employee_id=SETTINGS.employee_id,
            employee_pin=SETTINGS.employee_pin,
            debug=SETTINGS.debug_mode,
        )
        with booker as active_booker:
            active_booker.full_state_toggle()

    def update_status(self) -> None:
        # first check, if Interflex is reachable at all
        try:
            self._vpn_connected = SeleniumTimeBooker.service_is_reachable()
        except Exception as error:
            logging.warning("Caught error: %s" % repr(error))
            self._vpn_connected = None
            return
        # if reachable, get all relevant information
        booker = SeleniumTimeBooker(
            employee_id=SETTINGS.employee_id,
            employee_pin=SETTINGS.employee_pin,
            debug=SETTINGS.debug_mode,
        )
        with booker as active_booker:
            self._saldo = active_booker.hour_saldo()
            self._clocked_in = active_booker.user_is_logged_in()
            self._bookings = DailyBookings(active_booker.today_bookings(),
                                           normal_hours_per_day=SETTINGS.hours_per_day)
        self._last_check = datetime.now()

    @property
    def last_check(self) -> str:
        if self._last_check is None:
            return "never"
        return self._last_check.strftime("%H:%M")

    @property
    def vpn_connected(self) -> Optional[bool]:
        return self._vpn_connected

    @property
    def clocked_in(self) -> Optional[bool]:
        return self._clocked_in

    @property
    def saldo(self) -> Optional[str]:
        if self._saldo is None:
            return None
        if SETTINGS.today_in_saldo is True:
            if self._bookings is None:
                return None
            return str(self._saldo + self._bookings.daily_saldo)
        return str(self._saldo)

    @property
    def time_today(self) -> Optional[str]:
        if self._bookings is None or len(self._bookings) == 0:
            return None
        return str(self._bookings.total)

    @property
    def done_today(self) -> Optional[str]:
        if self._bookings is None or len(self._bookings) == 0:
            return None
        return str(self._bookings.done_for_today)
