#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module to convert between from MQTT to socket and conversely.
"""
import os
import socket
import argparse
import logging
import logging.config
import json
import yaml
import coloredlogs
import paho.mqtt.client as mqtt
from time import sleep
from pdb import set_trace

__author__ = "Brent Maranzano"
__license__ = "MIT"


def get_environment_variables():
    """Retrieve the environmental variables for server and
    broker settings.

    Returns JSON object of environment variables and values
    """
    return {
        "socket_host": os.getenv("SOCKET_HOST"),
        "socket_port": int(os.getenv("SOCKET_PORT")),
        "mqtt_broker": os.getenv("MQTT_BROKER"),
        "client_id": os.getenv("CLIENT_ID")
    }


class SocketMqtt(object):
    """Receives messages via MQTT (e.g. a JSON object that contains an
    instrument command) and redirects to a local socket (that may subsequently
    send to an instrument serial port to set/change a instrument parameter).
    Also, reads from a socket (such as instrument data) and tramsmitts via
    MQTT.
    """

    def __init__(self, socket_host="", socket_port=54132,
                 mqtt_broker="", client_id="ape#"):
        """Start the logger, connect to a socket and mqtt broker. Start
        polling the socket for data and publishing on to MQTT.

        Arguments:
        socket_host (str): Name of the socket host. This is the service
            name if started with docker-compose.
        socket_port (int): Port number of the socket used to
            interact with instrument.
        mqtt_broker (str): Namre or address of the MQTT broker.
        client_id (str): MQTT client id.
        """
        self._setup_logger()
        self._client_id = client_id
        self._sock = self._connect_socket(socket_host, socket_port)
        self._mqttc = self._connect_mqtt(mqtt_broker, client_id)
        self._logger.info("Instrument initiated")

    def _setup_logger(self):
        """Start the logger.
        """
        self._logger = logging.getLogger("socket_mqtt_logger")
        self._logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        self._logger.addHandler(handler)
        self._logger.info("socket-mqtt logger setup")

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

    def _connect_mqtt(self, mqtt_broker, client_id):
        """Connect to the MQTT broker.

        Arguments
        mqtt_broker (str): Server name or IP address of MQTT broker.
        client_id (str): MQTT client id (e.g. ape-5)
        """
        self._logger.debug("attempting to connect to MQTT: {}".format(mqtt_broker))
        try:
            mqttc = mqtt.Client(client_id=client_id)
            mqttc.on_connect = self._create_on_connect()
            mqttc.on_message = self._create_on_message()
            mqttc.connect(mqtt_broker, 1883, 10)
        except Exception as err:
            self._logger.error("Could not connect to MQTT broker")
            raise err
        else:
            self._logger.info("Connected to MQTT broker: {}".format(mqtt_broker))
        return mqttc

    def _create_on_connect(self):
        """Create a function for the MQTT on_connect callback.

        Return function
        """
        def on_connect(client, userdata, flags, rc):
            message = {
                    "user": None,
                    "password": None,
                    "command": {
                        "command_name": "get_about",
                        "parameters": None
                    }
            }
            about = self._send_message(message)
            self._logger.debug("on_connect callback publish about")
            self._mqttc.publish("{}/about".format(self._client_id),
                payload=json.dumps(about), qos=0, retain=True)
        return on_connect

    def _create_on_message(self):
        """Create a function for the MQTT on_message callback. The on_message callback
        sends the message to the instrument socket.

        Return function
        """
        def on_message(client, userdata, message):
            payload = json.loads(message.payload.decode('ascii'))
            self._logger.debug("received message:\n{}".format(payload))
            status = self._send_message(payload)
        return on_message

    def _send_message(self, message):
        """Send a message to the host socket.

        Arguments:
        message (JSON): Message to be sent to socket

        Returns (JSON) The response from the socket.
        """
        received = {"status": "failed"}
        self._logger.debug("sending message to socket:\n{}".format(message))
        message = json.dumps(message).encode('ascii')
        try:
            self._sock.sendall(message)
        except Exception as err:
            self._logger.error("error sending message to socket:\n{}".format(err))
        else:
            try:
                received = self._sock.recv(4096)
            except Exception as err:
                self._logger.error("error receiving message from socket:\n{}".format(err))
            else:
                received = json.loads(received.decode('ascii'))
                self._logger.debug("received message from socket:\n{}".format(received))
        return received

    def run(self):
        """Start the MQTT service loop; send the instrument startup information,
        then start infinite loop sending instrument data.
        """
        subscribe_topic = "{}/command".format(self._client_id)
        self._mqttc.subscribe(subscribe_topic)
        self._logger.debug("set subscribe topic: {}".format(subscribe_topic))
        publish_topic = "{}/data".format(self._client_id)
        self._logger.debug("set publish topic: {}".format(publish_topic))
        self._logger.info("Starting MQTT Loop")
        self._mqttc.loop_start()
        message = {
            "user": None,
            "password": None,
            "command": {
                "command_name": "get_data",
                "parameters": None
            }
        }
        while True:
            # get data
            data = self._send_message(message)
            self._logger.debug("publish\n{}".format(data))
            self._mqttc.publish(publish_topic, payload=json.dumps(data))
            sleep(5)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="socket to mqtt exchange")
    parser.add_argument(
        "--socket_host",
        help="host name or IP address for the instrument socket",
        type=str,
        default=None
    )
    parser.add_argument(
        "--socket_port",
        help="port number for the socket server",
        type=int,
        default=54132
    )
    parser.add_argument(
        "--mqtt_broker",
        help="host name or IP address of MQTT broker",
        type=str,
        default="192.168.1.3"
    )
    parser.add_argument(
        "--client_id",
        help="MQTT client ID",
        type=str,
        default="ape-0"
    )
    args = parser.parse_args()
    if args.socket_host is not None:
        socket_mqtt = SocketMqtt(args.socket_host, args.socket_port,
            args.mqtt_broker, args.client_id)
    else:
        env = get_environment_variables()
        socket_mqtt = SocketMqtt(env["socket_host"], env["socket_port"],
            env["mqtt_broker"], env["client_id"])
    socket_mqtt.run()
