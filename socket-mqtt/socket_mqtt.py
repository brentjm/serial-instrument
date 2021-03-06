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
from time import sleep

__author__ = "Brent Maranzano"
__license__ = "MIT"


class SocketMqtt(object):
    """Receives messages via MQTT (e.g. a JSON object that contains an
    instrument command) and redirects to a local socket (that may subsequently
    send to an instrument serial port to set/change a instrument parameter).
    Also, reads from a socket (such as instrument data) and tramsmitts via
    MQTT.
    """

    def __init__(self, socket_host="", socket_port=54132,
                 mqtt_broker="", group_id="proto", device_id="default"):
        """Start the logger, connect to a socket and mqtt broker. Start
        polling the socket for data and publishing on to MQTT.

        Arguments:
        socket_host (str): Name of the socket host. This is the service
            name if started with docker-compose.
        socket_port (int): Port number of the socket used to
            interact with instrument.
        mqtt_broker (str): Namre or address of the MQTT broker.
        group_id (str): MQTT Sparkplug group id.
        device_id (str): MQTT Sparkplug device id.
        """
        self._group_id = group_id
        self._device_id = device_id
        self._device_data = None
        self._setup_logger()
        self._sock = self._connect_socket(socket_host, socket_port)
        client_id = group_id + device_id
        self._mqttc = self._setup_mqtt(mqtt_broker, client_id)
        self._logger.info("Instrument initiated")

    def _setup_logger(self, config_file="./logger_conf.yml"):
        """Start the logger using the provided configuration file.
        """
        try:
            with open(config_file, 'rt') as file_obj:
                config = yaml.safe_load(file_obj.read())
                logging.config.dictConfig(config)
                coloredlogs.install()
        except Exception as e:
            print(e)
        self._logger = logging.getLogger("socket_mqtt_logger")
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

    def _setup_mqtt(self, mqtt_broker, client_id):
        """Connect to the MQTT broker and subscribe to the
        device_id command topic.

        Arguments
        mqtt_broker (str): Server name or IP address of MQTT broker.
        client_id (str): MQTT client id (e.g. ape-5)

        Return the mqtt instance
        """
        self._logger.debug("attempting to connect to MQTT: {}".format(mqtt_broker))
        try:
            mqttc = mqtt.Client(client_id=client_id)
            mqttc.on_connect = self._create_mqtt_on_connect()
            mqttc.on_message = self._create_mqtt_on_message()
            mqttc.connect(mqtt_broker, 1883, 10)
        except Exception as err:
            self._logger.error("Could not connect to MQTT broker")
            raise err
        else:
            self._logger.info("Connected to MQTT broker: {}".format(mqtt_broker))
            about = self._get_device_about()
            host = about["host"]
            subscribe_topic = "+/+/DCMD/{}/+".format(host)
            mqttc.subscribe(subscribe_topic)
            self._logger.debug("set subscribe topic: {}".format(subscribe_topic))
        return mqttc

    def _create_mqtt_on_connect(self):
        """Create a function for the MQTT on_connect callback.
        Uses both self._group_id and self._device_id to create topic.

        Return function
        """
        def on_connect(client, userdata, flags, rc):
            about = self._get_device_about()
            host = about["host"]
            topic = "spBv1.0/{}/NBIRTH/{}/{}".format(self._group_id, host, self._device_id)
            self._mqttc.publish(topic, payload=json.dumps(about), qos=1, retain=True)
            self._logger.debug("on_connect callback publish about")
        return on_connect

    def _create_mqtt_on_message(self):
        """Create a function for the MQTT on_message callback. The on_message callback
        sends the message to the instrument socket.

        Return function
        """
        def on_message(client, userdata, message):
            payload = json.loads(message.payload.decode('ascii'))
            self._logger.debug("received message:\n{}".format(payload))
            status = self._send_socket_message(payload)
        return on_message

    def _send_socket_message(self, message):
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
                try:
                    received = json.loads(received.decode('ascii'))
                    self._logger.debug("received message from socket:\n{}".format(received))
                except Exception as err:
                    self._logger.error("error decoding response: {}".format(
                        received.decode('ascii')))
        return received

    def _get_device_data(self):
        """Get the instrument data.

        Returns JSON of device data
        """
        message = {
            "user": None,
            "password": None,
            "command": {
                "command_name": "get_data",
                "parameters": None
            }
        }
        data = self._send_socket_message(message)
        self._logger.debug("retrived device data: {}".format(data))
        return data

    def _get_device_about(self):
        """Get the device "about".

        Returns JSON "about" instrument parameters
        """
        message = {
                "user": None,
                "password": None,
                "command": {
                    "command_name": "get_about",
                    "parameters": None
                }
        }
        about = self._send_socket_message(message)
        self._logger.debug("retrived device about: {}".format(about))
        return about

    def run(self):
        """Start the MQTT service loop; send the instrument startup information,
        then start infinite loop sending instrument data.
        """
        self._logger.info("Starting MQTT Loop")
        self._mqttc.loop_start()
        # Create the publish topic outside loop
        about = self._get_device_about()
        host = about["host"]
        topic = "spBv1.0/{}/NDATA/{}/{}".format(self._group_id, host,
            self._device_id)
        # Wait to finsish request about device
        sleep(2)
        while True:
            # get instrument data
            data = self._get_device_data()
            self._logger.debug("publishing:\n topic: {}\n data: {}"
                .format(topic, data))
            self._mqttc.publish(topic, payload=json.dumps(data), qos=0,
                retain=False)
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
        "--group_id",
        help="MQTT Sparkplug group ID",
        type=str,
        default="prototype"
    )
    parser.add_argument(
        "--device_id",
        help="MQTT Sparkplug device ID",
        type=str,
        default="fake"
    )
    args = parser.parse_args()
    socket_mqtt = SocketMqtt(args.socket_host, args.socket_port,
                             args.mqtt_broker, args.group_id, args.device_id)
    socket_mqtt.run()
