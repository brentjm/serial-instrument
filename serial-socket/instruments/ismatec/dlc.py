#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Reads data from an Arduino connected to a
dynamic load cell (dlc).
"""
import logging
import argparse
from serial import Serial
from instrument import SerialInstrument


__author__ = "Brent Maranzano"
__license__ = "MIT"

logger = logging.getLogger(__name__)


class Ismatec(SerialInstrument):
    """Class to communicate with a Cole-Parmer Ismatec pump
       http://www.ismatec.com/images/pdf/manuals/Reglo_Digital_new.pdf
       This class over-rides the following base clase methods:
           __init__
           _connect_instrument
           _update_data
           _set_about
    """

    def __init__(self, instrument_port, socket_ip, socket_port, host):
        super(Ismatec, self).__init__(instrument_port, socket_ip, socket_port,
                                      host)
        # Set information about the attached device.
        # TODO add additional commands
        self._device_information = {
            "instrument": "Ismatec pump",
            "description": "Ismatec pump",
            "parameters": "SP, PV",
            "instrument commands": "start, stop, set_mode, set_SP"
        }
        self._data = {
            "SP": 0.0,
            "PV": 0.0
        }

    def _connect_instrument(self, port):
        """Connect to the Ismatec using RS232
        http://www.ismatec.com/images/pdf/manuals/Reglo_Digital_new.pdf (p 33)

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = Serial(port=port, baudrate=9600, bytesize=8,
                                parity="N", stopbits=1, timeout=None)
        except:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
            self._instrument_status = "error: could not connect to instrument"
            raise
        else:
            self._logger.info("Connected to instrument on port {}"
                              .format(port))
        return connection

    def _update_data(self):
        """Update the data from the the pump.

        Returns dictionary of data
        """
        mode = self._get_mode()
        self._data["MODE"] = mode
        if mode is "N":
            self._data["SPEED"] = self._get_speed()
        elif mode is "M":
            self._data["FLOWRATE"] = self._get_flowrate()
        elif mode is "N":
            self._data["TIME"] = self._get_time()
        elif mode is "O":
            self._data["VOLUME"] = self._get_volume()
        return self._data

    def _start(self):
        """Start the pump
        """
        self._instrument.write("1H{}".format(chr(13)).encode('ascii'))

    def _stop(self):
        """Stop the pump
        """
        self._instrument.write("1I{}".format(chr(13)).encode('ascii'))

    def _set_mode(self, mode):
        """Set the mode of the pump:

        Arguments
        mode (str)
            L - RPM
            M - flow rate
            N - Time
            O - Volume
        """
        self._instrument.write("1{}{}".format(mode, chr(13)).encode('ascii'))

    def _set_speed(self, speed):
        """Set the speed of the pump.

        Arguments
        speed (float): Set the pump speed in RPM
        """
        self._instrument.write("1S{}{}".format(speed, chr(13)).zfill(6).encode('ascii'))

    def _set_flowrate(self, flowrate):
        """Set the flowrate of the pump.

        Arguments
        flowrate (float): Set the pump flow rate (ml/min)
        """
        self._instrument.write("1!{}{}".format(flowrate, chr(13)).zfill(6).encode('ascii'))

    def _set_dispense_time(self, disp_time):
        """Set the dispensing time of the pump.

        Arguments
        disp_time (float): Set the pump dispensing time (seconds)
        """
        self._instrument.write("1V{}{}".format(disp_time, chr(13)).zfill(6).encode('ascii'))

    def _get_mode(self):
        """Get the pump mode.

        Return (float): Pump mode
            mode (str)
                L - RPM
                M - flow rate
                N - Time
                O - Volume
        """
        data = self._instrument.write("1E{}".format(chr(13)).encode('ascii'))
        return data

    def _get_speed(self):
        """Get the speed of the pump.

        Return (float): Speed of pump in RPM.
        """
        data = self._instrument.write("1S{}".format(chr(13)).encode('ascii'))
        return data

    def _get_flowrate(self):
        """Get the flowrate of the pump.

        Return (float): Flow rate of pump in ml/min.
        """
        data = self._instrument.write("1!{}".format(chr(13)).encode('ascii'))
        return data

    def _get_time(self):
        """Get the dispensing time of the pump.

        Return (float): Dispensing time (1/10 seconds)
        """
        data = self._instrument.write("1V{}".format(chr(13)).encode('ascii'))
        return data

    def _get_volume(self):
        """Get the dispensing volume of the pump.

        Return (float): Dispensing volume (ml)
        """
        data = self._instrument.write("1v{}".format(chr(13)).encode('ascii'))
        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            description="IKA Eursostart socket server")
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
    instrument = Ismatec(args.instrument_port, args.socket_ip,
                         args.socket_port, args.host)
    instrument.run()
