#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Controls the IKA  Eurostar Power overhead stirrer
"""
import os
import logging
import argparse
import random
from time import sleep
from serial import Serial
from instrument import SerialInstrument

__author__ = "Brent Maranzano"
__license__ = "MIT"

logger = logging.getLogger(__name__)


class Ika(SerialInstrument):
    """Class to communicate with the IKA Eurostart Power overhead
       stirrer.
       This class over-rides the following base clase methods:
           __init__
           _connect_instrument
           _update_data
           _set_about
       Only the .set_SP_speed should be called from a user command, as
       the retrieving the current instrument values will automatically
       be performed by the Instrument class methods.
    """

    def __init__(self, instrument_port, socket_ip, socket_port):
        super().__init__(instrument_port, socket_ip, socket_port)
        self._instrument.write("START_4 \r \n".encode('ascii'))

    def _connect_instrument(self, port):
        """Connect to the IKA using RS232

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = Serial(port=port, baudrate=9600, bytesize=7, parity="E",
                         stopbits=1, rtscts=0, timeout=1)
        except:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
        else:
            self._logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _set_about(self):
        """Setting attributes about the host microcomputer
        and connected instrument.
       """
        self._about = {
            "host": os.getenv("HOST"),
            "instrument": "IKA",
            "descriptions": "IKA Eurostar Power overhead stirrer."
        }
        self._logger.debug("about: {}".format(self._about))

    def _update_data(self):
        """Update the IKA speed set point and speed present value.

        Returns dictionary of data
        """
        data = {}
        data["user"] = self._user
        data["user_tag"] = self._user_tag
        data["SP_speed"] = self._get_SP_speed()
        data["PV_speed"] = self._get_PV_speed()
        return data

    def _get_SP_speed(self):
        """Get the speed set point.

        Return (float): current speed SP
        """
        buffer = self._instrument.inWaiting()
        junk = self._instrument.read(buffer)
        self._instrument.write("IN_SP_4 \r \n".encode('ascii'))
        sleep(0.3)
        speed = float(self._instrument.readline().decode('ascii').split(" ")[0])
        return speed

    def _get_PV_speed(self):
        """Get the speed present value.

        Return (float): current speed present value
        """
        buffer = self._instrument.inWaiting()
        junk = self._instrument.read(buffer)
        self._instrument.write("IN_PV_4 \r \n".encode('ascii'))
        sleep(0.3)
        speed = float(self._instrument.readline().decode('ascii').split(" ")[0])
        return speed

    def set_SP_speed(self, value=0):
        """Set the speed set point to value.

        value (float): value of set point.

        Return (dict): Status of command.
        """
        command = "OUT_SP_4 {:.2f} \r \n".format(value)
        try:
            self._instrument.write(command.encode('ascii'))
            response = {"socket response": "ok",
                        "description": "sent command: {}".format(command)}
        except:
            response = {"socket response": "error",
                        "description": "sent command: {}".format(command)}
        return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IKA Eursostart socket server")
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
    args = parser.parse_args()
    instrument = Ika(args.instrument_port, args.socket_ip, args.socket_port)
    instrument.run()
