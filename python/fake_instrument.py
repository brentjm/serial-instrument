#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import random
from serial_instrument import SerialInstrument
from pdb import set_trace
logger = logging.getLogger(__name__)

"""
Contains the Bronkhorst class that is a subclass of the
generic instrument object.
"""


class FakeInstrument(SerialInstrument):
    """Class to communicate with Bronkhorst mini-Cori
    flow meter.

    Attributes:
    bronkhorst (propar.instrument): Bronkhorst interface.
        https://pypi.org/project/bronkhorst-propar/
        https://pypi.org/project/bronkhorst-propar/
    """
    def __init__(self, port="/dev/ttyUSB0"):
        super().__init__(port=port)

    def _connect_instrument(self, port):
        """Connect to the instrument serial port.
        https://pypi.org/project/bronkhorst-propar/

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = "fake_instrument"
        except:
            logger.info(
                "Could not connect to instrument on port {}".format(port)
            )
        else:
            logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the Bronkhorst flow rate present value.
        https://pypi.org/project/bronkhorst-propar/
        """
        data = {}
        for attribute in ["PV", "SP"]:
            data[attribute] = random.random()
        return data

    def _test_command(self):
        """Causes the leds on the side to flash.
        """
        print("executing test command")


def test():
    fake_instrument = FakeInstrument()
    request = {"user": "unique_user", "password": "123"}

    print("test login")
    request["command"] = {"command_name": "login"}
    print(fake_instrument.process_request(request))

    print("test get_data")
    request["command"] = {"command_name": "get_data"}
    print(fake_instrument.process_request(request))

    print("test sending command")
    request["command"] = {"command_name": "_test_command"}
    print(fake_instrument.process_request(request))

    print("test sending invalid command")
    request["command"] = {"command_name": "invalid command"}
    print(fake_instrument.process_request(request))

    print("testing with wrong credentials")
    print(fake_instrument.process_request({
        "user": "no one",
        "password": "wrong",
        "command": {"command_name": "get_data"}
    }))

    print("test logout")
    request["command"] = {"command_name": "logout"}
    print(fake_instrument.process_request(request))


if __name__ == "__main__":
    test()
