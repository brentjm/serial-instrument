#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to convert between from MQTT to socket and conversely.
"""
import socket
import argparse
import logging
import logging.config
import json
import yaml
import coloredlogs
import paho.mqtt.client as mqtt
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


class SocketMqtt(object):
    """Receives messages via MQTT (e.g. a JSON object that contains an
    instrument command) and redirects to a local socket (that may subsequently
    send to an instrument serial port to set/change a instrument parameter).
    Also, reads from a socket (such as instrument data) and tramsmitts via
    MQTT.
    """

    def __init__(self, socket_host="", socket_port=5007,
                 mqtt_broker="10.131.72.83", device_name="ape#"):
        """Start the logger, connect to a socket and mqtt broker. Start
        polling the socket for data and publishing on to MQTT.

        Arguments:
        socket_host (str): Name of the socket host. This is the service
            name if started with docker-compose.
        socket_port (int): Port number of the socket used to
            interact with instrument.
        mqtt_broker (str): Namre or address of the MQTT broker.
        """
        self._setup_logger()
        self._sock = self._connect_socket(socket_host, socket_port)
        self._mqttc = self._connect_mqtt(mqtt_broker, device_name)
        self._logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
        """Start the logger using the provided configuration file.
        """
        try:
            with open(config_file, 'rt') as file_obj:
                config = yaml.safe_load(file_obj.read())
                logging.config.dictConfig(config)
                coloredlogs.install(level='DEBUG')
        except Exception as e:
            print(e)
        self._logger = logging.getLogger("instrument_logger")
        self._logger.debug("instrument_server logger setup")

    def _connect_socket(self, host, port):
        """Connect to socket.

        Arguments:
        host (string): hostname or IP address of host.
        port (int): Socket server port number.

        Returns a socket connection.
        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        sock.setblocking(False)
        self._logger.info("Socket server listening on")
        return sock

    def _connect_mqtt(self, mqtt_broker, device_name):
        """Connect to the MQTT broker.

        Arguments
        mqtt_broker (str): Server name or IP address of MQTT broker.
        device_name (str): The name of the device (e.g. ape-5)
        """
        mqttc = mqtt.Client()
        mqttc.on_connect = self._create_on_connect()
        mqttc.on_message = self._create_on_message()
        mqttc.connect(mqtt_broker, 1883, 60)
        self._logger.info("Connected to MQTT broker: {}".format(mqtt_broker))
        return mqttc

    def _create_on_connect(self):
        """Create a function for the MQTT on_connect callback.

        Return function
        """
        def on_connect(client, userdata, flags, rc):
            pass
        return on_connect
    
    def _create_on_message(self):
        """Create a function for the MQTT on_message callback.

        Return function
        """
        def on_message(client, userdata, message):
            self._sock.sendall(message)
        return on_message

    def run(self):
        """Run the socket server. Accept clients and service requests.
        """
        mqttc.loop_start()
        # TODO get data from sensor and publish
        self._update_thread.start()
        self._execute_thread.start()
        self._logger.info("Instrument service run started.")
        while True:
            events = sel.select()
            for key, mask in events:
                callback = key.data
                callback(key.fileobj, mask)


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
        default="/dev/ttyUSB0"
    )
    args = parser.parse_args()
    instrument_server = SerialInstrument(args.instrument_port, args.socket_ip, args.socket_port)
    instrument_server.run()
