#!/usr/bin/env python
# -*- coding: utf-8 -*-

import propar
from instruments.serial_instrument import SerialInstrument

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
    def __init__(self, port="/dev/ttyUSB0"):
        super().__init__(port=port)

    def _connect(self, port):
        """Connect to the instrument serial port.
        https://pypi.org/project/bronkhorst-propar/

        Arguments
        port (str): Filename of device (e.g. "/dev/ttyUSB0")
        """
        try:
            connection = propar.instrument(port)
        except:
            logger.info("Could not connect to instrument on port {}".format(port))
        else:
            logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the Bronkhorst flow rate present value.
        https://pypi.org/project/bronkhorst-propar/
        """
        for attribute in ["flow_rate"]:
            self._data[attribute] = self._instrument.measure
