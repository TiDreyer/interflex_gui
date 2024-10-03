import os
from pathlib import Path

import pytest

from work_clock.settings import UserSettings, DriverType


@pytest.fixture
def settings(scope='session'):
    tmp_settings_file = Path("tmp_test_settings.json")
    class MockSettings(UserSettings):
        @staticmethod
        def setting_file_path() -> Path:
            return tmp_settings_file
    yield MockSettings()
    os.remove(tmp_settings_file)


def test_base_url(settings):
    default_value = ""
    test_value = "my.url.com"
    assert settings.base_url == default_value
    settings.base_url = test_value
    assert settings.base_url == test_value


def test_employee_id(settings):
    default_value = None
    test_value = 123456
    assert settings.employee_id == default_value
    settings.employee_id = test_value
    assert settings.employee_id == test_value


def test_employee_pin(settings):
    default_value = None
    test_value = 123456
    assert settings.employee_pin == default_value
    settings.employee_pin = test_value
    assert settings.employee_pin == test_value


def test_today_in_saldo(settings):
    default_value = False
    test_value = True
    assert settings.today_in_saldo == default_value
    settings.today_in_saldo = test_value
    assert settings.today_in_saldo == test_value


def test_hours_per_day(settings):
    default_value = 7.0
    test_value = 3.14
    assert settings.hours_per_day == default_value
    settings.hours_per_day = test_value
    assert settings.hours_per_day == test_value


def test_debug_mode(settings):
    default_value = False
    test_value = True
    assert settings.debug_mode == default_value
    settings.debug_mode = test_value
    assert settings.debug_mode == test_value


def test_webdriver(settings):
    default_value = DriverType.edge
    test_value = DriverType.firefox
    assert settings.webdriver == default_value
    settings.webdriver = test_value
    assert settings.webdriver == test_value
