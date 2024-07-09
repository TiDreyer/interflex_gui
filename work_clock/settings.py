import json
from pathlib import Path
from platform import system
from typing import Optional

from work_clock import APP_NAME_CODE


class UserSettings:
    def __init__(self):
        self._base_url: Optional[str] = None
        self._employee_id: Optional[int] = None
        self._employee_pin: Optional[int] = None
        self._today_in_saldo: Optional[bool] = None
        self._hours_per_day: Optional[float] = None
        self._debug_mode: Optional[bool] = None

        self.load()

    @staticmethod
    def setting_file_path() -> Path:
        operating_system = system()
        if operating_system == 'Windows':
            settings_dir = Path.home().joinpath(f'AppData/local/{APP_NAME_CODE}')
        elif operating_system == 'Linux':
            settings_dir = Path.home().joinpath(f'.config/{APP_NAME_CODE}')
        else:
            raise RuntimeError("Unknown OS: %s" % operating_system)
        settings_dir.mkdir(parents=True, exist_ok=True)
        settings_file = settings_dir.joinpath('usersettings.json')
        return settings_file

    def save(self):
        settings = {
            'base_url': self._base_url,
            'employee': {
                'id': self._employee_id,
                'pin': self._employee_pin,
            },
            'today_in_saldo': self._today_in_saldo,
            'hours_per_day': self._hours_per_day,
            'debug_mode': self._debug_mode,
        }
        settings_json = json.dumps(settings)
        with open(self.setting_file_path(), 'w') as settings_file:
            settings_file.write(settings_json)

    def load(self):
        if not self.setting_file_path().is_file():
            self.save()
        with open(self.setting_file_path(), 'r') as settings_file:
            settings_json = json.loads(settings_file.read())
        self._base_url = settings_json.get('base_url', None)
        self._employee_id = settings_json.get('employee', {}).get('id', None)
        self._employee_pin = settings_json.get('employee', {}).get('pin', None)
        self._today_in_saldo = settings_json.get('today_in_saldo', None)
        self._hours_per_day = settings_json.get('hours_per_day', None)
        self._debug_mode = settings_json.get('debug_mode', None)

    @property
    def base_url(self) -> str:
        if self._base_url is None:
            return ""
        return self._base_url

    @base_url.setter
    def base_url(self, base_url: str) -> None:
        self._base_url = base_url
        self.save()

    @property
    def employee_id(self) -> Optional[int]:
        return self._employee_id

    @employee_id.setter
    def employee_id(self, employee_id: int) -> None:
        self._employee_id = employee_id
        self.save()

    @property
    def employee_pin(self) -> Optional[int]:
        return self._employee_pin

    @employee_pin.setter
    def employee_pin(self, employee_pin: int) -> None:
        self._employee_pin = employee_pin
        self.save()

    @property
    def today_in_saldo(self) -> Optional[bool]:
        return self._today_in_saldo

    @today_in_saldo.setter
    def today_in_saldo(self, today_in_saldo: bool) -> None:
        self._today_in_saldo = today_in_saldo
        self.save()

    @property
    def hours_per_day(self) -> Optional[float]:
        return self._hours_per_day

    @hours_per_day.setter
    def hours_per_day(self, hours_per_day: float) -> None:
        self._hours_per_day = hours_per_day
        self.save()

    @property
    def debug_mode(self) -> Optional[bool]:
        return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, debug_mode: bool) -> None:
        self._debug_mode = debug_mode
        self.save()


SETTINGS = UserSettings()
