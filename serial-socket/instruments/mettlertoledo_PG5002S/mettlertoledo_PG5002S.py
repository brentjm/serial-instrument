#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from serial import Serial
from time import sleep
from instrument import SerialInstrument
logger = logging.getLogger(__name__)
from pdb import set_trace

"""
Contains the Metter Toledo class that is a subclass of the
generic instrument object."""


class MettlerToledo(SerialInstrument):
    """Class to communicate with Mettler Toledo PG5002-S
    balance. The Mettler Toledo balance should be connected to from USB 
    to D-Sub9 (not null).
    https://www.mt.com/dam/product_organizations/laboratory_weighing/WEIGHING_SOLUTIONS/PRODUCTS/MT-SICS/MANUALS/en/Excellence-SICS-BA-en-11780711D.pdf

    self._data = {"mass": float}

    Attributes:
    ser (pySerial object): serial connection to the Mettler Toledo balance
    """
    def __init__(self, instrument_port, socket_ip, socket_port):
        super().__init__(instrument_port, socket_ip, socket_port)

    def _connect_instrument(self, port="/dev/ttyUSB0"):
        """Connect to the instrument serial port. See class description
        for connectivity.

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")

	Return ser (pySerial object) serial connection to balance.
        """
        try:
            ser = Serial(port=port)
        except:
            logger.info(
                "Could not connect to instrument on port {}".format(port)
            )
        else:
            logger.info("Connected to instrument on port {}".format(port))
        return ser

    def _update_data(self):
        """Update the value of the current mass (see manual for commands).
        Note that self._instrument is the instrument connection returned from
        _connect_instrument and self._data is inherrited from base class that 
        contains a dictionary of data for the instrument.
        """
        data = {}
        for attribute in ["mass"]:
            self._instrument.write("SI\r\n".encode("utf-8"))
            sleep(0.8)          
            data[attribute] = self._instrument.readline()
            return data


if __name__ == "__main__":
    balance = MettlerToledo("/dev/ttyUSB0", "127.0.0.1", 54132)
    balance.run()
