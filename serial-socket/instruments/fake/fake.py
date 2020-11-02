#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import argparse
import random
from instrument import SerialInstrument
from pdb import set_trace

"""
Contains the Fake instrument class that is a subclass of the
generic instrument object.
"""


class Fake(SerialInstrument):
    """Class to communicate with a fake serial connection. 
       This class over-rides the following base clase methods:
           _connect_instrument
           _update_data
    """

    def __init__(self, instrument_port, socket_ip, socket_port):
        super().__init__(instrument_port, socket_ip, socket_port)

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
        except Exception as e:
            self._logger.error(
                "Could not connect to instrument on port {}".format(port)
            )
            self._logger.error(
                "{}".format(e.message)
            )
            raise e
        else:
            self._logger.info("Connected to instrument on port {}".format(port))
        return connection

    def _update_data(self):
        """Update the values of the fake instrument.
        
        Returns dictionary of data
        """
        data = {}
        for attribute in ["PV_1", "PV_2", "PV_3", "SP_1", "SP_2"]:
            data[attribute] = random.random()
        return data

    def _start(self):
        """Start the fake instrument.
        """
        response = {"status": "ok", "description": "successful start"}
        return response

    def _stop(self):
        """Stop the fake instrument.
        """
        response = {"status": "ok", "description": "successful stop"}
        return response


def test():
    instrument = Instrument("/dev/ttyUSB0", "127.0.0.1", 5007)
    request = {"user": "unique_user", "password": "123"}

    print("test login")
    request["command"] = {"command_name": "login"}
    print(instrument.process_request(request))

    print("test get_data")
    request["command"] = {"command_name": "get_data"}
    print(instrument.process_request(request))

    print("test start")
    request["command"] = {"command_name": "get_data"}
    print(instrument.process_request(request))

    print("test sending invalid command")
    request["command"] = {"command_name": "invalid command"}
    print(instrument.process_request(request))

    print("testing with wrong credentials")
    print(instrument.process_request({
        "user": "nobody",
        "password": "wrong",
        "command": {"command_name": "get_data"}
    }))

    print("test logout")
    request["command"] = {"command_name": "logout"}
    print(instrument.process_request(request))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="instrument server")
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
        default="fake/port"
    )
    args = parser.parse_args()
    instrument_server = Fake(args.instrument_port, args.socket_ip, args.socket_port)
    instrument_server.run()
