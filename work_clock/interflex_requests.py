import asyncio
import datetime
import logging
from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Optional

import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait, expected_conditions

from work_clock.settings import SETTINGS
from work_clock.time_evaluation import TimeBookingList, BookingTime


SELENIUM_TIMEOUT = 5  # in seconds

INDEX_URL = SETTINGS.base_url + 'index.jsp'
LOGIN_URL = SETTINGS.base_url + 'iflx/pin.jsp'
MAIN_URL = SETTINGS.base_url + 'iflx/profile_187001/main.jsp'
HOME_URL = SETTINGS.base_url + 'iflx/profile_187001/home.jsp'
MENUE_URL = SETTINGS.base_url + 'iflx/profile_187001/menue.jsp'
BOOKING_URL = SETTINGS.base_url + 'iflx/profile_187001/bookingsmain.jsp'


def only_in_context(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(self, *args, **kwargs):
        if not self._context_active:
            raise RuntimeError("Please only use this method in an active context")
        return function(self, *args, **kwargs)

    return wrapper


class SeleniumTimeBooker:
    def __init__(self, employee_id: int, employee_pin: int, debug=False):
        self.employee_id = employee_id
        self.employee_pin = employee_pin
        self.debug_mode = debug
        self.driver = None
        self._context_active: bool = False

    def __enter__(self):
        if self._context_active:
            raise RuntimeError("Only open one context at a time!")
        self._context_active = True
        asyncio.run(self._init_driver())
        asyncio.run(self._login())
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        asyncio.run(self._logout())
        self._close()
        self._context_active = False

    @staticmethod
    def service_is_reachable() -> bool:
        try:
            code = requests.get(INDEX_URL).status_code
            return code == HTTPStatus.OK
        except requests.exceptions.ConnectionError:
            return False

    @only_in_context
    def full_state_toggle(self):
        asyncio.run(self._click_booking_button())

    @only_in_context
    def hour_saldo(self) -> Optional[BookingTime]:
        return asyncio.run(self._get_hour_saldo())

    @only_in_context
    def user_is_logged_in(self) -> bool:
        is_logged_in = asyncio.run(self._is_logged_in())
        return is_logged_in

    @only_in_context
    def today_bookings(self) -> TimeBookingList:
        table = asyncio.run(self._journal_table())
        bookings = self._table_to_booking_list(table=table)
        return bookings

    async def _init_driver(self):
        options = webdriver.EdgeOptions()
        if not self.debug_mode:
            options.add_argument('--headless=new')
        self.driver = webdriver.Edge(options=options)

    async def _login(self):
        logging.info("Logging in to the web interface")
        self.driver.get(LOGIN_URL)
        employee_id_field = await self.__get_element_once_present(By.ID, 'InpEmpId')
        employee_id_field.send_keys(str(self.employee_id))
        employee_id_field = await self.__get_element_once_present(By.ID, 'InpEmpPwd')
        employee_id_field.send_keys(str(self.employee_pin))
        login_button = await self.__get_element_once_present(By.CLASS_NAME, 'iflxButtonFactoryTextContainerOuter')
        login_button.click()

    async def __get_element_once_present(self, by: By, value: str, multiple: bool = False) -> Any:
        logging.info(f"Waiting for {repr(by)} = '{value}' to be present")
        locator = (by, value)
        await asyncio.sleep(0.01)  # minimum wait time
        wait.WebDriverWait(self.driver, SELENIUM_TIMEOUT).until(
            expected_conditions.presence_of_element_located(locator))
        if multiple:
            return self.driver.find_elements(by, value)
        return self.driver.find_element(by, value)

    async def _is_logged_in(self) -> bool:
        logging.info("Check, if user is logged in")
        self.driver.get(BOOKING_URL)
        self.driver.get(MAIN_URL)
        self.driver.get(BOOKING_URL)
        booking_button = await self.__get_element_once_present(By.CLASS_NAME, 'iflxButtonFinder')
        button_text = booking_button.text.strip()
        if button_text == 'Kommen':
            return False
        if button_text == 'Gehen':
            return True
        raise RuntimeError(f"Unknown text on button: '{button_text}'")

    async def _click_booking_button(self):
        logging.info("Toggle the booking button")
        self.driver.get(BOOKING_URL)
        self.driver.get(MAIN_URL)
        self.driver.get(BOOKING_URL)
        booking_button = await self.__get_element_once_present(By.CLASS_NAME, 'iflxButtonFactoryTextContainerNormal')
        booking_button.click()

    async def _journal_table(self) -> list[list[str]]:
        self.driver.get(BOOKING_URL)
        self.driver.get(MAIN_URL)
        self.driver.get(BOOKING_URL)
        table_headers = await self.__get_element_once_present(
            By.CSS_SELECTOR, 'th.iflxQujouHdr', multiple=True)
        table_cells = await self.__get_element_once_present(
            By.CSS_SELECTOR,
            ('td.iflxQujouTab1, td.iflxQujouTabTime1, td.iflxQujouTabAccount1, '
             'td.iflxQujouTab2, td.iflxQujouTabTime2, td.iflxQujouTabAccount2'),
            multiple=True,
        )
        cells_per_row = len(table_headers)
        colspans = [cell.get_attribute('colspan') for cell in table_cells]
        n_cells = sum(int(colspan) if colspan is not None else 1 for colspan in colspans)
        assert n_cells % cells_per_row == 0
        table = [[th.text for th in table_headers]]
        table_row = []
        for cell in table_cells:
            colspan = 1 if cell.get_attribute('colspan') is None else cell.get_attribute('colspan')
            for _ in range(int(colspan)):
                table_row.append(cell.text)
            if len(table_row) >= cells_per_row:
                table.append(table_row)
                table_row = []
        return table

    async def _get_hour_saldo(self) -> Optional[BookingTime]:
        self.driver.get(HOME_URL)
        table_headers = await self.__get_element_once_present(
            By.CSS_SELECTOR, 'th.iflxHomeInfoAcc', multiple=True)
        table_cells = await self.__get_element_once_present(
            By.CSS_SELECTOR, 'td.iflxHomeInfoAcc', multiple=True)
        for header, data in zip(table_headers, table_cells):
            if header.text.strip() == 'Gleitzeit':
                time_as_str = data.text.strip().replace(',', ':')
                return BookingTime.from_string(time_as_str)
        return None

    @staticmethod
    def _table_to_booking_list(table: list[list[str]]) -> TimeBookingList:
        time_booking_list = []
        current_day_str = datetime.datetime.today().strftime("%d.%m.")
        on_current_day = False
        for row in table:
            if current_day_str in row[0]:
                on_current_day = True
            if not on_current_day:
                continue
            in_time_str = row[2]
            out_time_str = row[3]
            if in_time_str.strip() == '':
                continue
            if out_time_str.strip() == '':
                out_time_str = datetime.datetime.now().strftime("%H:%M")
            booking = (BookingTime.from_string(in_time_str), BookingTime.from_string(out_time_str))
            time_booking_list.append(booking)
        return time_booking_list

    async def _logout(self):
        logging.info("Log out from the web interface")
        self.driver.get(MENUE_URL)
        logout_button = await self.__get_element_once_present(By.CLASS_NAME, 'iflxMenu3ExitButton')
        logout_button.click()

    def _close(self):
        self.driver.close()
