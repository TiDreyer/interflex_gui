import logging
import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk, simpledialog, messagebox
from typing import Optional

from selenium.common import WebDriverException

from work_clock import APP_NAME, APP_VERSION
from work_clock.logic import ClockState
from work_clock.settings import SETTINGS, DriverType


@dataclass
class Symbol:
    CHAR_BULLET = chr(0x2022)  # Bullet
    CHAR_ELLIPSES = chr(0x2026)  # Ellipsis
    CHAR_UNKNOWN = chr(0x2753)  # White Question Mark
    CHAR_YES = chr(0x2714)  # Check Mark
    CHAR_NO = chr(0x274C)  # Cross Mark
    CHAR_RELOAD = chr(0x27F3)  # Clockwise Gapped Circle Arrow
    CHAR_SETTINGS = chr(0x1F6E0)  # Hammer and Wrench


@dataclass
class UiLabels:
    vpn_status: str = Symbol.CHAR_UNKNOWN
    clocked_in = Symbol.CHAR_UNKNOWN
    time_today = Symbol.CHAR_UNKNOWN
    clock_button = "Toggle clock status"
    last_check = "Updated: never"
    saldo = Symbol.CHAR_UNKNOWN
    done_today = f"Done for today: {Symbol.CHAR_UNKNOWN}"


class TimeBookingUi:
    def __init__(self):
        self._clock = ClockState()
        self._label = UiLabels()
        self._update_labels()
        self._create_window()

    def _create_window(self):
        self.root = tk.Tk()
        self.root.geometry('280x120')
        self.root.resizable(False, False)
        self.root.winfo_toplevel().title(APP_NAME + " " + APP_VERSION)

        self.content = ttk.Frame(self.root, padding=10)
        self.content.grid(column=0, row=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self._fill_window()

        self.root.columnconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=1)
        self.content.columnconfigure(2, weight=0)

    def _fill_window(self):
        """
        Layout:
               0      1      2      3
            +-------------+-------------+
        0   |      |      |      |      |
            +------+------+      |      |
        1   |      |      |      |      |
            +------+------+------+------+
        2   |      |      |      |      |
            +------+------+------+------+
        3   |      |      |      |      |
            +------+------+------+------+
        4   |                           |
            +---------------------------+
        """
        parent = self.content
        sticky = tk.N + tk.S + tk.E + tk.W

        # rows 0 + 1
        ttk.Label(parent, text="VPN Status:").grid(row=0, column=0, sticky=sticky)
        ttk.Label(parent, text="Clocked in:").grid(row=1, column=0, sticky=sticky)
        ttk.Label(parent, text=self._label.vpn_status).grid(row=0, column=1, sticky=sticky)
        ttk.Label(parent, text=self._label.clocked_in).grid(row=1, column=1, sticky=sticky)
        s = ttk.Style()
        s.configure('my.TButton', font=("Calibri", 20), width=4)
        ttk.Button(parent, text=Symbol.CHAR_SETTINGS, style='my.TButton', command=self._button_settings
                   ).grid(row=0, rowspan=2, column=2, sticky=sticky)
        ttk.Button(parent, text=Symbol.CHAR_RELOAD, style='my.TButton', command=self._button_update_all
                   ).grid(row=0, rowspan=2, column=3, sticky=sticky)

        # rows 2
        ttk.Label(parent, text="Time today:").grid(row=2, column=0, sticky=sticky)
        ttk.Label(parent, text=self._label.time_today).grid(row=2, column=1, sticky=sticky)
        ttk.Label(parent, text="Saldo:").grid(row=2, column=2, sticky=sticky)
        ttk.Label(parent, text=self._label.saldo).grid(row=2, column=3, sticky=sticky)

        # rows 3
        ttk.Label(parent, text="Updated:").grid(row=3, column=0, sticky=sticky)
        ttk.Label(parent, text=self._label.last_check).grid(row=3, column=1, sticky=sticky)
        ttk.Label(parent, text="Done for today:").grid(row=3, column=2, sticky=sticky)
        ttk.Label(parent, text=self._label.done_today).grid(row=3, column=3, sticky=sticky)

        # row 4
        ttk.Button(parent, text=self._label.clock_button, command=self._button_toggle_clock
                   ).grid(row=4, column=0, columnspan=4, sticky=sticky)

        self.root.update()

    def _button_update_all(self):
        self._set_wip_labels()
        self._fill_window()
        try:
            self._clock.update_status()
        except WebDriverException as error:
            logging.error(repr(error))
        self._update_labels()
        self._fill_window()

    def _button_settings(self):
        dialog = SettingsUi()

        def update():
            dialog.root.destroy()
            self._update_labels()
            self._fill_window()

        dialog.root.protocol("WM_DELETE_WINDOW", update)
        dialog.run()

    def _button_toggle_clock(self):
        confirm = messagebox.askokcancel(
            title="Clock toggle", message=f"Do you really want to '{self._label.clock_button}'?",
        )
        if not confirm:
            return
        self._set_wip_labels()
        self._fill_window()
        try:
            self._clock.toggle_clock()
            self._clock.update_status()
        except WebDriverException as error:
            logging.error(repr(error))
        self._update_labels()
        self._fill_window()

    def _update_labels(self) -> None:
        def none_to_unknown(x: Optional[str]) -> str:
            return x if x is not None else Symbol.CHAR_UNKNOWN

        def optional_bool(x: Optional[bool]) -> str:
            match x:
                case None: return Symbol.CHAR_UNKNOWN
                case True: return Symbol.CHAR_YES
                case False: return Symbol.CHAR_NO

        self._label.vpn_status = optional_bool(self._clock.vpn_connected)
        self._label.clocked_in = optional_bool(self._clock.clocked_in)
        self._label.time_today = none_to_unknown(self._clock.time_today)
        self._label.done_today = none_to_unknown(self._clock.done_today)
        self._label.saldo = none_to_unknown(self._clock.saldo)
        self._label.last_check = self._clock.last_check

        match self._clock.clocked_in:
            case None: self._label.clock_button = "Toggle clock status"
            case True: self._label.clock_button = "Clock out"
            case False: self._label.clock_button = "Clock in"

    def _set_wip_labels(self) -> None:
        self._label.clocked_in = Symbol.CHAR_ELLIPSES
        self._label.time_today = Symbol.CHAR_ELLIPSES
        self._label.last_check = Symbol.CHAR_ELLIPSES
        self._label.clock_button = Symbol.CHAR_ELLIPSES

    def run(self):
        self.root.mainloop()


