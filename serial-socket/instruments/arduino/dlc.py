#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads data from an Arduino connected to a
dynamic load cell (dlc).
"""
import logging
import argparse
from numpy import var
from scipy.stats import skew, kurtosis
from serial import Serial
from instrument import SerialInstrument


__author__ = "Brent Maranzano"
__license__ = "MIT"

logger = logging.getLogger(__name__)


class Dlc(SerialInstrument):
    """Class to communicate with the Arduino and process data
       from the attached dynamic load cell.
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
        super(Dlc, self).__init__(instrument_port, socket_ip, socket_port, host)
        # Set information about the attached device.
        self._device_information = {
            "instrument": "Arduino - DLC",
            "description": "Arduino with dyamic load cell.",
            "parameters": "PV",
            "instrument commands": None
        }
        self._data = {
            "PV": [],
            "VAR": 0.0
        }

    def _connect_instrument(self, port):
        """Connect to the IKA using RS232

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyACM0")
        """
        try:
            connection = Serial(port=port, baudrate=115200, timeout=None)
        except:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
            self._instrument_status = "error: could not connect to instrument"
            raise
        else:
            self._logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the data from the dynamic load cell.

        Returns dictionary of data
        """
        voltage = self._get_PV()
        self._calculate_statistics(voltage)
        return self._data

    def _get_PV(self, number_pts=800):
        """Get the present value array from the DLC

        Arguments
        number_pts (int): Number of points to expected in the buffer.
            Note that the number must coincide with the
            Arduino output or the byte order may not be correct.

        Return (array): last full buffer read of the load cell data.
        """
        data = [int(self._instrument.read(2).hex(), 16)
                for i in range(number_pts)]
        return data

    def _calculate_statistics(self, data):
        """Caclulate the statistics of the time series pressure fluctuations.
        Function directly modifies the class variable self._data.

        Arguments
        data (list): Time series data of pressure points.
        """
        self._data["VAR"] = var(data)
        self._data["SKEW"] = skew(data)
        self._data["KURTOSIS"] = kurtosis(data)


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
        default="/dev/ttyACM0"
    )
    parser.add_argument(
        "--host",
        help="host name",
        type=str,
        default="ape-53"
    )
    args = parser.parse_args()
    instrument = Dlc(args.instrument_port, args.socket_ip,
        args.socket_port, args.host)
    instrument.run()
