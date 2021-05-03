#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Service to interchange information between Delta V OPC UA server and Waters'
Empower socket API
"""
import socket
import argparse
import logging
import logging.config
import yaml
import coloredlogs
from time import sleep
from numpy import random

__author__ = 'Giuseppe Cogoni'
__author__ = 'Brent Maranzano'
__license__ = 'MIT'


class SocketClient(object):
    """Generic socket client for protocol conversions.
    """

    def __init__(self, socket_host, socket_port):
        """Connect to the socket.

        Arguments
        socket_host (str): interface to bind socket (e.g. '0.0.0.0')
        socket_port (int): port number to use for socket
        """
        self._logger = logging.getLogger(__name__)
        self._sock = self._connect_socket(socket_host, socket_port)

    def setup_logger(self, config_file='./logger_conf.yml'):
            """Start the logger using the provided configuration file.

            Arguments
            config_file (yml file): logger configuration file.

            Returns logger
            """
            try:
                with open(config_file, 'rt') as file_obj:
                    config = yaml.safe_load(file_obj.read())
                    logging.config.dictConfig(config)
                    coloredlogs.install(level='DEBUG')
            except Exception as e:
                print(e)
            logger = logging.getLogger(__name__)
            logger.info('Logger started...')
            return logger

    def _connect_socket(self, host, port):
        """Connect to socket. Note that the socket is left
        as blocking and shouldn't be modified unless a selector
        is used.

        Arguments:
        host (string): hostname or IP address of host.
        port (int): Socket server port number.

        Returns a socket connection.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
        except socket.error as err:
            self._logger.error(
                    "Failed to connect to socket {}:{}".format(host, port))
            raise err
        else:
            self._logger.info(
                    "Connected to socket host: {}, port: {}".format(host, port))
        return sock


    def run_command(self, command=''):
        """run commands to socket server

        Arguments:
        command/message to be sent to socket server

        Return:
        data (string): Echoed command sent by client
        """

        self._logger.debug('Sending message to socket.')
        self._sock.sendall(command.encode())
        data = self._sock.recv(1024).decode(encoding='UTF-8')
        self._logger.debug('returned message from OPC: {}'.format(data))
        return data




if __name__ == '__main__':

    logger = setup_logger()
    logger.info('Main service started.')
    parser = argparse.ArgumentParser(description='mock Empower socket server and OPC UA server info')

    parser.add_argument(
        '--socket_ip',
        help='host address for the socket to bind',
        type=str,
        default='127.0.0.1'
    )

    parser.add_argument(
        '--socket_port',
        help='port number for the socket server',
        type=int,
        default=54756
    )

    parser.add_argument(
        '--endpoint',
        help='endpoint for the OPC UA server',
        type=str,
        default='opc.tcp://127.0.0.1:4840/deltavopcua/server/'
    )
    args = parser.parse_args()

    opcua = OPCClient(args.socket_ip, args.socket_port, args.endpoint).run()
    logger.debug('Service argument passed successfully!')

