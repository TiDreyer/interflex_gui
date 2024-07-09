import argparse
import logging
import sys

from work_clock.user_interface import TimeBookingUi
from work_clock.settings import SETTINGS


if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-d', '--debug', action='store_true')
    ARGS = PARSER.parse_args(sys.argv[1:])

    logging.basicConfig(
        level=logging.DEBUG if ARGS.debug else logging.INFO,
        format="%(asctime)s  %(levelname)-8s %(funcName)35s():  %(message)s",
    )
    SETTINGS.debug_mode = ARGS.debug

    UI = TimeBookingUi()
    UI.run()
