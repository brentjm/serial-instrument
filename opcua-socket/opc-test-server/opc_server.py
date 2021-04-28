#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simulates a fake serial instrument for testing the software stack.
"""
import argparse
import logging
import logging.config
import yaml
import coloredlogs
from time import sleep
from opcua import Server, ua
from opc_tags import tags_dict

__author__ = 'Giuseppe Cogoni'
__author__ = 'Brent Maranzano'
__license__ = 'MIT'


class OPCServer(object):
    """Mock Waters' Patrol socket API interface.
    """

    def __init__(self):
        """Start the logger and OPC UA server
        """
        self._setup_logger()
        self._tagGroup = 'DeltaV'
        self._configString = 'Test_config'
        self._sampleInterval = 10

    def _setup_logger(self, config_file='./logger_conf.yml'):
        """Start the logger using the provided configuration file.

        Arguments:
        config_file (yml file): configuration file for logger
        """
        try:
            with open(config_file, 'rt') as file_obj:
                config = yaml.safe_load(file_obj.read())
                logging.config.dictConfig(config)
                coloredlogs.install(level='INFO')
        except Exception as e:
            print(e)
        self._logger = logging.getLogger('opc_server')
        self._logger.debug('OPC UA server logger setup.')

    def run(self, endpoint=None):
        """Create a very simple OPC UA server.

        Arguments:
        endpoint (str): endpoint for OPC server
        """
        server = Server()
        server.set_endpoint(endpoint)

        uri = 'http://mock.deltav.server'
        idx = server.register_namespace(uri)

        objects = server.get_objects_node()

        myobj = objects.add_object(idx, '{}'.format(self._tagGroup))

        tags = {}

        for tag_name, info in tags_dict.items():

            tags[tag_name] = myobj.add_variable(idx, tag_name, info['tag_init'], 
                                                datatype=info['tag_type'])
            if info['tag_writable']:
                tags[tag_name].set_writable()
            else:
                tags[tag_name].set_read_only()

        server.start()

        count, sample_count, sample_cnt_int = 0, 0, 0
        try:
            while True:
                self._logger.info('\nCount #: {}'.format(count))
                if count == 10:
                    self._logger.info('LC configuration sent')
                    tags['CONFIG_NAME_DLV'].set_value(self._configString)
                StringEcho = tags['CONFIG_NAME_PAT'].get_value()
                self._logger.info('Config from service: '+str(StringEcho))
                if StringEcho == self._configString:
                    sample_cnt_int += 1
                    LC_status = tags['INT1_PAT'].get_value() 
                    self._logger.info('LC_status: {}'.format(LC_status))
                    self._logger.info('Sample counter: {}'.format(sample_cnt_int))
                    if (int(LC_status) == 1) and (sample_cnt_int >= self._sampleInterval):
                        sample_count += 1
                        sample_cnt_int = 0
                        sample_name = 'Sample_'+str(sample_count)
                        self._logger.info('Sample ID: {}'.format(sample_name))
                        tags['STRING1_DLV'].set_value(sample_name)
                sample_results = tags['FLOAT1_PAT'].get_value()
                if sample_results > 0:
                    sample_name_PAT = tags['STRING1_PAT'].get_value()
                    self._logger.info('LC_results for {}: {}'.format(sample_name_PAT, sample_results))

                count += 1
                sleep(1)
        finally:
            server.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='mock Delta V OPC UA server')
    parser.add_argument(
        '--endpoint',
        help='endpoint for the OPC UA server',
        type=str,
        default='opc.tcp://0.0.0.0:4840/deltavopcua/server/'
    )
    args = parser.parse_args()
    opcua = OPCServer()
    opcua.run(endpoint=args.endpoint)
