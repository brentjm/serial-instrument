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

    def __init__(self, instrument_port, socket_ip, socket_port, host):
        super(FakeInstrument, self).__init__(instrument_port, socket_ip, socket_port, host)
        # Inhereted attribute
        self._device_information = {
            "instrument": "fake",
            "description": "Fake instrument for code testing.",
            "parameters": "SP_SP1, SP_SP2, PV_PV1, PV_PV2",
            "instrument commands": "set_SP_SP1(value=<float>), set_SP_SP2(value=<float>)"
        }
        # Inhereted attribute
        self._data = {
            "status": "off",
            "SP1": 0,
            "SP2": 0,
            "PV1": 0,
            "PV2": 0
        }
        # Attributes specific to this "fake" instrument to make
        # like a real instrument.
        self._instrument_parameters = {
            "status": "off",
            "SP1": 0,
            "SP2": 0,
            "PV1": 0,
            "PV2": 0
        }

    def _connect_instrument(self, port):
        """Create a fake serial connection.

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        connection = None
        try:
            connection = {
                "port": port,
                "bauderate": 9600,
                "bytesize": 8,
                "parity": "N",
                "stopbits": "1"
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
        data["user"] = self._user
        data["user_tag"] = self._user_tag
        data["status"] = self._instrument_parameters["status"]
        data["SP1"] = self._instrument_parameters["SP1"]
        data["SP2"] = self._instrument_parameters["SP2"]
        if self._instrument_parameters["status"] is "on":
            data["PV1"] = self._instrument_parameters["SP1"] + random.random()
            data["PV2"] = self._instrument_parameters["SP2"] + random.random()
        else:
            data["PV1"] = 0
            data["PV2"] = 0
        return data

    def set_SP_SP1(self, value=0):
        """Set the value of the set point 1 (SP1).

        value (float): value of set point 1.
        """
        self._instrument_parameters["SP1"] = value

    def set_SP_SP2(self, value=0):
        """Set the value of the set point 2 (SP2).

        value (float): value of set point 2.
        """
        self._instrument_parameters["SP2"] = value

    def start(self):
        """Start the fake instrument.
        """
        self._instrument_parameters["status"] = "on"

    def stop(self):
        """Stop the fake instrument.
        """
        self._instrument_parameters["status"] = "off"


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
        default=54132
    )
    parser.add_argument(
        "--instrument_port",
        help="port for instrument",
        type=str,
        default="/dev/ttyUSB0"
    )
    parser.add_argument(
        "--host",
        help="host name",
        type=str,
        default="ape-0"
    )
    args = parser.parse_args()
    fake_instrument = FakeInstrument(args.instrument_port, args.socket_ip, args.socket_port, args.host)
    fake_instrument.run()
