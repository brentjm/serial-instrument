#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import propar
from instruments.instrument import SerialInstrument
logger = logging.getLogger(__name__)
from pdb import set_trace

"""
Contains the Bronkhorst class that is a subclass of the
generic instrument object.
"""


class Bronkhorst(SerialInstrument):
    """Class to communicate with Bronkhorst mini-Cori
    flow meter.

    Attributes:
    bronkhorst (propar.instrument): Bronkhorst interface.
        https://pypi.org/project/bronkhorst-propar/
        https://pypi.org/project/bronkhorst-propar/
    """
    def __init__(self, instrument_port, socket_ip, socket_port):
        super().__init__(instrument_port, socket_ip, socket_port)

    def _connect_instrument(self, port):
        """Connect to the instrument serial port.
        https://pypi.org/project/bronkhorst-propar/

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = propar.instrument(port)
        except:
            logger.info(
                "Could not connect to instrument on port {}".format(port)
            )
        else:
            logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the value of the current measured flow rate.
        https://pypi.org/project/bronkhorst-propar/
        """
        for attribute in ["flow_rate"]:
            self._data[attribute] = self._instrument.measure

    def _wink(self):
        """Causes the leds on the side to flash.
        """
        self._instrument.wink()
        response = {"status": "ok", "description": "successful wink"}
        return response


def test():
    #bronkhorst = Bronkhorst("/dev/ttyUSB0", "172.19.5.2", 5007)
    bronkhorst = Bronkhorst("/dev/ttyUSB0", "127.0.0.1", 5007)
    request = {"user": "unique_user", "password": "123"}

    print("test login")
    request["command"] = {"command_name": "login"}
    print(bronkhorst.process_request(request))

    print("test get_data")
    request["command"] = {"command_name": "get_data"}
    print(bronkhorst.process_request(request))

    print("test sending command (wink)")
    request["command"] = {"command_name": "_wink"}
    print(bronkhorst.process_request(request))

    print("test sending invalid command")
    request["command"] = {"command_name": "invalid command"}
    print(bronkhorst.process_request(request))

    print("testing with wrong credentials")
    print(bronkhorst.process_request({
        "user": "no one",
        "password": "wrong",
        "command": {"command_name": "get_data"}
    }))

    print("test logout")
    request["command"] = {"command_name": "logout"}
    print(bronkhorst.process_request(request))


if __name__ == "__main__":
    #bronkhorst = Bronkhorst("/dev/ttyUSB0", "172.19.5.2", 5007)
    bronkhorst = Bronkhorst("/dev/ttyUSB0", "127.0.0.1", 5007)
    bronkhorst.run()
