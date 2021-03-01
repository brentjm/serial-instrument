#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simulates a fake serial instrument for testing the software stack.
"""
import logging
import argparse
import random
from instrument import SerialInstrument

__author__ = "Brent Maranzano"
__license__ = "MIT"

logger = logging.getLogger(__name__)


class FakeInstrument(SerialInstrument):
    """Class to communicate with a fake serial instrument.
       This class over-rides the following base clase methods:
           _connect_instrument
           _update_data
    """

    def __init__(self, instrument_port, socket_ip, socket_port):
        super().__init__(instrument_port, socket_ip, socket_port)
        self._status = "off"
        self._SP1 = 0
        self._SP2 = 0
        self._PV1 = 0
        self._PV2 = 0

    def _connect_instrument(self, port):
        """Create a fake serial connection.

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        connection = None
        try:
            connection = {
                "bauderate": 9600,
                "port": port
            }
        except:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
        else:
            self._logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the values (PV) of the fake instrument.

        Returns dictionary of data
        """
        data = {}
        data["status"] = self._status
        data["SP1"] = self._SP1
        data["SP2"] = self._SP2
        if self._status is "on":
            data["PV1"] = self._SP1 + random.random()
            data["PV2"] = self._SP2 + random.random()
        else:
            data["PV1"] = None
            data["PV2"] = None
        return data

    def set_SP1(self, value=0):
        """Set the value of the set point 1 (SP1).

        value (float): value of set point 1.

        Return (dict): Status of command.
        """
        self._SP1 = value
        response = {"status": "ok", "description": "successful set SP1"}
        return response

    def set_SP2(self, value=0):
        """Set the value of the set point 2 (SP2).

        value (float): value of set point 2.

        Return (dict): Status of command.
        """
        self._SP2 = value
        response = {"status": "ok", "description": "successful set SP2"}
        return response

    def start(self):
        """Start the fake instrument.
        """
        self._status = "on"
        response = {"status": "ok", "description": "successful start"}
        return response

    def stop(self):
        """Stop the fake instrument.
        """
        self._status = "off"
        response = {"status": "ok", "description": "successful stop"}
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fake instrument server")
    parser.add_argument(
        "--socket_ip",
        help="host address for the socket to bind",
        type=str,
        default="127.0.0.1"
    )
    parser.add_argument(
        "--socket_port",
        help="port number for the socket server",
        type=int,
        default=5007
    )
    parser.add_argument(
        "--instrument_port",
        help="port for instrument",
        type=str,
        default="/dev/ttyUSB0"
    )
    args = parser.parse_args()
    fake_instrument = FakeInstrument(args.instrument_port, args.socket_ip, args.socket_port)
    fake_instrument.run()
