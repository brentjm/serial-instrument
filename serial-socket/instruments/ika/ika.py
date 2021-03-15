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

    def __init__(self, instrument_port, socket_ip, socket_port, host):
        super(Ika, self).__init__(instrument_port, socket_ip, socket_port, host)
        # Set information about the attached device.
        self._device_information = {
            "instrument": "IKA",
            "description": "IKA Eurostar Power overhead stirrer.",
            "parameters": "SP_speed, PV_speed",
            "instrument commands": "set_SP_speed(value=<float>)"
        }
        self._data = {
            "SP_speed": 0.0,
            "PV_speed": 0.0
        }
        # start the IKA
        response = self._write_read_serial_command("IN_SP_4")

    def _connect_instrument(self, port):
        """Connect to the IKA using RS232

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = Serial(port=port, baudrate=9600, bytesize=7, parity="E",
                         stopbits=1, rtscts=0, timeout=0.5)
        except:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
            self._instrument_status = "error: could not connect to instrument"
        else:
            self._logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the IKA speed set point and speed present value.

        Returns dictionary of data
        """
        self._data["SP_speed"] = self._get_SP_speed()
        self._data["PV_speed"] = self._get_PV_speed()

    def _write_read_serial_command(self, command):
        """Write the command to the serial connection and
        then read response (if any).

        Arguments:
        command (str): command

        Returns (str) serial instrument response
        """
        command = command + " \r \n"
        command = command.encode('ascii')
        try:
            buffer = self._instrument.inWaiting()
            junk = self._instrument.read(buffer)
            self._instrument.write(command)
            sleep(0.3)
            response = self._instrument.readline().decode('ascii')
        except:
            response = None
            self._instrument_status = "error: reading serial connection"
        return response

    def _get_SP_speed(self):
        """Get the speed set point.

        Return (float): current speed SP
        """
        command = "IN_SP_4"
        response = self._write_read_serial_command(command)
        speed = float(response.split(" ")[0])
        return speed

    def _get_PV_speed(self):
        """Get the speed present value.

        Return (float): current speed present value
        """
        command = "IN_PV_4"
        response = self._write_read_serial_command(command)
        speed = float(response.split(" ")[0])
        return speed

    def set_SP_speed(self, value=0):
        """Set the speed set point to value.

        value (float): value of set point.
        """
        command = "OUT_SP_4 {:.2f} \r \n".format(value)
        try:
            response = self._instrument.write(command.encode('ascii'))
        except:
            self._instrument_status = "error: could not write new speed set point"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IKA Eursostart socket server")
    parser.add_argument(
        "--socket_ip",
        help="host address for the socket to bind",
        type=str,
        default="0.0.0.0"
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
    instrument = Ika(args.instrument_port, args.socket_ip,
        args.socket_port, args.host)
    instrument.run()
