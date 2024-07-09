import sys
from pathlib import Path
from subprocess import check_output, CalledProcessError
from typing import Optional


VERSION_FILE_PATH = Path('VERSION')


def git_tag_version() -> Optional[str]:
    try:
        git_output = check_output(['git', 'describe', '--tags', '--dirty'])
    except (CalledProcessError, FileNotFoundError):
        return None
    return git_output.decode().strip()


def file_version() -> Optional[str]:
    with open(VERSION_FILE_PATH, 'r') as version_file:
        version = version_file.readline().strip()
    return version


if getattr(sys, "frozen", False):
    APP_VERSION = file_version() or "Unknown Version"
else:
    APP_VERSION = git_tag_version() or "Unknown Version"
APP_NAME = 'Work Clock'
APP_NAME_CODE = 'interflex_work_clock'
APP_DESCRIPTION = 'Native GUI interface to clock in/out on the Interflex web interface when in home office.'
