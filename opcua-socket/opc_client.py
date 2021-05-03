#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Service to interchange information between Delta V OPC UA server and Waters'
Empower socket API
"""
import argparse
import logging
import logging.config
import yaml
import coloredlogs
import threading
from time import sleep
from opcua import Client, ua
from opc_tags import tags_dict
from numpy import random

__author__ = 'Giuseppe Cogoni'
__author__ = 'Brent Maranzano'
__license__ = 'MIT'


class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another
    thread if you need to do such a thing
    """
    def __init__(self, tags, lock, sock):
        self._logger = logging.getLogger(__name__+'SubHandler')
        self._logger.info('SubHandler initialized.')

        self.tags = tags
        self.lock = lock
        self.sock = sock

        self._tag_config = 'CONFIG_NAME_DLV'
        self._tag_sampleName = 'STRING1_DLV'


    def _compareTags(self, tag, node):
        return str(self.tags[tag]) in str(node)


    def _logicBlock_1(self, node, val):
        if self._compareTags(self._tag_config, node) and len(val)>0:
            self.tags['CONFIG_NAME_PAT'].set_value(val)
            self._logger.info('Configuration echoed to OPC server: {}'.format(val))
            LC_status = 1
            self.tags['INT1_PAT'].set_value(LC_status)
            self._logger.info('LC status set to: {}'.format(LC_status))


    def _logicBlock_2(self, node, val):
        if self._compareTags(self._tag_sampleName, node) and len(val)>0:
            LC_status = 2
            self.tags['INT1_PAT'].set_value(LC_status)
            self._logger.info('LC status set to: {}'.format(LC_status))
            rand_val = random.rand(1)[0]
            data = self.sock.run_command(command=str(rand_val))
            sleep(3)
            LC_status = 1
            self.tags['FLOAT1_PAT'].set_value(float(data))
            self.tags['STRING1_PAT'].set_value(val)
            self._logger.info('LC results for {} transmitted: {}'.format(val, data))
            self.tags['INT1_PAT'].set_value(LC_status)
            self._logger.info('LC status set to: {}'.format(LC_status))


    def datachange_notification(self, node, val, data):
        self._logger.debug('OPC-server data change detected with: {}, {}, {}'.format(node, val, data))
        def do_stuff(val, node, lock):
            with lock:
                self._logicBlock_1(node, val)
                self._logicBlock_2(node, val)

        threading.Thread(target=do_stuff, args=[val, node, self.lock], daemon=True).start()


class OPCClient(threading.Thread):
    """Client for DeltaV.
    """

    def __init__(self, socket_host, socket_port, endpoint):
        """Start the initial configuration for OPC client/socket service
        """
        super().__init__()
        self.setDaemon(True)
        self.lock = threading.Lock()

        self._logger = logging.getLogger(__name__+'OPC-client')
        self._logger.info('OPC client initialized.')

        self._tagGroup = 'DeltaV'
        self._uri = 'http://mock.deltav.server'

        self.sock = self._createSocket(socket_host, socket_port)
        self.client = self._connectOPCClient(endpoint)
        self.tags = self._getOPCTags()


    def _connectOPCClient(self, endpoint):
        opc_connected = False
        client = Client(endpoint)
        while not opc_connected:
            try:
                client.connect()
                self._logger.info('OPC client connected to: {}'.format(endpoint))
                opc_connected = True
            except:
                self._logger.info('Error connecting OPC client, retrying in 5 seconds...')
                sleep(5)
                continue
        return client


    def _createSocket(self, host, port):
        self._logger.info('Socket connection created.')
        return OpcSocket(host, port)


    def _getOPCTags(self):

        root = self.client.get_root_node()
        objects = self.client.get_objects_node()

        idx = self.client.get_namespace_index(self._uri)
        tags = {}

        for tag_name, info in tags_dict.items():

            tags[tag_name] = root.get_child(['0:Objects','{}:{}'.format(idx, self._tagGroup),
                                             '{}:{}'.format(idx,tag_name)])

        self._logger.info('OPC tags retrieved: {}'.format(tags))
        return tags


    def run(self):
        """Create OPC UA client.

        Arguments:
        endpoint (str): endpoint for OPC client
        """

        handler = SubHandler(self.tags, self.lock, self.sock)

        sub = self.client.create_subscription(500, handler)
        handle = sub.subscribe_data_change([self.tags['CONFIG_NAME_DLV'],self.tags['STRING1_DLV']])


def setup_logger(config_file='./logger_conf.yml'):
        """Start the logger using the provided configuration file.
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