@dataclass
class UiLabelsSettings:
    base_url: str = ""
    employee_id: str = ""
    employee_pin: str = ""
    hours_per_day: str = ""
    today_in_saldo: str = ""
    debug_mode: str = ""
    webdriver: Optional[tk.StringVar] = None


class SettingsUi:
    def __init__(self):
        SETTINGS.load()
        self._label = UiLabelsSettings()
        self._update_labels()
        self._create_window()

    def _create_window(self):
        self.root = tk.Tk()
        self.root.geometry('300x180')
        self.root.resizable(False, False)
        self.root.winfo_toplevel().title(APP_NAME + " Settings")

        self.content = ttk.Frame(self.root, padding=10)
        self.content.grid(column=0, row=0, sticky=tk.N + tk.S + tk.E + tk.W)

        self._label.webdriver = tk.StringVar(master=self.root, value=SETTINGS.webdriver.value)

        self._fill_window()

        self.root.columnconfigure(0, weight=1)
        self.content.columnconfigure(0, weight=3)
        self.content.columnconfigure(1, weight=1)
        self.content.columnconfigure(2, weight=0)

    def _update_labels(self) -> None:
        def bool_label(value) -> str:
            match value:
                case None: return Symbol.CHAR_UNKNOWN
                case True: return Symbol.CHAR_YES
                case False: return Symbol.CHAR_NO

        self._label.base_url = SETTINGS.base_url or 'https://inteflex.example.com/WebClient/'

        self._label.employee_id = str(SETTINGS.employee_id)
        # censor pin by replacing each character with a bullet symbol
        self._label.employee_pin = Symbol.CHAR_BULLET * len(str(SETTINGS.employee_pin))

        self._label.hours_per_day = str(SETTINGS.hours_per_day)

        self._label.today_in_saldo = bool_label(SETTINGS.today_in_saldo)
        self._label.debug_mode = bool_label(SETTINGS.debug_mode)
        if not self._label.webdriver is None:
            self._label.webdriver.set(SETTINGS.webdriver.value)

    def _fill_window(self):
        parent = self.content
        sticky = tk.N + tk.S + tk.E + tk.W

        row = 0
        ttk.Label(parent, text="Base URL:").grid(row=row, column=0, columnspan=2, sticky=sticky)
        row += 1
        ttk.Button(parent, text=self._label.base_url, command=self._button_set_base_url
                   ).grid(row=row, column=0, columnspan=2, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Employee ID:").grid(row=row, column=0, sticky=sticky)
        ttk.Button(parent, text=self._label.employee_id, command=self._button_set_employee_id
                   ).grid(row=row, column=1, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Employee PIN:").grid(row=row, column=0, sticky=sticky)
        ttk.Button(parent, text=self._label.employee_pin, command=self._button_set_employee_pin
                   ).grid(row=row, column=1, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Hours per day:").grid(row=row, column=0, sticky=sticky)
        ttk.Button(parent, text=self._label.hours_per_day, command=self._button_set_hours_per_day
                   ).grid(row=row, column=1, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Include today in saldo?").grid(row=row, column=0, sticky=sticky)
        ttk.Button(parent, text=self._label.today_in_saldo, command=self._button_today_in_saldo
                   ).grid(row=row, column=1, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Set Debug Mode").grid(row=row, column=0, sticky=sticky)
        ttk.Button(parent, text=self._label.debug_mode, command=self._button_set_debug_mode
                   ).grid(row=row, column=1, sticky=sticky)

        row += 1
        ttk.Label(parent, text="Web Driver:").grid(row=row, column=0, sticky=sticky)
        driver_options = ttk.Combobox(parent, textvariable=self._label.webdriver)
        driver_options.bind(sequence='<<ComboboxSelected>>', func=self._combo_set_driver)
        driver_options.grid(row=row, column=1, sticky=sticky)
        driver_options['values'] = [driver.value for driver in DriverType]

        self.root.update()

    def _button_set_base_url(self):
        result = simpledialog.askstring("User input", "Under which URL do you open the interface?",
                                         initialvalue=SETTINGS.base_url)
        if result is not None:
            SETTINGS.base_url = result
        self._update_labels()
        self._fill_window()

    def _button_set_employee_id(self):
        result = simpledialog.askinteger("User input", "What is your employee ID?",
                                         initialvalue=SETTINGS.employee_id)
        if result is not None:
            SETTINGS.employee_id = result
        self._update_labels()
        self._fill_window()

    def _button_set_employee_pin(self):
        result = simpledialog.askinteger("User input", "What is your interflex PIN?",
                                         initialvalue=SETTINGS.employee_pin)
        if result is not None:
            SETTINGS.employee_pin = result
        self._update_labels()
        self._fill_window()

    def _button_set_hours_per_day(self):
        result = simpledialog.askfloat("User input", "How many hours do you need to work per day?",
                                       initialvalue=SETTINGS.hours_per_day)
        if result is not None:
            SETTINGS.hours_per_day = result
        self._update_labels()
        self._fill_window()

    def _button_today_in_saldo(self):
        match SETTINGS.today_in_saldo:
            case None: SETTINGS.today_in_saldo = True
            case True: SETTINGS.today_in_saldo = False
            case False: SETTINGS.today_in_saldo = True
        self._update_labels()
        self._fill_window()

    def _button_set_debug_mode(self):
        match SETTINGS.debug_mode:
            case None: SETTINGS.debug_mode = True
            case True: SETTINGS.debug_mode = False
            case False: SETTINGS.debug_mode = True
        self._update_labels()
        self._fill_window()

    def _combo_set_driver(self, event):
        SETTINGS.webdriver = DriverType(self._label.webdriver.get())
        self._update_labels()
        self._fill_window()

    def run(self):
        self.root.mainloop()
